/* Local preview of the Lumaube Shopify theme with sample data (no Shopify store needed).
 * Usage:  cd tools/theme-preview && npm i liquidjs@10 && node render.js && node shoot.js
 * Renders templates/index.json and templates/product.json through layout/theme.liquid using LiquidJS,
 * with stubs for Shopify-only filters/tags. It is a visual approximation, not Shopify itself. */
const fs = require('fs');
const path = require('path');
const { Liquid } = require('liquidjs');

const ROOT = path.resolve(__dirname, '../../shopify-theme');
const MEDIA = path.resolve(__dirname, '../../store-content/media');
const OUT = path.resolve(__dirname, 'out');
fs.mkdirSync(OUT, { recursive: true });

const read = (p) => fs.readFileSync(path.join(ROOT, p), 'utf8');
const locale = JSON.parse(read('locales/fr.default.json'));
const fileUrl = (p) => 'file://' + p;

const engine = new Liquid({ root: [path.join(ROOT, 'snippets')], extname: '.liquid', dynamicPartials: true, strictVariables: false });

/* ---------- Shopify filter stubs ---------- */
const kw = (args) => Object.fromEntries(args.filter((a) => Array.isArray(a) && a.length === 2));
const lookup = (key) => key.split('.').reduce((o, k) => (o ? o[k] : undefined), locale);
engine.registerFilter('t', (key, ...args) => {
  let v = lookup(key);
  const vars = kw(args);
  if (v && typeof v === 'object') v = vars.count === 1 ? v.one : v.other;
  if (typeof v !== 'string') return key;
  return v.replace(/{{\s*(\w+)\s*}}/g, (_, n) => (vars[n] !== undefined ? vars[n] : ''));
});
engine.registerFilter('asset_url', (n) => fileUrl(path.join(ROOT, 'assets', n)));
engine.registerFilter('stylesheet_tag', (u) => `<link rel="stylesheet" href="${u}">`);
engine.registerFilter('image_url', (img) => (img && img.src) || img || '');
engine.registerFilter('image_tag', (url, ...args) => {
  const o = kw(args);
  return `<img src="${url}" alt="${o.alt || ''}"${o.class ? ` class="${o.class}"` : ''} loading="eager">`;
});
engine.registerFilter('placeholder_svg_tag', (name, cls) =>
  `<svg class="${cls || ''}" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="pg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9E4F0"/><stop offset="1" stop-color="#F7C873"/></linearGradient></defs><rect width="400" height="400" fill="url(#pg)"/></svg>`);
const euro = (c) => (Number(c || 0) / 100).toFixed(2).replace('.', ',') + ' €';
engine.registerFilter('money', euro);
engine.registerFilter('money_with_currency', (c) => euro(c) + ' EUR');
engine.registerFilter('money_without_currency', (c) => (Number(c || 0) / 100).toFixed(2).replace('.', ','));
// font_face returns CSS text, like Shopify, so markup that prints it outside <style> shows up in the preview.
engine.registerFilter('font_face', (font) => `@font-face { font-family: ${(font && font.family) || 'x'}; }`);
for (const f of ['font_url', 'preload_tag', 'structured_data', 'default_pagination', 'external_video_tag', 'media_tag'])
  engine.registerFilter(f, () => '');
engine.registerFilter('font_modify', (font) => ({ ...font, weight: 700 }));
engine.registerFilter('payment_button', () =>
  '<button type="button" class="btn btn--block" style="width:100%;background:#FFC439;color:#111;border:0">Payer avec PayPal</button>');
engine.registerFilter('payment_type_svg_tag', (t) =>
  `<svg class="payment-icon" viewBox="0 0 38 24"><rect width="38" height="24" rx="3" fill="#fff"/><text x="19" y="15" font-size="7" text-anchor="middle" fill="#1E2238" font-family="Inter">${t}</text></svg>`);
engine.registerFilter('video_tag', (v) => `<video src="${(v && v.src) || v}" autoplay muted loop playsinline></video>`);
engine.registerFilter('time_tag', (d) => `<time>${d}</time>`);
engine.registerFilter('format_code', (c) => c);

/* ---------- Shopify tag stubs ---------- */
const blockTag = (name, open, close) => ({
  parse(token, remain) {
    const cls = (token.args.match(/class:\s*'([^']+)'/) || [])[1];
    this.open = cls ? open.replace('<form ', `<form class="${cls}" `) : open;
    this.tpls = [];
    const stream = this.liquid.parser.parseStream(remain)
      .on(`tag:end${name}`, () => stream.stop())
      .on('template', (tpl) => this.tpls.push(tpl));
    stream.start();
  },
  * render(ctx, emitter) {
    emitter.write(this.open);
    yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter);
    emitter.write(close);
  },
});
engine.registerTag('form', blockTag('form', '<form action="#" onsubmit="return false">', '</form>'));
engine.registerTag('paginate', blockTag('paginate', '', ''));

/* ---------- Data ---------- */
const schemaOf = (src) => {
  const m = src.match(/{%-?\s*schema\s*-?%}([\s\S]*?){%-?\s*endschema\s*-?%}/);
  return m ? JSON.parse(m[1]) : {};
};
const stripSchema = (src) => src.replace(/{%-?\s*schema\s*-?%}[\s\S]*?{%-?\s*endschema\s*-?%}/, '')
  .replace(/posted_successfully\?/g, 'posted_successfully');

const globalSchema = JSON.parse(read('config/settings_schema.json'));
const settings = {};
for (const g of globalSchema) for (const s of g.settings || []) if (s.id) settings[s.id] = s.default;
Object.assign(settings, JSON.parse(read('config/settings_data.json')).presets.Default);
settings.font_heading = { family: 'Caladea', fallback_families: 'Georgia, serif', weight: 400 };
settings.font_body = { family: 'Inter', fallback_families: 'Arial, sans-serif', weight: 400 };

const img = (file) => ({ src: fileUrl(path.join(MEDIA, file)), alt: '', id: file, media_type: 'image', preview_image: { src: fileUrl(path.join(MEDIA, file)) } });
const variant = (id, price) => ({ id, price, compare_at_price: null, available: true, title: 'Default Title', options: ['Default Title'] });
const wake = {
  id: 1, title: "Réveil Simulateur d'Aube Lumaube", url: '#product', price: 4990, available: true,
  has_only_default_variant: true, options_with_values: [], variants: [variant(11, 4990)],
  metafields: { lumaube: { tagline: 'Le lever de soleil, directement dans votre chambre.',
    specs: { value: "Alimentation: USB (câble fourni)\nPuissance: 3 W\nAffichage: écran avec heure\nÉclairage: aube progressive + 7 couleurs d'ambiance\nDimensions: 10,6 x 15,1 cm\nGarantie: 2 ans (garantie légale)" } } },
  description: "<p>Les matins d'hiver, il fait encore nuit quand le réveil sonne. Le réveil simulateur d'aube Lumaube allume la chambre <strong>progressivement avant l'heure choisie</strong>, comme un lever de soleil.</p>",
  media: [img('lumaube-ad-1080x1080-last.jpg'), img('lumaube-hero-1920x1080-last.jpg')],
};
wake.featured_media = wake.media[0];
wake.selected_or_first_available_variant = wake.variants[0];
const mk = (id, title, price, file, tagline) => {
  const p = { id, title, url: '#', price, available: true, has_only_default_variant: true, variants: [variant(id * 10, price)],
    metafields: { lumaube: { tagline } }, media: [img(file)] };
  p.featured_media = p.media[0]; p.selected_or_first_available_variant = p.variants[0]; return p;
};
const mask = mk(3, 'Masque de Nuit Lumaube', 1290, 'lumaube-ad-1080x1920-last.jpg', 'Le noir complet, en douceur.');
const products = [wake, mk(2, 'Masseur Électrique Cuir Chevelu', 3490, 'lumaube-hero-1920x1080-last.jpg', 'Une pause détente de 5 minutes.'), mask,
  mk(4, 'Kit Réveil Doux', 5990, 'lumaube-ad-1080x1080-last.jpg', 'Le réveil + le masque de nuit.')];

const base = {
  settings, shop: { name: 'Lumaube', description: 'Des matins plus doux.', enabled_payment_types: ['visa', 'master', 'paypal'], url: '#' },
  request: { locale: { iso_code: 'fr' }, origin: 'https://lumaube.example' },
  routes: { root_url: '#', cart_url: '#cart', search_url: '#search', all_products_collection_url: '#all', cart_add_url: '#', product_recommendations_url: '#' },
  cart: { item_count: 1, currency: { iso_code: 'EUR' } }, canonical_url: '#', content_for_header: '',
  collections: { all: { products } }, recommendations: { performed: false }, form: {},
};

// Shopify exposes these objects everywhere, including inside {% render %} snippets.
engine.options.globals = { settings, shop: base.shop, routes: base.routes, request: base.request, cart: base.cart };

async function renderSection(type, data, key, ctx) {
  const src = read(`sections/${type}.liquid`);
  const schema = schemaOf(src);
  const s = {};
  for (const st of schema.settings || []) if (st.id) s[st.id] = st.default;
  Object.assign(s, data.settings || {});
  const blocks = (data.block_order || Object.keys(data.blocks || {})).map((id) => {
    const b = data.blocks[id];
    const bs = (schema.blocks || []).find((x) => x.type === b.type) || {};
    const bset = {};
    for (const st of bs.settings || []) if (st.id) bset[st.id] = st.default;
    Object.assign(bset, b.settings || {});
    if (b.type === 'bundle' && !bset.product) bset.product = mask; // preview only
    return { id, type: b.type, settings: bset, shopify_attributes: '' };
  });
  const html = await engine.parseAndRender(stripSchema(src), { ...ctx, section: { id: key, settings: s, blocks } });
  return `<div id="shopify-section-${key}" class="shopify-section ${schema.class || ''}">${html}</div>`;
}
async function renderGroup(file, ctx) {
  const g = JSON.parse(read(`sections/${file}`));
  const parts = [];
  for (const k of g.order) parts.push(await renderSection(g.sections[k].type, g.sections[k], k, ctx));
  return parts.join('\n');
}
async function page(template, ctx, outName) {
  const t = JSON.parse(read(`templates/${template}`));
  const body = [];
  for (const k of t.order) body.push(await renderSection(t.sections[k].type, t.sections[k], k, ctx));
  let layout = read('layout/theme.liquid')
    .replace(/{%\s*sections 'header-group'\s*%}/, '%%HEADER%%')
    .replace(/{%\s*sections 'footer-group'\s*%}/, '%%FOOTER%%');
  let html = await engine.parseAndRender(layout, { ...ctx, content_for_layout: body.join('\n') });
  html = html.replace('%%HEADER%%', await renderGroup('header-group.json', ctx))
    .replace('%%FOOTER%%', await renderGroup('footer-group.json', ctx));
  fs.writeFileSync(path.join(OUT, outName), html);
  console.log('wrote', outName);
}

(async () => {
  await page('index.json', { ...base, template: { name: 'index' }, page_title: "Lumaube – Réveil simulateur d'aube", request: { ...base.request, page_type: 'index' } }, 'home.html');
  await page('product.json', { ...base, template: { name: 'product' }, page_title: wake.title, product: wake, request: { ...base.request, page_type: 'product' } }, 'product.html');
})().catch((e) => { console.error(e); process.exit(1); });
