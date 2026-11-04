const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async () => { const b = await chromium.launch(); const p = await b.newPage({deviceScaleFactor: 2});
 const jobs=[['logo.svg','logo.png','#FBF6EE'],['logo-white.svg','logo-white.png','#1E2238'],['logo-icon.svg','logo-icon.png',null],['logo-icon-dark.svg','logo-icon-dark.png',null]];
 for (const [src,out,bg] of jobs){ const svg=fs.readFileSync(src,'utf8'); const m=svg.match(/width="(\d+)" height="(\d+)"/); const w=+m[1], h=+m[2];
  await p.setViewportSize({width:w,height:h}); await p.setContent(`<html><body style="margin:0;background:${bg||'transparent'}">${svg}</body></html>`);
  await p.screenshot({path:out, omitBackground: !bg, clip:{x:0,y:0,width:w,height:h}}); }
 // favicon 64x64 (rendered at 1x)
 const p2 = await b.newPage({deviceScaleFactor:1}); await p2.setViewportSize({width:64,height:64});
 await p2.setContent(`<html><body style="margin:0">${fs.readFileSync('logo-icon.svg','utf8').replace('width="512" height="512"','width="64" height="64"')}</body></html>`);
 await p2.screenshot({path:'favicon-64.png', omitBackground:true}); await b.close(); })();
