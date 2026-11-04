# Lumaube media

## Videos (made here, free to use)
| File | Size | Use |
|---|---|---|
| `lumaube-hero-1920x1080.mp4` | 8 s, no text | Home page hero banner. Upload it in Shopify → Contenu › Fichiers, then pick it in *Bannière principale › Vidéo*. You can also add it as product media on the wake-up light. |
| `lumaube-ad-1080x1920.mp4` | 9 s, vertical | Instagram/Facebook Reels, TikTok, YouTube Shorts |
| `lumaube-ad-1080x1080.mp4` | 9 s, square | Facebook/Instagram feed, Google Demand Gen |
| `*-last.jpg` | last frame | Video thumbnails / posters |

The animation is code (`anim/sunrise.html` + `anim/record.js`): night with "6:30", then the Lumaube sun
rising, the sky turning peach and honey, the headline and the logo. To change the text, edit
`HEAD`/`SUB` in `sunrise.html` and run:
```
cd store-content/media/anim && NODE_PATH=$(npm root -g) node record.js
```

> These are **brand animations**: they don't show the product itself. For the product page, also
> film the real sample (UGC scripts in `../products.md`). Google and EU consumer law require product
> images to show the real product.

## Product lifestyle images (ElevenLabs, generated 4 Nov 2026)
Both images were made from the **real supplier photos** (CJ) with the instruction to keep the product
identical. They are saved in your ElevenLabs workspace, in the flow **"Lumaube – visuels produits"**:
https://elevenlabs.io/app/flows/f4B6mljWQqrzOb6ZbWmW

| Image | Contents | Generation |
|---|---|---|
| Wake-up light at dawn | The supplier's wake-up light on an oak bedside table, warm glow, linen bedding, blue dawn window | `OdF4ZNT561Qz6gMalGoA` |
| Scalp massager, evening | The white 8-claw massager on a linen towel, candle, eucalyptus | `q9qKZgZnlbAnAGlGqmtq` |

To use them: open the flow, download each image at full size, check that the product still matches
the supplier photo exactly (shape, buttons, display), then upload as the 2nd or 3rd product image
(keep a clean product photo first). The format is 16:9, so crop to 1:1 for product pages.

ElevenLabs **video** generation needs a paid ElevenLabs plan. With one, animate the wake-up light
image with this prompt: "Slow push-in; the lamp's glow rises from dim amber to warm golden light like
a sunrise; room slowly fills with light; maintain exact product appearance, no text."
