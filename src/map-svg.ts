// The map as SVG, for the share pictures the Worker draws: every shape filled with its colour, one path per colour, and the
// borders the frame's scale has room for. Points closer than half a pixel to the last one drawn are skipped.
import type { MapGeometry } from './map-geometry.ts';

export type SvgMapFrame = {
  // The frame's size in pixels, and where the map's top left corner sits and how many pixels one map unit spans.
  width: number; height: number; left: number; top: number; scale: number;
};

function ringPath(geometry: MapGeometry, ring: number, frame: SvgMapFrame): string {
  const { points, ringStarts } = geometry, start = ringStarts[ring], end = ringStarts[ring + 1];
  let path = '', lastX = NaN, lastY = NaN, count = 0;
  for (let point = start; point < end; point++) {
    const x = Math.round((points[point * 2] * frame.scale + frame.left) * 2) / 2, y = Math.round((points[point * 2 + 1] * frame.scale + frame.top) * 2) / 2;
    if (Math.abs(x - lastX) < 0.5 && Math.abs(y - lastY) < 0.5) continue;
    path += `${count ? 'L' : 'M'}${x} ${y}`;
    lastX = x; lastY = y; count++;
  }
  return count >= 3 ? `${path}Z` : '';
}

function isOutsideFrame(geometry: MapGeometry, shape: number, frame: SvgMapFrame): boolean {
  const box = geometry.shapeBoxes.subarray(shape * 4, shape * 4 + 4);
  return box[2] * frame.scale + frame.left < 0 || box[0] * frame.scale + frame.left > frame.width
    || box[3] * frame.scale + frame.top < 0 || box[1] * frame.scale + frame.top > frame.height;
}

export function svgMap(geometry: MapGeometry, frame: SvgMapFrame, colourOfShape: (shape: number) => string, borders: { colour: string; width: number; kinds: ('country' | 'state' | 'region')[] }): string {
  const pathsByColour = new Map<string, string>();
  for (let shape = 0; shape < geometry.shapeCodes.length; shape++) {
    if (isOutsideFrame(geometry, shape, frame)) continue;
    let path = '';
    for (let ring = geometry.shapeFirstRing[shape]; ring < geometry.shapeFirstRing[shape + 1]; ring++) path += ringPath(geometry, ring, frame);
    if (!path) continue;
    const colour = colourOfShape(shape);
    pathsByColour.set(colour, (pathsByColour.get(colour) ?? '') + path);
  }
  let svg = '';
  for (const [colour, path] of pathsByColour) svg += `<path d="${path}" fill="${colour}" fill-rule="evenodd" stroke="${colour}" stroke-width="0.6" stroke-linejoin="round"/>`;
  let lines = '';
  for (const kind of borders.kinds) {
    for (const line of geometry.lines[kind]) {
      let path = '', lastX = NaN, lastY = NaN;
      for (let index = 0; index < line.length; index += 2) {
        const x = Math.round((line[index] * frame.scale + frame.left) * 2) / 2, y = Math.round((line[index + 1] * frame.scale + frame.top) * 2) / 2;
        if (Math.abs(x - lastX) < 0.5 && Math.abs(y - lastY) < 0.5 && index + 2 < line.length) continue;
        path += `${path ? 'L' : 'M'}${x} ${y}`;
        lastX = x; lastY = y;
      }
      lines += path;
    }
  }
  if (lines) svg += `<path d="${lines}" fill="none" stroke="${borders.colour}" stroke-width="${borders.width}" stroke-linejoin="round" stroke-linecap="round"/>`;
  return svg;
}
