# Lumaube – brand guide

**Name:** Lumaube (lumière + aube, "light + dawn").
**Backup name:** Aubelia.
**Rejected:** Aubéa, which is too close to the lingerie brand Aubade.

**Promise:** *Des matins plus doux, des soirées plus calmes.* Lumaube sells a few carefully chosen
objects for waking up gently and winding down in the evening: a sunrise simulator, a scalp
massager and a silk sleep mask.

**Tagline (FR):** « Réveillez-vous avec la lumière. »
**Tagline (EN):** "Wake up with the light."

## Checks done (4 Nov 2026)
- Web search: no business, shop or brand found using "Lumaube" or "Aubelia".
- Not checked here, so do these before buying the domain:
  1. Domain availability (the registrar tool was blocked in this environment). Check these in order:
     `lumaube.com`, `lumaube.shop`, `aubelia.com`.
     **No `.fr` or `.eu`:** both require the holder to live in the EU/EEA (or Switzerland), so they
     can't be registered from Morocco in your own name. `.com` works from any country.
     Avoid city names such as "paris" in the domain: the business is not based there.
     Support e-mail in the theme and legal pages: `bonjour@lumaube.com` (change it if the domain changes).
  2. Trademark search at INPI ([data.inpi.fr](https://data.inpi.fr)) and EUIPO
     ([euipo.europa.eu/eSearch](https://euipo.europa.eu/eSearch/)) for "Lumaube", classes 9, 11 and 20.

## Logo
| File | Use |
|---|---|
| `logo.svg` / `logo.png` | Main logo on light backgrounds (header, invoices) |
| `logo-white.svg` / `logo-white.png` | On dark backgrounds (footer, ads) |
| `logo-icon.svg` / `logo-icon.png` | Social avatar, app icon |
| `logo-icon-dark.svg` / `logo-icon-dark.png` | Dark avatar |
| `favicon-64.png` | Shopify favicon |

The wordmark is converted to vector paths (Caladea serif), so it renders the same everywhere.
Rebuild it with `python3 make_logo.py && node render.js`.

The icon is a sun rising over the horizon, with a peach-to-honey gradient. The horizon line sits
on the wordmark's baseline.

## Colours
| Token | Hex | Use |
|---|---|---|
| Nuit (ink) | `#1E2238` | Text, horizon line, dark sections |
| Aube (dawn) | `#F08A5D` | Primary buttons, highlights |
| Miel (honey) | `#F7C873` | Gradients, badges |
| Crème (cream) | `#FBF6EE` | Page background |
| Brume (mist) | `#E9E4F0` | Cards, alternate sections |
| Texte doux | `#4A4D63` | Secondary text |

Contrast (WCAG): ink on cream 14.6:1, ink on dawn 6.3:1, secondary text on cream 7.7:1. White on dawn is only 2.5:1, so primary buttons
use **ink text on dawn**, or cream text on ink.

## Typography
- Headings: **Lora** (Shopify font `lora_n6`), a soft and readable serif.
- Body: **Assistant** (`assistant_n4`), clean and very readable on mobile.

## Tone of voice (FR)
- Calm, warm and precise: "vous", short sentences, concrete details (lux, minutes, sons).
- No medical promises: never "soigne", "guérit", "contre la dépression" or "anti-insomnie".
  Talk about comfort, routine and wellbeing instead.
- No invented numbers, fake reviews, fake countdowns or fake "stock bas".
- Be honest about delivery: « Expédié sous 24–72 h · livré en 7 à 12 jours ouvrés · suivi inclus ».

## Photo style (Google Flow prompts are in each product file)
Warm early-morning light, bedside scenes, linen and wood textures, real hands. No text in images.
