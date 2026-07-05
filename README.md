# 🌞 Nyári Tanoda 2026 — Anna és Lotti

Napi oktatási munkalapok **2026. július 6-tól augusztus 31-ig** (57 nap), két gyerekre szabva:

| | Anna | Lotti |
|---|---|---|
| Született | 2018 ősz (7,5 éves) | 2021 ősz (4,5 éves) |
| Szint | 2. osztályba készül | óvodás (középső csoport) |
| Napi idő | kb. 25–35 perc | kb. 15–20 perc, szülővel |
| Fájlok | `pdf/anna/` — 57 PDF | `pdf/lotti/` — 57 PDF |

Minden munkalap **egyoldalas**, kinyomtatható A4-es PDF, és a végén
**★ HOLNAPI KALAND ★** kedvcsinálóval zárul, hogy a gyerekek várják a másnapi tanulást.

## 📅 Heti témák (mindkét gyereknél közös)

| Hét | Dátum | Téma |
|---|---|---|
| 1. | júl. 6–12. | 🐶 Háziállatok és a nyár |
| 2. | júl. 13–19. | 🦊 Az erdő állatai |
| 3. | júl. 20–26. | 🐸 Vízpart és vízi állatok |
| 4. | júl. 27–aug. 2. | 🍎 A testünk és az egészség |
| 5. | aug. 3–9. | 🌻 Növények és a kert |
| 6. | aug. 10–16. | 🌦️ Időjárás és évszakok |
| 7. | aug. 17–23. | 🚗 Közlekedés |
| 8. | aug. 24–30. | 🚀 A világűr és a Föld |
| 9. | aug. 31. | 🎒 Irány az iskola és az ovi! – nagy ismétlés |

## 📚 Anna tanterve (napi 6 blokk)

1. **Naptár-bemelegítő** – hét napjai, hónapok, évszakok, dátumírás (minden nap)
2. **Nyelvtan** – heti progresszió: ábécé és magánhangzók → rövid/hosszú hangok →
   szótagolás → elválasztás → mondat és írásjelek → mondatfajták → j/ly →
   ellentétek, rokon értelmű szavak → nagy ismétlés
3. **Matematika** – összeadás/kivonás 20-ig → számolás 100-ig → tízesátlépés →
   pótlás → **szorzás bevezetése (2, 5, 10)** → vegyes műveletek; minden nap
   témához illő szöveges feladattal
4. **Óraolvasás** – rajzolt óralapokkal: egész → fél → negyed/háromnegyed →
   percek 5-ösével → digitális-analóg; a hét második felétől a gyerek rajzol mutatót
5. **Angol** – heti tematikus szókincs (4 szó/nap), heti 8 új szó
6. **Környezetismeret** – a heti témához illő kérdés, megfigyelés vagy kis kísérlet

## 🧸 Lotti tanterve (napi 7 játékos blokk)

1. **Köszöntő** – nap neve, időjárás-megfigyelés
2. **A nap száma (1–10)** – megszámolható alakzatokkal, ujjszámolással
3. **Forma és szín** – kör/négyzet/háromszög/csillag/szív + színkeresés a lakásban
4. **Betűvarázs** – hangfelismerés, nagy betű átrajzolása
5. **Angol szavacskák** – napi 2 szó a heti témából
6. **A nap figurája** – állat/figura utánzás, rajz, mesélés
7. **Mondóka és ügyes kezek** – népi mondókák + vonalvezető finommotorikás gyakorlat

Hétvégén mindkét gyereknél könnyített, játékosabb adag (családi feladatokkal).

## 🖨️ Használat

1. Nyomtasd ki az aznapi lapot a `pdf/anna/` és `pdf/lotti/` mappából
   (a fájlnév mutatja a napot: `nap01_2026-07-06_hetfo.pdf`).
2. Anna nagyrészt önállóan dolgozhat, Lottival közösen játsszatok.
3. A nap végén olvassátok fel együtt a **Holnapi kalandot**!

## ⚙️ Újragenerálás / testreszabás

```bash
pip install reportlab
cd generator
python3 generate.py
```

A tananyag a `generator/data.py`-ban szerkeszthető (témák, szavak, feladatok),
a nehézségi progresszió a `generator/generate.py`-ban.

## ⬆️ Feltöltés GitHubra

```bash
# a repó gyökerében:
git remote add origin https://github.com/FELHASZNALONEV/nyari-tanoda-2026.git
git push -u origin main
```

(Előtte hozz létre egy üres `nyari-tanoda-2026` repót a GitHubon.)
