// The map on the page: shapes and borders drawn by the graphics card, so a pan or zoom costs one frame, and city labels drawn on a
// canvas above it. Which labels show is decided once for each half step of zoom, best known city first, so panning never moves or
// swaps them and zooming in only adds more.
import { zoom as d3Zoom, zoomIdentity, type ZoomTransform } from 'd3-zoom';
import { select } from 'd3-selection';
import 'd3-transition';
import { lineKinds, shapeAt, type LineKind, type MapGeometry } from '../src/map-geometry.ts';
import { projection } from '../src/projection.ts';

export type MapLabel = {
  // amountColours: the amount's own colour where it carries a verdict, for a light label and for a dark one, else null for the
  // label's ink. amount may be empty, for the visitor's or compared place when it has no figure. colour: the dot's fill.
  code: string; x: number; y: number; name: string; amount: string; amountColours: { onLight: string; onDark: string } | null; colour: string;
  flag: HTMLCanvasElement | null;
  // fame: how well known the city is, 0 the most (src/places.ts); it decides the zoom at which its label may first show.
  fame: number; population: number;
};
export type MapCovers = { top: number; bottom: number; left: number; right: number; boxes: DOMRect[] };
type ScreenBox = [left: number, top: number, right: number, bottom: number];

// The colours around the places, as fractions: the sea, the lines between places, and the outline of an opened place.
export type MapTheme = { sea: [number, number, number]; line: [number, number, number]; ink: [number, number, number]; isDark: boolean };
// The zoom at which a label may first show, by fame: the best known from the whole world, the least known only up close.
const firstLevelOfFame = [0, 0, 4, 6];
const labelMargin = 9;
const deepestZoom = 10, labelStep = 0.5;
const labelHeight = 22, labelPadLeft = 4, labelPadRight = 7, labelGap = 5, flagWidth = 17, flagHeight = 12, dotRadius = 4, dotGap = 5;
const labelFont = (weight: number) => `${weight} 12px Archivo, system-ui, sans-serif`;

const projectShader = `
uniform vec2 scale; uniform vec2 translate; uniform vec2 viewport;
vec4 toClip(vec2 point) { vec2 pixel = point * scale + translate; return vec4(pixel.x / viewport.x * 2.0 - 1.0, 1.0 - pixel.y / viewport.y * 2.0, 0.0, 1.0); }`;
const fillVertex = `#version 300 es
in vec2 position; in float shape; flat out int shapeIndex;${projectShader}
void main() { shapeIndex = int(shape + 0.5); gl_Position = toClip(position); }`;
const fillFragment = `#version 300 es
precision mediump float; precision highp int;
flat in int shapeIndex; uniform sampler2D colours; out vec4 colour;
void main() { colour = texelFetch(colours, ivec2(shapeIndex % 1024, shapeIndex / 1024), 0); }`;
const lineVertex = `#version 300 es
in vec2 corner; in vec4 segment; uniform float halfWidth;${projectShader}
void main() {
  vec2 a = segment.xy * scale + translate, b = segment.zw * scale + translate, along = b - a;
  float length_ = max(length(along), 1e-6); along /= length_;
  vec2 across = vec2(-along.y, along.x), pixel = mix(a - along * halfWidth, b + along * halfWidth, corner.x) + across * corner.y * halfWidth;
  gl_Position = vec4(pixel.x / viewport.x * 2.0 - 1.0, 1.0 - pixel.y / viewport.y * 2.0, 0.0, 1.0);
}`;
const lineFragment = `#version 300 es
precision mediump float; uniform vec4 lineColour; out vec4 colour; void main() { colour = lineColour; }`;

function segmentsOf(lines: Float32Array[]): Float32Array {
  let count = 0;
  for (const line of lines) count += line.length / 2 - 1;
  const segments = new Float32Array(count * 4);
  let index = 0;
  for (const line of lines) for (let point = 2; point < line.length; point += 2) segments.set([line[point - 2], line[point - 1], line[point], line[point + 1]], (index++) * 4);
  return segments;
}

export function createMapView(container: HTMLElement, events: { placeAt(x: number, y: number, shape: number, labelCode: string | null): void; moved(): void; hovered(shape: number, labelCode: string | null, clientX: number, clientY: number): void }) {
  container.innerHTML = '<canvas class="map-shapes"></canvas><canvas class="map-labels" role="img" aria-label="Map"></canvas>';
  const shapeCanvas = container.querySelector<HTMLCanvasElement>('.map-shapes')!, labelCanvas = container.querySelector<HTMLCanvasElement>('.map-labels')!;
  const gl = shapeCanvas.getContext('webgl2', { antialias: true, alpha: false })!;
  if (!gl) throw new Error('This browser cannot draw the map (no WebGL2).');

  const compile = (vertexSource: string, fragmentSource: string) => {
    const program = gl.createProgram()!;
    for (const [type, source] of [[gl.VERTEX_SHADER, vertexSource], [gl.FRAGMENT_SHADER, fragmentSource]] as const) {
      const shader = gl.createShader(type)!;
      gl.shaderSource(shader, source); gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader) ?? 'shader');
      gl.attachShader(program, shader);
    }
    gl.linkProgram(program);
    const uniforms = new Proxy({} as Record<string, WebGLUniformLocation | null>, { get: (cache, name: string) => (cache[name] ??= gl.getUniformLocation(program, name)) });
    return { program, uniforms };
  };
  const fill = compile(fillVertex, fillFragment), line = compile(lineVertex, lineFragment);

  let theme: MapTheme = { sea: [0.914, 0.933, 0.953], line: [1, 1, 1], ink: [0.063, 0.082, 0.11], isDark: false };
  let geometry: MapGeometry | null = null;
  let fillVao: WebGLVertexArrayObject | null = null, fillIndexCount = 0;
  const lineVaos = new Map<string, { vao: WebGLVertexArrayObject; count: number }>();
  const colourTexture = gl.createTexture();
  let colourBytes: Uint8Array = new Uint8Array(0);

  function lineVao(segments: Float32Array) {
    const vao = gl.createVertexArray()!;
    gl.bindVertexArray(vao);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([0, -1, 1, -1, 1, 1, 0, -1, 1, 1, 0, 1]), gl.STATIC_DRAW);
    const corner = gl.getAttribLocation(line.program, 'corner');
    gl.enableVertexAttribArray(corner); gl.vertexAttribPointer(corner, 2, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, segments, gl.STATIC_DRAW);
    const segment = gl.getAttribLocation(line.program, 'segment');
    gl.enableVertexAttribArray(segment); gl.vertexAttribPointer(segment, 4, gl.FLOAT, false, 0, 0); gl.vertexAttribDivisor(segment, 1);
    gl.bindVertexArray(null);
    return { vao, count: segments.length / 4 };
  }

  function setGeometry(next: MapGeometry): void {
    if (next.projection !== projection.name) throw new Error(`The map file is in ${next.projection}, the page in ${projection.name}`);
    geometry = next;
    fillVao = gl.createVertexArray();
    gl.bindVertexArray(fillVao);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, next.points, gl.STATIC_DRAW);
    const position = gl.getAttribLocation(fill.program, 'position');
    gl.enableVertexAttribArray(position); gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, Float32Array.from(next.shapeOfPoint), gl.STATIC_DRAW);
    const shape = gl.getAttribLocation(fill.program, 'shape');
    gl.enableVertexAttribArray(shape); gl.vertexAttribPointer(shape, 1, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, next.triangleIndices, gl.STATIC_DRAW);
    fillIndexCount = next.triangleIndices.length;
    gl.bindVertexArray(null);
    for (const kind of lineKinds) lineVaos.set(kind, lineVao(segmentsOf(next.lines[kind])));
    setHighlightedShape(highlightedShape);
    draw();
  }

  // One colour per shape, as RGBA bytes, in the order of the geometry's shapes.
  function setShapeColours(bytes: Uint8Array): void {
    colourBytes = bytes;
    const rows = Math.ceil(bytes.length / 4 / 1024), padded = new Uint8Array(rows * 1024 * 4);
    padded.set(bytes);
    gl.bindTexture(gl.TEXTURE_2D, colourTexture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, 1024, rows, 0, gl.RGBA, gl.UNSIGNED_BYTE, padded);
    draw();
  }

  let highlightedShape = -1;
  function setHighlightedShape(shape: number): void {
    highlightedShape = shape;
    lineVaos.delete('highlight');
    if (geometry && shape >= 0) {
      const rings: Float32Array[] = [];
      for (let ring = geometry.shapeFirstRing[shape]; ring < geometry.shapeFirstRing[shape + 1]; ring++) {
        const start = geometry.ringStarts[ring], end = geometry.ringStarts[ring + 1];
        const points = new Float32Array((end - start + 1) * 2);
        points.set(geometry.points.subarray(start * 2, end * 2)); points.set(geometry.points.subarray(start * 2, start * 2 + 2), (end - start) * 2);
        rings.push(points);
      }
      lineVaos.set('highlight', lineVao(segmentsOf(rings)));
    }
    draw();
  }

  // ---- The view: a d3 zoom transform over the world fitted to the screen.
  let size = { width: 1, height: 1 }, covers: MapCovers = { top: 0, bottom: 0, left: 0, right: 0, boxes: [] };
  let baseScale = 1, baseTranslate: [number, number] = [0, 0], transform: ZoomTransform = zoomIdentity;
  const viewScale = () => baseScale * transform.k;
  const viewTranslate = (): [number, number] => [baseTranslate[0] * transform.k + transform.x, baseTranslate[1] * transform.k + transform.y];
  const toScreen = (x: number, y: number): [number, number] => { const [tx, ty] = viewTranslate(), scale = viewScale(); return [x * scale + tx, y * scale + ty]; };
  const toMap = (screenX: number, screenY: number): [number, number] => { const [tx, ty] = viewTranslate(), scale = viewScale(); return [(screenX - tx) / scale, (screenY - ty) / scale]; };
  // Zoom as on tiled web maps: 0 shows the world 256 pixels wide.
  const zoomLevel = () => Math.log2(viewScale() / 256);

  const zoomBehaviour = d3Zoom<HTMLCanvasElement, unknown>()
    .on('zoom', event => { transform = event.transform; draw(); if (event.sourceEvent) events.moved(); });
  const selection = select(labelCanvas).call(zoomBehaviour).on('dblclick.zoom', null);

  // The world fills the screen's width, running behind the cards, with the inhabited latitudes in the middle; the cards over the
  // map never move it, only the labels keep clear of them.
  const middleLatitude = 17;
  function fit(): void {
    const rect = container.getBoundingClientRect();
    size = { width: Math.max(1, Math.round(rect.width)), height: Math.max(1, Math.round(rect.height)) };
    baseScale = size.width;
    baseTranslate = [0, size.height / 2 - projection.project(0, middleLatitude)[1] * baseScale];
    const worldTop = projection.project(0, 84)[1] * baseScale + baseTranslate[1], worldBottom = projection.project(0, -60)[1] * baseScale + baseTranslate[1];
    zoomBehaviour.scaleExtent([1, 2 ** deepestZoom * 256 / baseScale]).extent([[0, 0], [size.width, size.height]])
      .translateExtent([[-size.width * 0.15, Math.min(0, worldTop)], [size.width * 1.15, Math.max(size.height, worldBottom)]]);
    const pixelRatio = devicePixelRatio || 1;
    for (const canvas of [shapeCanvas, labelCanvas]) {
      canvas.width = Math.round(size.width * pixelRatio); canvas.height = Math.round(size.height * pixelRatio);
    }
    draw();
  }

  // Move the view so a point sits in the middle of the uncovered map, at a zoom level, gliding there unless asked not to.
  function show(x: number, y: number, level: number, glide = true): void {
    const scale = 256 * 2 ** Math.max(level, Math.log2(baseScale / 256)), k = scale / baseScale;
    const middleX = covers.left + (size.width - covers.left - covers.right) / 2, middleY = covers.top + (size.height - covers.top - covers.bottom) / 2;
    const target = zoomIdentity.translate(middleX - (x * scale + baseTranslate[0] * k), middleY - (y * scale + baseTranslate[1] * k)).scale(k);
    if (glide && !matchMedia('(prefers-reduced-motion: reduce)').matches) selection.transition().duration(600).call(zoomBehaviour.transform, target);
    else selection.call(zoomBehaviour.transform, target);
  }
  // Show a box of the map (west, north, east, south in map units) as large as fits in the uncovered part.
  function showBox(west: number, north: number, east: number, south: number, glide = true): void {
    const width = Math.max(80, size.width - covers.left - covers.right - 120), height = Math.max(80, size.height - covers.top - covers.bottom - 80);
    const scale = Math.min(width / Math.max(east - west, 1e-6), height / Math.max(south - north, 1e-6));
    show((west + east) / 2, (north + south) / 2, Math.min(7, Math.log2(scale / 256)), glide);
  }
  // The whole world, its inhabited latitudes in the middle of the part the cards leave uncovered.
  function showWorld(glide = true): void {
    const target = zoomIdentity.translate(0, covers.top / 2 - covers.bottom / 2);
    if (glide) selection.transition().duration(600).call(zoomBehaviour.transform, target); else selection.call(zoomBehaviour.transform, target);
  }
  const zoomBy = (factor: number) => selection.transition().duration(250).call(zoomBehaviour.scaleBy, factor);

  // ---- Labels: placed once per half step of zoom.
  let labels: MapLabel[] = [], emphasis: { dark: string | null; ringed: string | null; named: string[] } = { dark: null, ringed: null, named: [] };
  const placementCache = new Map<number, Map<string, 'right' | 'left'>>();
  const measure = labelCanvas.getContext('2d')!;
  const widths = new Map<string, number>();
  function labelWidth(label: MapLabel): number {
    if (!widths.has(label.code)) {
      measure.font = labelFont(500); const nameWidth = measure.measureText(label.name).width;
      // Every amount is measured as the widest one, so placements do not change when the amounts do.
      measure.font = labelFont(700); const amountWidth = measure.measureText('−$88.8M').width;
      widths.set(label.code, labelPadLeft + flagWidth + labelGap + nameWidth + labelGap + amountWidth + labelPadRight);
    }
    return widths.get(label.code)!;
  }
  function boxAt(label: MapLabel, side: 'right' | 'left', centreX: number, centreY: number): ScreenBox {
    const width = labelWidth(label), left = side === 'right' ? centreX + dotRadius + dotGap : centreX - dotRadius - dotGap - width;
    return [left, centreY - labelHeight / 2, left + width, centreY + labelHeight / 2];
  }
  const overlaps = (a: ScreenBox, b: ScreenBox, margin: number) => a[0] - margin < b[2] && a[2] + margin > b[0] && a[1] - margin < b[3] && a[3] + margin > b[1];

  // Strict priority: each label, most important first, takes the lowest level at which it clears every more important label at
  // that level, and keeps its room at every closer level, so a lesser label never takes a greater one's place.
  function placementsAt(level: number): Map<string, 'right' | 'left'> {
    const cached = placementCache.get(level);
    if (cached) return cached;
    const levels: number[] = [];
    for (let candidate = 0; candidate <= deepestZoom; candidate += labelStep) levels.push(candidate);
    // Placed boxes, by level, in a grid of 256-pixel cells so each test looks only at near neighbours.
    const grids = levels.map(() => new Map<number, ScreenBox[]>()), found = levels.map(() => new Map<string, 'right' | 'left'>());
    const cellsOf = (box: ScreenBox) => {
      const cells: number[] = [];
      for (let column = Math.floor(box[0] / 256); column <= Math.floor(box[2] / 256); column++) for (let row = Math.floor(box[1] / 256); row <= Math.floor(box[3] / 256); row++) cells.push(column * 1e6 + row);
      return cells;
    };
    const isFree = (index: number, box: ScreenBox) => cellsOf(box).every(cell => !(grids[index].get(cell) ?? []).some(other => overlaps(other, box, labelMargin)));
    const sideFreeAt = (label: MapLabel, index: number) => {
      const scale = 256 * 2 ** levels[index];
      return (['right', 'left'] as const).find(candidate => isFree(index, boxAt(label, candidate, label.x * scale, label.y * scale)));
    };
    for (const label of labels) {
      for (let index = levels.indexOf(firstLevelOfFame[label.fame] ?? 5); index < levels.length; index++) {
        let side = sideFreeAt(label, index);
        if (!side) continue;
        // Shown from this level on, on whichever side is free at each closer level (the last side where neither is).
        for (let later = index; later < levels.length; later++) {
          side = sideFreeAt(label, later) ?? side;
          const laterScale = 256 * 2 ** levels[later], box = boxAt(label, side, label.x * laterScale, label.y * laterScale);
          for (const cell of cellsOf(box)) { if (!grids[later].has(cell)) grids[later].set(cell, []); grids[later].get(cell)!.push(box); }
          found[later].set(label.code, side);
        }
        break;
      }
    }
    levels.forEach((candidate, index) => placementCache.set(candidate, found[index]));
    return placementCache.get(level)!;
  }
  // Placements depend only on which cities are labelled and their names, so new amounts or colours keep them.
  let placedFor = '';
  function setLabels(next: MapLabel[]): void {
    labels = [...next].sort((a, b) => a.fame - b.fame || b.population - a.population);
    const key = labels.map(label => `${label.code}:${label.name}`).join('|');
    if (key !== placedFor) { placedFor = key; placementCache.clear(); widths.clear(); }
    draw();
  }

  let drawnLabels: { label: MapLabel; box: ScreenBox; dot: [number, number] }[] = [];
  // A label is placed with room for any amount, but drawn only as wide as what it says.
  function drawnWidth(context: CanvasRenderingContext2D, label: MapLabel): number {
    context.font = labelFont(500); const nameWidth = context.measureText(label.name).width;
    context.font = labelFont(700); const amountWidth = label.amount ? context.measureText(label.amount).width + labelGap : 0;
    return labelPadLeft + flagWidth + labelGap + nameWidth + amountWidth + labelPadRight;
  }
  function drawLabels(context: CanvasRenderingContext2D): void {
    const level = Math.max(0, Math.min(deepestZoom, Math.floor(zoomLevel() / labelStep) * labelStep));
    const placements = labels.length ? placementsAt(level) : new Map();
    const blocked: ScreenBox[] = covers.boxes.map(box => [box.left - 4, box.top - 4, box.right + 4, box.bottom + 4]);
    drawnLabels = [];
    const isInside = (box: ScreenBox) => box[0] >= 2 && box[1] >= 2 && box[2] <= size.width - 2 && box[3] <= size.height - 2;
    // The visitor's, the compared and the opened place's labels first, wherever they fit.
    const emphasised = [...new Set([emphasis.ringed, emphasis.dark, ...emphasis.named])].filter(Boolean).map(code => labels.find(label => label.code === code)).filter(Boolean) as MapLabel[];
    for (const label of [...emphasised, ...labels.filter(candidate => placements.has(candidate.code) && !emphasised.includes(candidate))]) {
      const [x, y] = toScreen(label.x, label.y);
      if (x < -200 || x > size.width + 200 || y < -50 || y > size.height + 50) continue;
      const placed = placements.get(label.code) ?? 'right', width = drawnWidth(context, label);
      const boxOn = (side: 'right' | 'left'): ScreenBox => {
        const left = side === 'right' ? x + dotRadius + dotGap : x - dotRadius - dotGap - width;
        return [left, y - labelHeight / 2, left + width, y + labelHeight / 2];
      };
      const box = ([placed, placed === 'right' ? 'left' : 'right'] as const).map(boxOn)
        .find(candidate => isInside(candidate) && !blocked.some(other => overlaps(candidate, other, 0)) && !drawnLabels.some(other => overlaps(candidate, other.box, 4)));
      if (!box) continue;
      drawnLabels.push({ label, box, dot: [x, y] });
    }
    // Ordinary labels are white on a light map and a dark slate on a dark one; the visitor's label is the strongest either way.
    const plain = theme.isDark ? { fill: '#252D38', ink: '#EDF1F5', flagEdge: '#FFFFFF40' } : { fill: '#FFFFFF', ink: '#10151C', flagEdge: '#10151C33' };
    const strong = theme.isDark ? { fill: '#EDF1F5', ink: '#10151C', flagEdge: '#10151C33' } : { fill: '#10151C', ink: '#FFFFFF', flagEdge: '#FFFFFF59' };
    for (const { label, box, dot } of [...drawnLabels].reverse()) {
      const isStrong = label.code === emphasis.dark, isRinged = label.code === emphasis.ringed, look = isStrong ? strong : plain;
      context.beginPath(); context.arc(dot[0], dot[1], dotRadius + 1.5, 0, Math.PI * 2); context.fillStyle = '#10151C'; context.fill();
      context.beginPath(); context.arc(dot[0], dot[1], dotRadius + 1, 0, Math.PI * 2); context.fillStyle = '#FFFFFF'; context.fill();
      context.beginPath(); context.arc(dot[0], dot[1], dotRadius - 0.5, 0, Math.PI * 2); context.fillStyle = label.colour; context.fill();
      context.beginPath(); context.roundRect(box[0], box[1], box[2] - box[0], labelHeight, 5);
      context.shadowColor = '#10151C33'; context.shadowBlur = 2; context.shadowOffsetY = 1;
      context.fillStyle = look.fill; context.fill();
      context.shadowColor = 'transparent';
      if (isRinged) { context.lineWidth = 2; context.strokeStyle = theme.isDark ? '#EDF1F5' : '#10151C'; context.stroke(); }
      if (label.flag) {
        context.save(); context.beginPath(); context.roundRect(box[0] + labelPadLeft, box[1] + (labelHeight - flagHeight) / 2, flagWidth, flagHeight, 2); context.clip();
        context.drawImage(label.flag, box[0] + labelPadLeft, box[1] + (labelHeight - flagHeight) / 2, flagWidth, flagHeight);
        context.restore();
        context.beginPath(); context.roundRect(box[0] + labelPadLeft + 0.25, box[1] + (labelHeight - flagHeight) / 2 + 0.25, flagWidth - 0.5, flagHeight - 0.5, 2);
        context.lineWidth = 0.5; context.strokeStyle = look.flagEdge; context.stroke();
      }
      context.fillStyle = look.ink; context.textBaseline = 'middle';
      context.font = labelFont(500); context.fillText(label.name, box[0] + labelPadLeft + flagWidth + labelGap, box[1] + labelHeight / 2 + 0.5);
      const nameWidth = context.measureText(label.name).width;
      const isLightLabel = theme.isDark === isStrong;
      if (label.amountColours) context.fillStyle = isLightLabel ? label.amountColours.onLight : label.amountColours.onDark;
      context.font = labelFont(700); context.fillText(label.amount, box[0] + labelPadLeft + flagWidth + labelGap + nameWidth + labelGap, box[1] + labelHeight / 2 + 0.5);
    }
  }

  // ---- Drawing, at most once a frame.
  let frameRequested = false;
  function draw(): void {
    if (frameRequested) return;
    frameRequested = true;
    requestAnimationFrame(() => {
      frameRequested = false;
      const pixelRatio = shapeCanvas.width / size.width, scale = viewScale(), [tx, ty] = viewTranslate();
      gl.viewport(0, 0, shapeCanvas.width, shapeCanvas.height);
      gl.clearColor(theme.sea[0], theme.sea[1], theme.sea[2], 1); gl.clear(gl.COLOR_BUFFER_BIT);
      if (geometry && fillVao && colourBytes.length) {
        gl.useProgram(fill.program);
        gl.uniform2f(fill.uniforms.scale, scale, scale); gl.uniform2f(fill.uniforms.translate, tx, ty); gl.uniform2f(fill.uniforms.viewport, size.width, size.height);
        gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, colourTexture); gl.uniform1i(fill.uniforms.colours, 0);
        gl.bindVertexArray(fillVao); gl.drawElements(gl.TRIANGLES, fillIndexCount, gl.UNSIGNED_INT, 0);
        gl.useProgram(line.program);
        gl.uniform2f(line.uniforms.scale, scale, scale); gl.uniform2f(line.uniforms.translate, tx, ty); gl.uniform2f(line.uniforms.viewport, size.width, size.height);
        gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
        // Region lines fade in as the regions grow big enough to tell apart.
        const level = zoomLevel(), regionAlpha = Math.max(0, Math.min(1, (level - 3.2) / 1.2)) * 0.35;
        const [lineRed, lineGreen, lineBlue] = theme.line, [inkRed, inkGreen, inkBlue] = theme.ink;
        const styles: [string, [number, number, number, number], number][] = [
          ['region', [lineRed, lineGreen, lineBlue, regionAlpha], 0.4], ['state', [lineRed, lineGreen, lineBlue, 0.55], 0.45],
          ['country', [lineRed, lineGreen, lineBlue, 1], 0.45], ['highlight', [inkRed, inkGreen, inkBlue, 1], 1],
        ];
        for (const [kind, colour, halfWidth] of styles) {
          const vao = lineVaos.get(kind as LineKind | 'highlight');
          if (!vao || colour[3] <= 0) continue;
          gl.uniform4f(line.uniforms.lineColour, ...colour); gl.uniform1f(line.uniforms.halfWidth, halfWidth);
          gl.bindVertexArray(vao.vao); gl.drawArraysInstanced(gl.TRIANGLES, 0, 6, vao.count);
        }
        gl.disable(gl.BLEND); gl.bindVertexArray(null);
      }
      const context = labelCanvas.getContext('2d')!;
      context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
      context.clearRect(0, 0, size.width, size.height);
      drawLabels(context);
    });
  }

  // ---- What is under the pointer: a label first, then a shape.
  function labelAt(screenX: number, screenY: number): MapLabel | null {
    for (const { label, box, dot } of drawnLabels) {
      if ((screenX >= box[0] && screenX <= box[2] && screenY >= box[1] && screenY <= box[3]) || Math.hypot(screenX - dot[0], screenY - dot[1]) <= dotRadius + 4) return label;
    }
    return null;
  }
  const shapeUnder = (screenX: number, screenY: number) => (geometry ? shapeAt(geometry, ...toMap(screenX, screenY)) : -1);
  let pressedAt: [number, number] | null = null;
  labelCanvas.addEventListener('pointerdown', event => { pressedAt = [event.offsetX, event.offsetY]; });
  labelCanvas.addEventListener('click', event => {
    if (pressedAt && Math.hypot(event.offsetX - pressedAt[0], event.offsetY - pressedAt[1]) > 6) return;
    const label = labelAt(event.offsetX, event.offsetY);
    const [x, y] = toMap(event.offsetX, event.offsetY);
    events.placeAt(x, y, shapeUnder(event.offsetX, event.offsetY), label?.code ?? null);
  });
  labelCanvas.addEventListener('pointermove', event => {
    if (event.pointerType === 'touch' || event.buttons) return;
    const label = labelAt(event.offsetX, event.offsetY);
    labelCanvas.style.cursor = label ? 'pointer' : 'grab';
    events.hovered(label ? -1 : shapeUnder(event.offsetX, event.offsetY), label?.code ?? null, event.clientX, event.clientY);
  });
  labelCanvas.addEventListener('pointerleave', () => events.hovered(-1, null, 0, 0));

  // Measured now, so a place opened by the link can be shown at once, and again whenever the window changes size.
  fit();
  new ResizeObserver(() => fit()).observe(container);
  return {
    setGeometry, setShapeColours, setLabels, setHighlightedShape, show, showBox, showWorld, zoomBy, fit, redraw: draw,
    setEmphasis(next: typeof emphasis) { emphasis = next; draw(); },
    setTheme(next: MapTheme) { theme = next; draw(); },
    setCovers(next: MapCovers) { covers = next; draw(); },
    get geometry() { return geometry; },
    // The zoom from which a place's label shows, for checks, or null if it never does.
    labelLevelOf(code: string): number | null {
      for (let level = 0; level <= deepestZoom; level += labelStep) if (placementsAt(level).has(code)) return level;
      return null;
    },
    zoomLevel,
  };
}
export type MapView = ReturnType<typeof createMapView>;
