// The map's shapes and lines in one compact file, written by tools/map/build-map-geometry.ts and read by the page and the Worker.
// Points are Web Mercator, scaled so the world is one unit wide and one tall (x from the antimeridian eastwards, y from the north),
// rounded to a grid of 2^24 across. Each border is stored once, as an arc of points, each point as its difference from the one
// before; a shape's rings are lists of arcs, as in TopoJSON. The triangles the graphics card fills come precomputed.

export const gridSize = 2 ** 24;

// The lines between places, from the most to the least prominent.
export const lineKinds = ['country', 'state', 'region'] as const;
export type LineKind = typeof lineKinds[number];

export type MapGeometry = {
  shapeCodes: string[];
  // Every shape's rings, one after another: x and y of each point, in map units.
  points: Float32Array;
  // Where each ring starts in points (counted in points), with one extra entry at the end.
  ringStarts: Uint32Array;
  ringIsOuter: Uint8Array;
  // Each shape's first ring, with one extra entry at the end.
  shapeFirstRing: Uint32Array;
  // Triangles over all the points, for the graphics card.
  triangleIndices: Uint32Array;
  shapeOfPoint: Uint16Array;
  // Each shape's bounding box: west, north, east, south, in map units.
  shapeBoxes: Float32Array;
  lines: Record<LineKind, Float32Array[]>;
};

export type GeometryHeader = {
  shapeCodes: string[]; arcCount: number; arcPointCount: number; ringCount: number; pointCount: number; triangleIndexCount: number;
  lineArcCounts: Record<LineKind, number>;
};

export class VarintWriter {
  private bytes: number[] = [];
  unsigned(value: number): void {
    while (value >= 0x80) { this.bytes.push((value % 0x80) | 0x80); value = Math.floor(value / 0x80); }
    this.bytes.push(value);
  }
  signed(value: number): void { this.unsigned(value < 0 ? -2 * value - 1 : 2 * value); }
  result(): Uint8Array { return Uint8Array.from(this.bytes); }
}

class VarintReader {
  private position = 0;
  private readonly bytes: Uint8Array;
  constructor(bytes: Uint8Array) { this.bytes = bytes; }
  unsigned(): number {
    let value = 0, multiplier = 1, byte: number;
    do { byte = this.bytes[this.position++]; value += (byte & 0x7f) * multiplier; multiplier *= 0x80; } while (byte & 0x80);
    return value;
  }
  signed(): number { const value = this.unsigned(); return value % 2 ? -(value + 1) / 2 : value / 2; }
  get isDone(): boolean { return this.position >= this.bytes.length; }
}

// A ring's points from its arcs, in grid units: arcs joined end to start, the closing point and repeated points dropped.
// The builder triangulates exactly these points, so both sides must assemble rings the same way.
export function assembleRing(arcs: Int32Array[], arcReferences: number[]): number[] {
  const out: number[] = [];
  for (const reference of arcReferences) {
    const arc = arcs[reference < 0 ? ~reference : reference], count = arc.length / 2;
    for (let step = out.length ? 1 : 0; step < count; step++) {
      const point = reference < 0 ? count - 1 - step : step, x = arc[point * 2], y = arc[point * 2 + 1];
      if (out.length && out[out.length - 2] === x && out[out.length - 1] === y) continue;
      out.push(x, y);
    }
  }
  if (out.length >= 4 && out[0] === out[out.length - 2] && out[1] === out[out.length - 1]) out.length -= 2;
  return out;
}

export function readMapGeometry(file: Uint8Array): MapGeometry {
  const headerLength = new DataView(file.buffer, file.byteOffset, 4).getUint32(0, true);
  const header: GeometryHeader = JSON.parse(new TextDecoder().decode(file.subarray(4, 4 + headerLength)));
  const reader = new VarintReader(file.subarray(4 + headerLength));

  const arcs: Int32Array[] = [];
  let x = 0, y = 0;
  for (let arc = 0; arc < header.arcCount; arc++) {
    const count = reader.unsigned(), points = new Int32Array(count * 2);
    for (let point = 0; point < count; point++) { x += reader.signed(); y += reader.signed(); points[point * 2] = x; points[point * 2 + 1] = y; }
    arcs.push(points);
  }

  const shapeCount = header.shapeCodes.length;
  const points = new Float32Array(header.pointCount * 2), shapeOfPoint = new Uint16Array(header.pointCount);
  const ringStarts = new Uint32Array(header.ringCount + 1), ringIsOuter = new Uint8Array(header.ringCount);
  const shapeFirstRing = new Uint32Array(shapeCount + 1), shapeBoxes = new Float32Array(shapeCount * 4);
  let pointIndex = 0, ringIndex = 0;
  for (let shape = 0; shape < shapeCount; shape++) {
    shapeFirstRing[shape] = ringIndex;
    let west = Infinity, north = Infinity, east = -Infinity, south = -Infinity, previousReference = 0;
    const ringCount = reader.unsigned();
    for (let ring = 0; ring < ringCount; ring++, ringIndex++) {
      ringIsOuter[ringIndex] = reader.unsigned();
      const references: number[] = [];
      for (let count = reader.unsigned(); count > 0; count--) { previousReference += reader.signed(); references.push(previousReference); }
      ringStarts[ringIndex] = pointIndex;
      const gridPoints = assembleRing(arcs, references);
      for (let index = 0; index < gridPoints.length; index += 2, pointIndex++) {
        const mapX = gridPoints[index] / gridSize, mapY = gridPoints[index + 1] / gridSize;
        points[pointIndex * 2] = mapX; points[pointIndex * 2 + 1] = mapY;
        shapeOfPoint[pointIndex] = shape;
        if (mapX < west) west = mapX; if (mapX > east) east = mapX; if (mapY < north) north = mapY; if (mapY > south) south = mapY;
      }
    }
    shapeBoxes.set([west, north, east, south], shape * 4);
  }
  ringStarts[ringIndex] = pointIndex;
  shapeFirstRing[shapeCount] = ringIndex;
  if (pointIndex !== header.pointCount) throw new Error(`The map file's rings have ${pointIndex} points, not ${header.pointCount}`);

  const triangleIndices = new Uint32Array(header.triangleIndexCount);
  for (let shape = 0, index = 0; shape < shapeCount; shape++) {
    const firstPoint = ringStarts[shapeFirstRing[shape]];
    let local = 0;
    for (let count = reader.unsigned(); count > 0; count--) { local += reader.signed(); triangleIndices[index++] = firstPoint + local; }
  }

  const lines = {} as Record<LineKind, Float32Array[]>;
  for (const kind of lineKinds) {
    lines[kind] = [];
    let arc = 0;
    for (let count = header.lineArcCounts[kind]; count > 0; count--) {
      arc += reader.unsigned();
      lines[kind].push(Float32Array.from(arcs[arc], value => value / gridSize));
    }
  }
  if (!reader.isDone) throw new Error('The map file has more in it than its header says');
  return { shapeCodes: header.shapeCodes, points, ringStarts, ringIsOuter, shapeFirstRing, triangleIndices, shapeOfPoint, shapeBoxes, lines };
}

export const mapXOf = (longitude: number) => (longitude + 180) / 360;
export function mapYOf(latitude: number): number {
  const clamped = Math.max(-85.0511, Math.min(85.0511, latitude)) * Math.PI / 180;
  return 0.5 - Math.log(Math.tan(Math.PI / 4 + clamped / 2)) / (2 * Math.PI);
}
export const longitudeOf = (mapX: number) => mapX * 360 - 180;
export const latitudeOf = (mapY: number) => (2 * Math.atan(Math.exp((0.5 - mapY) * 2 * Math.PI)) - Math.PI / 2) * 180 / Math.PI;

// The shape a point on the map is in, by its rings (even-odd), or -1.
export function shapeAt(geometry: MapGeometry, mapX: number, mapY: number): number {
  const { shapeBoxes, shapeFirstRing, ringStarts, points } = geometry;
  for (let shape = 0; shape < geometry.shapeCodes.length; shape++) {
    if (mapX < shapeBoxes[shape * 4] || mapX > shapeBoxes[shape * 4 + 2] || mapY < shapeBoxes[shape * 4 + 1] || mapY > shapeBoxes[shape * 4 + 3]) continue;
    let inside = false;
    for (let ring = shapeFirstRing[shape]; ring < shapeFirstRing[shape + 1]; ring++) {
      const start = ringStarts[ring], end = ringStarts[ring + 1];
      for (let point = start, previous = end - 1; point < end; previous = point++) {
        const x1 = points[point * 2], y1 = points[point * 2 + 1], x0 = points[previous * 2], y0 = points[previous * 2 + 1];
        if ((y1 > mapY) !== (y0 > mapY) && mapX < (x0 - x1) * (mapY - y1) / (y0 - y1) + x1) inside = !inside;
      }
    }
    if (inside) return shape;
  }
  return -1;
}
