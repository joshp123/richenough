// Flags: a country's own, and a US state's over the lower right corner of the US flag.
import { flagCodesOf, type Places } from '../src/places.ts';

// Filled in by hosting/build.mjs: each flag file's address, which changes when the file does.
declare const FLAG_PATHS: Record<string, string>;
const flagPaths = FLAG_PATHS;

export function flagHtml(places: Places, code: string): string {
  const { country, state } = flagCodesOf(places, code);
  if (!flagPaths[country]) return '<span class="flag"></span>';
  const corner = state && flagPaths[state] ? `<img class="flag-corner" src="${flagPaths[state]}" alt="">` : '';
  return `<span class="flag"><img src="${flagPaths[country]}" alt="">${corner}</span>`;
}

const images = new Map<string, Promise<HTMLImageElement | null>>();
function image(flagCode: string): Promise<HTMLImageElement | null> {
  if (!images.has(flagCode)) {
    images.set(flagCode, flagPaths[flagCode]
      ? new Promise(resolve => { const picture = new Image(); picture.onload = () => resolve(picture); picture.onerror = () => resolve(null); picture.src = flagPaths[flagCode]; })
      : Promise.resolve(null));
  }
  return images.get(flagCode)!;
}

// A small picture of the flag for the map's labels, 17 by 12 points, drawn sharp for the screen.
const canvases = new Map<string, Promise<HTMLCanvasElement | null>>();
export function flagCanvas(places: Places, code: string): Promise<HTMLCanvasElement | null> {
  const { country, state } = flagCodesOf(places, code), key = `${country}|${state}`;
  if (!canvases.has(key)) {
    canvases.set(key, Promise.all([image(country), state ? image(state) : Promise.resolve(null)]).then(([countryFlag, stateFlag]) => {
      if (!countryFlag) return null;
      const pixelRatio = Math.max(2, devicePixelRatio || 1), width = 17 * pixelRatio, height = 12 * pixelRatio;
      const canvas = document.createElement('canvas'); canvas.width = width; canvas.height = height;
      const context = canvas.getContext('2d')!;
      const cover = (picture: HTMLImageElement, left: number, top: number, boxWidth: number, boxHeight: number) => {
        const scale = Math.max(boxWidth / picture.naturalWidth, boxHeight / picture.naturalHeight);
        context.drawImage(picture, left + (boxWidth - picture.naturalWidth * scale) / 2, top + (boxHeight - picture.naturalHeight * scale) / 2, picture.naturalWidth * scale, picture.naturalHeight * scale);
      };
      context.save(); context.beginPath(); context.rect(0, 0, width, height); context.clip(); cover(countryFlag, 0, 0, width, height); context.restore();
      if (stateFlag) {
        const cornerWidth = width * 0.6, cornerHeight = height * 0.6;
        context.fillStyle = '#FFFFFF'; context.fillRect(width - cornerWidth - pixelRatio, height - cornerHeight - pixelRatio, cornerWidth + pixelRatio, cornerHeight + pixelRatio);
        context.save(); context.beginPath(); context.rect(width - cornerWidth, height - cornerHeight, cornerWidth, cornerHeight); context.clip();
        cover(stateFlag, width - cornerWidth, height - cornerHeight, cornerWidth, cornerHeight); context.restore();
      }
      return canvas;
    }));
  }
  return canvases.get(key)!;
}
