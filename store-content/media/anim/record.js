const { chromium } = require('playwright'); const fs = require('fs'); const { execSync } = require('child_process');
const jobs = [
  { name: 'lumaube-hero-1920x1080', w: 1920, h: 1080, text: 0, dur: 8 },
  { name: 'lumaube-ad-1080x1920', w: 1080, h: 1920, text: 1, dur: 9 },
  { name: 'lumaube-ad-1080x1080', w: 1080, h: 1080, text: 1, dur: 9 },
];
(async () => {
  const b = await chromium.launch();
  for (const j of jobs) {
    const p = await b.newPage({ viewport: { width: j.w, height: j.h } });
    await p.goto('file://' + process.cwd() + `/sunrise.html?text=${j.text}`);
    const dir = `frames_${j.name}`; fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir);
    const fps = 30, n = j.dur * fps;
    for (let i = 0; i < n; i++) {
      await p.evaluate(([t, d]) => window.render(t, d), [i / fps, j.dur]);
      await p.screenshot({ path: `${dir}/f${String(i).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 92 });
    }
    execSync(`ffmpeg -y -loglevel error -framerate ${fps} -i ${dir}/f%04d.jpg -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -movflags +faststart ../${j.name}.mp4`);
    execSync(`ffmpeg -y -loglevel error -ss ${j.dur - 0.5} -i ../${j.name}.mp4 -frames:v 1 ../${j.name}-last.jpg`);
    fs.rmSync(dir, { recursive: true, force: true });
    console.log('done', j.name);
    await p.close();
  }
  await b.close();
})();
