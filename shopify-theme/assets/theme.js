/* Lumaube theme – small, dependency-free behaviours. */
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const cfg = window.theme || {};

  /* Mobile navigation */
  const toggle = $('[data-nav-toggle]');
  const nav = $('#MobileNav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  /* Money formatting in the shop currency */
  const currency = (window.Shopify && Shopify.currency && Shopify.currency.active) || 'EUR';
  const money = (cents) => new Intl.NumberFormat(cfg.locale || 'fr', { style: 'currency', currency }).format(cents / 100);

  /* Delivery estimate: today + dispatch + transit, counted in business days (Mon–Fri) */
  const addBusinessDays = (date, days) => {
    const d = new Date(date);
    let added = 0;
    while (added < days) {
      d.setDate(d.getDate() + 1);
      const day = d.getDay();
      if (day !== 0 && day !== 6) added += 1;
    }
    return d;
  };
  const fmtDate = (d) => d.toLocaleDateString(cfg.locale || 'fr', { weekday: 'short', day: 'numeric', month: 'long' });
  $$('[data-delivery-range]').forEach((el) => {
    const dl = cfg.delivery;
    if (!dl) return;
    const start = addBusinessDays(new Date(), dl.min + 1);
    const end = addBusinessDays(new Date(), dl.max + dl.dispatchMax);
    el.textContent = `${fmtDate(start)} – ${fmtDate(end)}`;
  });

  /* Gallery thumbnails */
  $$('[data-gallery]').forEach((gallery) => {
    $$('[data-thumb]', gallery).forEach((thumb) => {
      thumb.addEventListener('click', () => {
        const id = thumb.dataset.thumb;
        $$('.gallery__slide', gallery).forEach((s) => s.classList.toggle('is-active', s.dataset.mediaId === id));
        $$('[data-thumb]', gallery).forEach((t) => t.classList.toggle('is-active', t === thumb));
      });
    });
  });

  /* Quantity buttons */
  $$('[data-qty]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const input = btn.parentElement.querySelector('input');
      const next = Math.max(1, Math.min(10, (parseInt(input.value, 10) || 1) + Number(btn.dataset.qty)));
      input.value = next;
    });
  });

  /* Cart helpers */
  const toast = $('#CartToast');
  const showToast = () => {
    if (!toast) return;
    toast.hidden = false;
    clearTimeout(showToast.t);
    showToast.t = setTimeout(() => { toast.hidden = true; }, 3500);
  };
  const refreshCount = async () => {
    try {
      const res = await fetch(cfg.routes.cartJs, { headers: { Accept: 'application/json' } });
      const cart = await res.json();
      $$('[data-cart-count]').forEach((el) => { el.textContent = cart.item_count; el.hidden = cart.item_count === 0; });
    } catch (e) { /* non-blocking */ }
  };
  const addToCart = async (body) => {
    const res = await fetch(`${cfg.routes.cartAdd}.js`, { method: 'POST', headers: { Accept: 'application/json' }, body });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.description || err.message || 'Erreur');
    }
    await refreshCount();
    showToast();
  };

  /* Product form: variants + AJAX add */
  $$('[data-product]').forEach((section) => {
    const form = $('[data-product-form]', section);
    if (!form) return;
    const idInput = $('[data-variant-id]', form);
    const addBtn = $('[data-add-button]', form);
    const errorEl = $('[data-form-error]', form);
    const variantsJson = $('[data-variants]', section);
    const variants = variantsJson ? JSON.parse(variantsJson.textContent) : [];

    const onOptionChange = () => {
      const selected = $$('[data-option]:checked', section).map((i) => i.value);
      const variant = variants.find((v) => v.options.every((o, i) => o === selected[i]));
      if (!variant) return;
      idInput.value = variant.id;
      addBtn.disabled = !variant.available;
      $$('[data-price] .price__current').forEach((el) => { el.textContent = money(variant.price); });
      if (variant.featured_media) {
        const id = String(variant.featured_media.id);
        $$('.gallery__slide', section).forEach((s) => s.classList.toggle('is-active', s.dataset.mediaId === id));
      }
      const url = new URL(window.location.href);
      url.searchParams.set('variant', variant.id);
      window.history.replaceState({}, '', url);
    };
    $$('[data-option]', section).forEach((input) => input.addEventListener('change', onOptionChange));

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      errorEl.hidden = true;
      addBtn.disabled = true;
      try {
        await addToCart(new FormData(form));
      } catch (e) {
        errorEl.textContent = e.message;
        errorEl.hidden = false;
      } finally {
        addBtn.disabled = false;
      }
    });

    /* Sticky add-to-cart bar when the main button scrolls out of view */
    const sticky = $('[data-sticky-buy]');
    if (sticky && 'IntersectionObserver' in window) {
      new IntersectionObserver(([entry]) => { sticky.hidden = entry.isIntersecting || entry.boundingClientRect.top > 0; })
        .observe(addBtn);
    }
  });

  /* Quick add (bundle block) */
  $$('[data-quick-add]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      btn.disabled = true;
      const body = new FormData();
      body.append('id', btn.dataset.quickAdd);
      body.append('quantity', '1');
      try { await addToCart(body); } catch (e) { alert(e.message); } finally { btn.disabled = false; }
    });
  });

  /* Product recommendations (loaded after page render) */
  $$('[data-recommendations]').forEach(async (el) => {
    if (el.children.length) return;
    try {
      const res = await fetch(el.dataset.url);
      const html = await res.text();
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const fresh = doc.querySelector('[data-recommendations]');
      if (fresh && fresh.innerHTML.trim()) el.innerHTML = fresh.innerHTML;
    } catch (e) { /* ignore */ }
  });
})();
