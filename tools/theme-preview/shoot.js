const { chromium, devices } = require('playwright'); const path = require('path'); const fs = require('fs');
const OUT = path.resolve(__dirname, '../../docs/preview'); fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const b = await chromium.launch();
  const shots = [
    ['home.html', 'home-desktop.png', { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 }],
    ['product.html', 'product-desktop.png', { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 }],
    ['product.html', 'product-mobile.png', { ...devices['iPhone 13'] }],
    ['home.html', 'home-mobile.png', { ...devices['iPhone 13'] }],
  ];
  for (const [src, out, opts] of shots) {
    const ctx = await b.newContext(opts); const p = await ctx.newPage();
    await p.goto('file://' + path.join(__dirname, 'out', src)); await p.waitForTimeout(800);
    await p.screenshot({ path: path.join(OUT, out), fullPage: true });
    await ctx.close(); console.log('shot', out);
  }
  await b.close();
})();
