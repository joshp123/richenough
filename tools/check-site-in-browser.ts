// Uses the site as a visitor would, in headless WebKit (Safari's engine), and photographs each state at phone, laptop and wide
// sizes, light and dark, plus the share pictures at full size and at the sizes Twitter shows them.
// Usage: node tools/check-site-in-browser.ts <site address> <folder for the photographs>
import { webkit, type Page } from 'playwright-core';
import { mkdir, writeFile } from 'node:fs/promises';

const [siteAddress, folder] = process.argv.slice(2);
if (!siteAddress || !folder) throw new Error('Usage: node tools/check-site-in-browser.ts <site address> <folder>');
await mkdir(folder, { recursive: true });

const sizes = { phone: { width: 390, height: 844 }, laptop: { width: 1512, height: 900 }, wide: { width: 2560, height: 1300 } };
const browser = await webkit.launch();
const problems: string[] = [];

async function openPage(size: keyof typeof sizes, colorScheme: 'light' | 'dark', path = '/'): Promise<Page> {
  const context = await browser.newContext({ viewport: sizes[size], deviceScaleFactor: 2, colorScheme, hasTouch: size === 'phone', isMobile: size === 'phone' });
  const page = await context.newPage();
  page.on('console', message => { if (message.type() === 'error') problems.push(`${size} ${colorScheme}: ${message.text()}`); });
  page.on('pageerror', error => problems.push(`${size} ${colorScheme}: ${error.message}`));
  await page.goto(siteAddress + path);
  await page.waitForFunction(() => document.body.classList.contains('is-ready'));
  // The detailed map arrives after the page is ready.
  await page.waitForTimeout(1500);
  return page;
}
const photograph = (page: Page, name: string) => page.screenshot({ path: `${folder}/${name}.png` });

// How long the map takes to draw while it moves: frames during sixty small zoom and pan steps.
async function frameTimes(page: Page): Promise<string> {
  return page.evaluate(async () => {
    const view = (window as unknown as { enough: { mapView: { zoomBy(factor: number): unknown } } }).enough.mapView;
    const canvas = document.querySelector('.map-labels')!, box = canvas.getBoundingClientRect(), gaps: number[] = [];
    let last = performance.now();
    for (let step = 0; step < 60; step++) {
      canvas.dispatchEvent(new WheelEvent('wheel', { deltaY: step < 30 ? -40 : 40, clientX: box.width / 2 + step * 3, clientY: box.height / 2, bubbles: true, cancelable: true }));
      await new Promise(resolve => requestAnimationFrame(resolve));
      const now = performance.now(); gaps.push(now - last); last = now;
    }
    void view;
    gaps.sort((a, b) => a - b);
    return `median ${gaps[30].toFixed(1)} ms, slowest ${gaps[59].toFixed(1)} ms between frames`;
  });
}

for (const size of ['laptop', 'phone', 'wide'] as const) {
  for (const colorScheme of ['light', 'dark'] as const) {
    const page = await openPage(size, colorScheme);
    await photograph(page, `${size}-${colorScheme}-01-first-load`);
    if (colorScheme === 'dark') { await page.close(); continue; }
    console.log(`${size}: ${await frameTimes(page)}`);

    // Search: the visitor says where they are.
    await page.getByRole('button', { name: /Amsterdam|Choose a place/ }).first().click();
    await page.getByRole('searchbox', { name: 'Search for a place' }).fill('lisb');
    await photograph(page, `${size}-02-search-lisbon`);
    await page.getByRole('searchbox', { name: 'Search for a place' }).press('Enter');
    await page.waitForTimeout(900);
    await photograph(page, `${size}-03-lisbon-details`);

    // A place on the map: a US county, opened by tapping it.
    await page.goto(`${siteAddress}/?place=us-06037`);
    await page.waitForFunction(() => document.body.classList.contains('is-ready'));
    await page.waitForTimeout(1500);
    await photograph(page, `${size}-04-los-angeles-county`);
    await page.getByRole('button', { name: 'Compare with' }).first().click().catch(() => {});
    await page.waitForTimeout(400);
    await photograph(page, `${size}-05-compared`);

    // The first mode's share picture, then the second mode: what the visitor has, and the currency.
    await page.goto(`${siteAddress}/?me=lisbon&vs=los-angeles`);
    await page.waitForFunction(() => document.body.classList.contains('is-ready'));
    await page.waitForTimeout(1000);
    if (size === 'laptop') await writeFile(`${folder}/picture-7x8-how-much-you-need.png`, Buffer.from(await (await fetch(`${siteAddress}/picture.png?me=lisbon&vs=los-angeles&also=EUR`)).arrayBuffer()));
    await page.getByRole('button', { name: 'Am I gonna make it?' }).click();
    await page.waitForTimeout(300);
    await photograph(page, `${size}-06-am-i-gonna-make-it`);
    await page.locator('#have-slider').fill('0.7');
    await page.waitForTimeout(300);
    await photograph(page, `${size}-06b-have-two-and-a-half-million`);
    await page.locator('#currency-button').click();
    await photograph(page, `${size}-07-currency-list`);
    await page.getByRole('menuitemradio', { name: /Euro/ }).click();
    await page.waitForTimeout(300);
    await photograph(page, `${size}-08-in-euros`);

    // Sharing.
    await page.locator('#share-button').click();
    await page.waitForFunction(() => (document.getElementById('share-picture') as HTMLImageElement).complete, null, { timeout: 30000 });
    await page.waitForTimeout(500);
    await photograph(page, `${size}-09-share`);
    if (size === 'laptop') {
      const pictureAddress = await page.locator('#share-picture').getAttribute('src');
      const picture = await (await fetch(siteAddress + pictureAddress)).arrayBuffer();
      await writeFile(`${folder}/picture-7x8.png`, Buffer.from(picture));
      const preview = await (await fetch(`${siteAddress}/preview.png${pictureAddress!.slice('/picture.png'.length)}`)).arrayBuffer();
      await writeFile(`${folder}/preview-2x1.png`, Buffer.from(preview));
    }
    await page.close();
  }
}

// The share pictures at the sizes Twitter shows them: one picture 516 wide on the web and 313 in the phone app, two side by
// side as 7:8 tiles 155 wide on a phone, and the link preview 516 wide.
const twitter = await (await browser.newContext({ viewport: { width: 1100, height: 1500 }, deviceScaleFactor: 2 })).newPage();
const dataUrl = async (file: string) => `data:image/png;base64,${Buffer.from(await (await import('node:fs/promises')).readFile(`${folder}/${file}`)).toString('base64')}`;
const [picture, needPicture, preview] = await Promise.all([dataUrl('picture-7x8.png'), dataUrl('picture-7x8-how-much-you-need.png'), dataUrl('preview-2x1.png')]);
await twitter.setContent(`<body style="margin:24px;font:14px system-ui;background:#fff;display:flex;flex-wrap:wrap;gap:32px;align-items:flex-start">
  <figure style="margin:0"><img src="${needPicture}" style="width:516px;border-radius:16px;border:1px solid #cfd9de"><figcaption>One picture (How much you need), web, 516 wide</figcaption></figure>
  <figure style="margin:0"><img src="${picture}" style="width:516px;border-radius:16px;border:1px solid #cfd9de"><figcaption>One picture (Am I gonna make it?), web, 516 wide</figcaption></figure>
  <figure style="margin:0"><img src="${picture}" style="width:313px;border-radius:16px;border:1px solid #cfd9de"><figcaption>One picture, phone, 313 wide</figcaption></figure>
  <figure style="margin:0"><div style="display:flex;gap:2px;width:313px;border-radius:16px;overflow:hidden;border:1px solid #cfd9de"><img src="${picture}" style="width:155px;aspect-ratio:7/8;object-fit:cover"><img src="${picture}" style="width:155px;aspect-ratio:7/8;object-fit:cover"></div><figcaption>Two pictures, phone</figcaption></figure>
  <figure style="margin:0"><img src="${preview}" style="width:516px;aspect-ratio:1.91;object-fit:cover;border-radius:16px;border:1px solid #cfd9de"><figcaption>Link preview, web, trimmed to 1.91:1</figcaption></figure>
</body>`);
await twitter.waitForTimeout(300);
await twitter.screenshot({ path: `${folder}/twitter-sizes.png`, fullPage: true });
await browser.close();
console.log(problems.length ? `Problems:\n${[...new Set(problems)].join('\n')}` : 'No errors in the browser console.');
