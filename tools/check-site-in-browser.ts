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
  // The detailed map and the labels' flags arrive after the page is ready.
  await page.waitForTimeout(3000);
  return page;
}
// Every photograph is also checked for text a visitor cannot read whole: text ending in "…", an element that hides part of its
// text, and in "Am I gonna make it?" an amount written with a sign (+$0.3M), which Josh found confusing.
let photographCount = 0;
async function photograph(page: Page, name: string): Promise<void> {
  photographCount++;
  await page.screenshot({ path: `${folder}/${name}.png` });
  const found = await page.evaluate(() => {
    const out: string[] = [], isHaveMode = document.body.dataset.mode === 'have';
    for (const element of document.querySelectorAll<HTMLElement>('body *')) {
      if (element.closest('[hidden]') || !element.offsetParent && getComputedStyle(element).position !== 'fixed') continue;
      const style = getComputedStyle(element), ownText = [...element.childNodes].filter(node => node.nodeType === 3).map(node => node.textContent).join('').trim();
      if (ownText.endsWith('…')) out.push(`ends in …: "${ownText}"`);
      if (isHaveMode && /[+−-]\s?[$€£¥]/.test(ownText)) out.push(`signed amount: "${ownText}"`);
      const hides = style.overflowX === 'hidden' || style.overflowX === 'clip' || style.textOverflow === 'ellipsis';
      if (hides && element.textContent!.trim() && element.scrollWidth > element.clientWidth + 1 && element.tagName !== 'HTML' && element.tagName !== 'BODY') out.push(`cut off: "${element.textContent!.trim().slice(0, 60)}"`);
    }
    return out;
  });
  for (const problem of found) problems.push(`${name}: ${problem}`);
}

// How long the map takes to draw while it moves: frames during sixty small zoom and pan steps, after the pointer arrives on the map
// as a visitor's does before they scroll, or a finger lands as it does before it drags.
async function frameTimes(page: Page, size: keyof typeof sizes): Promise<string> {
  const { width, height } = sizes[size];
  if (size === 'phone') await page.evaluate(([x, y]) => document.querySelector('.map-labels')!.dispatchEvent(new PointerEvent('pointerdown', { pointerType: 'touch', clientX: x, clientY: y, bubbles: true })), [width / 2, height / 2]);
  else await page.mouse.move(width / 2, height / 2);
  await page.waitForTimeout(100);
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

// Josh's rule: the map is the product. At phone size it must keep at least 560 of the screen's 844 px between the bar and the strip.
async function phoneMapHeight(page: Page, photo: string): Promise<void> {
  const height = await page.evaluate(() => document.getElementById('strip')!.getBoundingClientRect().top - document.querySelector('.bar')!.getBoundingClientRect().bottom);
  console.log(`${photo}: ${Math.round(height)} px of map between the bar and the strip`);
  if (height < 560) problems.push(`${photo}: only ${Math.round(height)} px of map between the bar and the strip; the least is 560`);
}

const openAt = async (page: Page, path: string) => {
  await page.goto(siteAddress + path);
  await page.waitForFunction(() => document.body.classList.contains('is-ready'));
  // The detailed map and the labels' flags arrive after the page is ready.
  await page.waitForTimeout(3000);
};
for (const size of ['laptop', 'phone', 'wide'] as const) {
  for (const colorScheme of ['light', 'dark'] as const) {
    const name = `${size}-${colorScheme}`, page = await openPage(size, colorScheme);
    await photograph(page, `${name}-01-first-load`);
    if (size === 'phone') await phoneMapHeight(page, `${name}-01-first-load`);
    if (size === 'wide') { await page.close(); continue; }

    // The second mode, from the first load: the map must not move.
    await page.getByRole('button', { name: 'Am I gonna make it?' }).click();
    await page.waitForTimeout(400);
    await photograph(page, `${name}-02-am-i-gonna-make-it`);
    if (size === 'phone') await phoneMapHeight(page, `${name}-02-am-i-gonna-make-it`);
    await page.locator('#have-slider').fill('0.7');
    await page.waitForTimeout(300);
    await photograph(page, `${name}-03-have-two-and-a-half-million`);
    await page.getByRole('button', { name: 'How much you need' }).click();
    await page.waitForTimeout(300);
    if (colorScheme === 'light') console.log(`${size}: ${await frameTimes(page, size)}`);

    // Search: the visitor says where they are, and the map comes back with them on it.
    await page.locator('[data-pick="visitor"]').click();
    await page.getByRole('searchbox', { name: 'Search for a place' }).fill('lisb');
    await photograph(page, `${name}-04-search-lisbon`);
    await page.getByRole('searchbox', { name: 'Search for a place' }).press('Enter');
    await page.waitForTimeout(900);
    await photograph(page, `${name}-05-you-are-in-lisbon`);

    // A place's details, then comparing with it from there.
    await openAt(page, '/?me=amsterdam&place=lisbon');
    await photograph(page, `${name}-06-lisbon-details`);
    await page.getByRole('button', { name: /^Compare with/ }).click();
    await page.waitForTimeout(900);
    await photograph(page, `${name}-07-compared-with-lisbon`);

    // A US county, opened from its link.
    await openAt(page, '/?place=us-06037');
    await photograph(page, `${name}-08-los-angeles-county`);

    // The currency and sharing, in each mode.
    await openAt(page, '/?me=amsterdam&vs=lisbon');
    await page.locator('#currency-button').click();
    await photograph(page, `${name}-09-currency-list`);
    await page.getByRole('menuitemradio', { name: /Euro/ }).click();
    await page.waitForTimeout(300);
    await page.locator('#share-button').click();
    await page.waitForFunction(() => (document.getElementById('share-picture') as HTMLImageElement).complete, null, { timeout: 30000 });
    await page.waitForTimeout(500);
    await photograph(page, `${name}-10-share-how-much-you-need`);
    if (size === 'laptop' && colorScheme === 'light') {
      const address = await page.locator('#share-picture').getAttribute('src');
      await writeFile(`${folder}/picture-7x8-how-much-you-need.png`, Buffer.from(await (await fetch(siteAddress + address)).arrayBuffer()));
      await writeFile(`${folder}/preview-2x1.png`, Buffer.from(await (await fetch(`${siteAddress}/preview.png${address!.slice('/picture.png'.length)}`)).arrayBuffer()));
    }
    await page.keyboard.press('Escape');
    await page.getByRole('button', { name: 'Am I gonna make it?' }).click();
    await page.locator('#share-button').click();
    await page.waitForFunction(() => (document.getElementById('share-picture') as HTMLImageElement).complete, null, { timeout: 30000 });
    await page.waitForTimeout(500);
    await photograph(page, `${name}-11-share-am-i-gonna-make-it`);
    if (size === 'laptop' && colorScheme === 'light') {
      const address = await page.locator('#share-picture').getAttribute('src');
      await writeFile(`${folder}/picture-7x8.png`, Buffer.from(await (await fetch(siteAddress + address)).arrayBuffer()));
    }
    await page.keyboard.press('Escape');

    // The longest names a visitor can choose, in both modes, in a place's details and in the place list.
    const longPairs = [['12-long-names-am-i-gonna-make-it', '?mode=have&me=petropavlovsk-kamchatsky&vs=nuts-el422'], ['13-long-names', '?me=saint-petersburg&vs=us-09130'],
      ['14-long-names-county', '?mode=have&me=ho-chi-minh-city&vs=us-06037']];
    for (const [photo, query] of longPairs) {
      await openAt(page, `/${query}`);
      const named = await page.evaluate(() => { const { state } = (window as unknown as { enough: { state: { visitor: string | null; compared: string | null } } }).enough; return [state.visitor, state.compared]; });
      if (named.includes(null)) problems.push(`${photo}: a place in ${query} did not resolve (${named.join(', ')})`);
      await photograph(page, `${name}-${photo}`);
      if (size === 'laptop' && colorScheme === 'light' && photo.startsWith('12')) await writeFile(`${folder}/picture-7x8-long-names.png`, Buffer.from(await (await fetch(`${siteAddress}/picture.png${query}`)).arrayBuffer()));
    }
    await openAt(page, '/?me=petropavlovsk-kamchatsky&place=nuts-el422');
    await photograph(page, `${name}-15-long-name-details`);
    await openAt(page, '/?me=petropavlovsk-kamchatsky');
    await page.locator('[data-pick="compared"]').click();
    await page.getByRole('searchbox', { name: 'Search for a place' }).fill('andros');
    await page.waitForTimeout(300);
    await photograph(page, `${name}-16-long-name-search`);

    // China, drawn by province, chosen in the place list: the map frames and outlines the whole country.
    await page.keyboard.press('Escape');
    await openAt(page, '/?me=amsterdam');
    await page.locator('[data-pick="visitor"]').click();
    await page.getByRole('searchbox', { name: 'Search for a place' }).fill('china');
    await page.waitForTimeout(300);
    await page.getByRole('searchbox', { name: 'Search for a place' }).press('Enter');
    await page.waitForTimeout(1200);
    const chosen = await page.evaluate(() => (window as unknown as { enough: { state: { visitor: string | null } } }).enough.state.visitor);
    if (chosen !== 'CN') problems.push(`${name}-17-china-from-search: searching "china" chose ${chosen}, not China`);
    await photograph(page, `${name}-17-china-from-search`);
    await openAt(page, '/?me=cn&place=cn');
    await photograph(page, `${name}-18-china-details`);

    // The About page, reached from a place's sources, with one group of sources open, and from its top. With every group open
    // it must still fit the screen's width.
    await openAt(page, '/?me=amsterdam&place=lisbon');
    await page.getByRole('link', { name: 'All sources' }).click();
    await page.waitForURL('**/about#sources');
    await page.waitForTimeout(500);
    await photograph(page, `${name}-19-about-sources`);
    await page.locator('#sources-rent summary').click();
    await page.waitForTimeout(300);
    await photograph(page, `${name}-20-about-rent-sources`);
    await page.evaluate(() => { for (const group of document.querySelectorAll('details')) group.open = true; });
    const tooWide = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    if (tooWide > 0) problems.push(`${name}-about: with every group of sources open, the page is ${tooWide} px wider than the screen`);
    await page.evaluate(() => { for (const group of document.querySelectorAll('details')) group.open = false; scrollTo(0, 0); });
    await photograph(page, `${name}-21-about`);
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
console.log(problems.length ? `Problems:\n${[...new Set(problems)].join('\n')}`
  : `Checked ${photographCount} photographs: no browser errors, no text cut short or ending in "…", no signed amounts in "Am I gonna make it?", and every named place found.`);
