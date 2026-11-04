# Lumaube – product content (copy into Shopify)

Each product below has:
- the Shopify fields (title, URL handle, price, description, SEO);
- metafields: `lumaube.tagline` (single line text) and `lumaube.specs` (multi-line text, one
  "Name: value" per line);
- Google Merchant Center attributes;
- 4 Google Flow image prompts and 3 UGC scripts.

> ⚠️ **Before publishing:** order 1 sample of each product. Delete every sentence and spec the sample
> doesn't really do, and fill in the `[à confirmer]` values. Never add health claims.

---

## 1. Réveil simulateur d'aube (hero product)

**Supplier (CJ):** "Alarm Clock Wake-up Light Simulation Natural Sunrise Bedside Lamp", pid
`2412210731061625500`, variant **"3W With Time"**, cost $14.76, about 463 g, shipped China → France in
7–11 days for about $8.30. Landed cost is about **€21**.
- **Alternatives:** CJ pid `1674978644902551552` (sold by 17,087 CJ stores, $19.35) or pid
  `1386982812787281920` ("…Sunset Sleep Aid", $16.86).
- **Best option:** an AliExpress Choice listing that explicitly states FM radio, nature sounds and a
  sunset mode.

- **Template:** `product` (default)
- **Title:** Réveil Simulateur d'Aube Lumaube
- **Handle:** `reveil-simulateur-d-aube`
- **Price:** 49,90 €. Compare-at: **leave empty** (no fake discount).
- **Tagline (metafield):** Le lever de soleil, directement dans votre chambre.
- **SEO title:** Réveil Simulateur d'Aube – Réveil lumineux en douceur | Lumaube
- **SEO description:** Réveil simulateur d'aube : la lumière augmente progressivement avant l'alarme. Livraison offerte, suivi inclus, satisfait ou remboursé 30 jours.

**Description (HTML):**
```html
<p>Les matins d'hiver, il fait encore nuit quand le réveil sonne. Le réveil simulateur d'aube Lumaube allume la chambre <strong>progressivement avant l'heure choisie</strong>, comme un lever de soleil, pour un réveil plus doux qu'une sonnerie soudaine.</p>
<h3>Ce que vous allez aimer</h3>
<ul>
  <li><strong>Une aube progressive</strong> : la lumière passe d'une teinte chaude et douce à une lumière plus vive. [durée réglable : à confirmer, ex. 10 à 60 min]</li>
  <li><strong>Un réveil sonore doux</strong> : [sons naturels / radio FM : à confirmer selon le modèle]</li>
  <li><strong>Une lampe de chevet</strong> au quotidien, avec plusieurs couleurs d'ambiance.</li>
  <li><strong>Simple à installer</strong> : alimentation par câble USB.</li>
</ul>
<h3>Pour qui ?</h3>
<p>Pour celles et ceux qui ont du mal avec les réveils brutaux, les matins sombres d'hiver, ou qui cherchent un cadeau utile et original.</p>
<p><em>Ce produit n'est pas un dispositif médical.</em></p>
```

**Specs (metafield `lumaube.specs`):**
```
Alimentation: USB (câble fourni)
Puissance: 3 W
Affichage: écran avec heure
Éclairage: aube progressive + 7 couleurs d'ambiance
Durée de l'aube: [à confirmer]
Sons / radio: [à confirmer]
Dimensions: 10,6 x 15,1 cm
Matière: plastique
Contenu: 1 réveil, 1 câble USB
Garantie: 2 ans (garantie légale de conformité)
```

**Google Merchant Center:**
| Attribute | Value |
|---|---|
| google_product_category | Home & Garden > Decor > Clocks > Alarm Clocks (id 3696) |
| brand | Lumaube |
| identifier_exists | no (no GTIN) |
| condition | new |
| shipping | FR, 0 €, handling 1–3 days, transit 7–12 days |
| custom_label_0 | hero |

**Google Flow image prompts:**
1. *In use:* "A person waking up peacefully in a cozy French bedroom at dawn, a round bedside sunrise alarm lamp glowing warm orange on the nightstand, soft morning light, linen bedding, photorealistic, 35mm, shallow depth of field, no text, no logos."
2. *In hand:* "Close-up of a hand holding a compact round sunrise alarm clock lamp emitting warm amber light, neutral cream background softly blurred, true scale visible, soft window light, photorealistic, no text."
3. *Flat lay:* "Top-down flat lay of a sunrise alarm clock lamp on a light linen surface with a book, a cup of tea, a sleep mask and dried flowers, generous negative space, warm morning tones, photorealistic, no text."
4. *Macro:* "Macro detail of the diffuser surface of a sunrise lamp glowing from deep orange to warm white, gentle gradient, crisp focus on texture, dark background, photorealistic, no text."

**UGC scripts (film the real sample; no fake reviews or claims):**
1. **"Le matin d'hiver"** (20–30 s)
   - **Hook:** "6 h 30, il fait nuit noire… regardez ma chambre."
   - **Problem:** your old alarm going off in the dark.
   - **Demo:** a time-lapse of the room lighting up, then the alarm sound.
   - **CTA:** « Le lien est sur la page si vous voulez voir les détails. »
2. **"3 choses que j'ai remarquées"** (30 s)
   - **Setup:** set the time, the brightness, and the night-light mode.
   - **Include one honest limitation** (for example size or brightness).
   - **CTA** to the page.
3. **"Idée cadeau"** (15 s)
   - **Shots:** unboxing, then the light switching on.
   - **Voiceover:** « Un cadeau utile pour quelqu'un qui déteste les réveils. »
   - **Disclosure:** add #ad if the creator is paid or gifted.

---

## 2. Masseur électrique pour cuir chevelu

**Supplier (CJ):** "Head Massager Scalp Vibration Massage Eight Claw…", pid `1387972416516526080`,
white, cost $4.12, 181 g. Shipping China → FR 7–11 days costs $6.28, so the landed cost is about
**€9.60**.
- ⚠️ The supplier text claims "promotes hair growth / stress relief". **Do not copy it.**

- **Template:** `product.massager`
- **Title:** Masseur Électrique Cuir Chevelu Lumaube
- **Handle:** `masseur-cuir-chevelu-electrique`
- **Price:** 34,90 €. Compare-at: empty.
- **Tagline:** Une pause détente de 5 minutes, le soir.
- **SEO title:** Masseur Cuir Chevelu Électrique – Rechargeable, 8 griffes | Lumaube
- **SEO description:** Masseur électrique pour le cuir chevelu, 8 griffes souples, vibration douce, rechargeable USB. Livraison offerte, retours 30 jours.

**Description (HTML):**
```html
<p>Huit griffes souples, une vibration douce, et quelques minutes pour soi : le masseur Lumaube est fait pour décrocher après la journée.</p>
<ul>
  <li><strong>8 griffes souples</strong> qui épousent la forme de la tête</li>
  <li><strong>Vibration douce</strong>, à utiliser sur cheveux secs</li>
  <li><strong>Rechargeable par USB</strong>, sans fil, facile à emporter</li>
</ul>
<p>Utilisation : 5 à 10 minutes, en mouvements lents. Appareil de bien-être, pas un traitement.</p>
```
**Specs:**
```
Alimentation: batterie rechargeable USB [autonomie à confirmer]
Têtes: 8 griffes souples
Fonction: vibration
Couleur: blanc
Poids: environ 160 g
Contenu: 1 masseur, 1 câble USB
```
**Merchant Center:** google_product_category is Health & Beauty > Personal Care > Massage & Relaxation >
Massagers (id 5537); brand Lumaube; identifier_exists no.

**Google Flow prompts:**
1. "Person relaxing on a sofa in the evening using a white handheld eight-claw scalp massager, warm lamp light, cosy living room, photorealistic, no text."
2. "Hand holding a white eight-claw scalp massager, soft cream background, natural light, photorealistic, no text."
3. "Flat lay: scalp massager, candle, folded towel, eucalyptus sprig on beige linen, top-down, photorealistic, no text."
4. "Macro of the soft rounded claw tips of a scalp massager, studio light, photorealistic, no text."

**UGC hooks:**
1. « Le truc que je prends dès que je rentre du travail. »
2. « Je l'ai offert à ma mère, voici sa réaction. » Film it for real, with consent.
3. « 3 choses à savoir avant d'acheter un masseur cuir chevelu. »

---

## 3. Masque de nuit (add-on and gift)

**Supplier (CJ):** "Silk Sleep Natural Sleeping Eye Mask…", pid `1409072177503932416`, colour Black or
Grey, cost $1.95. With shipping (about $4.14) the landed cost is about **€5.60**.
- **Material is not confirmed.** Don't use the word "soie" until the supplier confirms it.

- **Title:** Masque de Nuit Lumaube · **Handle:** `masque-de-nuit` · **Price:** 12,90 €
- **Description:** « Un masque doux et léger pour faire le noir complet, en voyage comme à la maison. » Add the confirmed material and dimensions.
- **Use:** add-on in the cart, and free gift in the kit.

---

## 4. Kit "Réveil doux" (bundle)

- **What it is:** wake-up light + sleep mask for **59,90 €** (saves 2,90 € compared with buying them separately).
- **How to build it:** with the free **Shopify Bundles** app, so the order passes both items to
  fulfilment. Check that your CJ/DSers app maps bundle components correctly before advertising it.
- **Handle:** `kit-reveil-doux`
