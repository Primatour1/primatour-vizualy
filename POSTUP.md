# Primatour – príprava príspevkov na sociálne siete (postup pre automat)

Tento repozitár je verejný hosting vizuálov a fotiek pre GoHighLevel. Nič sa odtiaľto
nezverejňuje – každý príspevok ide do GHL Social Planner ako **čakajúci na schválenie**.

## Pevné pravidlá (od Martina)
- Nikdy nič nezverejniť. Stav vždy `in_review`, schvaľovateľ **Martina** (`0xUTyWp2W9euVd1eYLX7`);
  Klaudia (`HRvKvjpMQ1QIrN32c3hh`) len keď Martin povie, že zastupuje.
- Nikdy neporovnávať s „katalógovou/pôvodnou“ cenou. Len cena z ponuky („od X €“).
- Odporúčať len overené hotely. Hodnotenie nájdi (HolidayCheck, TripAdvisor, Google, primatour.sk –
  stránka hotela ukazuje % spokojnosti). Slabý hotel = buď nedávať, alebo napísať otvorene prečo (cena).
- Čísla v texte musia byť pravdivé (počet ponúk = skutočný počet v archíve za dané obdobie).
- Každý text musí obsahovať len fakty z ponuky a z hodnotení. Žiadne „dobrá kuchyňa“, „pláž pri hoteli“
  bez zdroja. Vzdialenosť pláže uviesť otvorene, ak je známa.
- Tón: formálny, ale priateľský, poradenský. Vzory: Claude Docs „Vzory príspevkov Primatour“.
- Prednosť majú odlety z Bratislavy (BTS) a Košíc (KSC).
- Mimo sezóny je menej ponúk v poriadku – radšej 1 dobrý príspevok ako 3 slabé. Žiadna ponuka = žiadny príspevok,
  len krátka správa.

## Zdroje
- Archív newslettrov CK: `G:\Môj disk\Newslettre-CK\ponuky\` (prístup cez pripojený počítač ptserver).
  Súbory `YYYYMMDD_HHMM_ck_predmet.txt` s hlavičkou X-CK/X-Predmet/X-Datum/X-Ceny-EUR; `digest_YYYY-MM-DD.json`.
- Fotky hotelov: zapísať požiadavku do `poziadavky/<datum>_<slug>.txt` (obsah: `Názov hotela | 10`),
  commit + push → GitHub Actions do ~1 min stiahne 10 fotiek z primatour.sk do `hotely/<id>-<slug>/01..10.jpg`
  a `info.json` (hviezdy, lokalita). Potom `git pull`. Fotky sú od CK cez Cesys (web Primatour).
  Verejná adresa: `https://raw.githubusercontent.com/Primatour1/primatour-vizualy/main/<cesta>`.
- Ak hotel na webe nie je (`poziadavky/hotovo/*.json` má `chyba`), príspevok ide len s vizuálom.

## Výber fotiek (reklama musí byť pekná)
Pozri si kontaktný hárok (`python -c` + PIL) a vyber 3:
1. „wow“ – more / pláž / bazén s výhľadom, obloha a voda;
2. kde si človek predstaví seba – izba s výhľadom, terasa, reštaurácia pri mori;
3. atmosféra – večer, bar, západ slnka.
Vynechaj: prázdne izby zo dverí, lobby, recepciu, parkoviská, konferenčné sály, fitness, fotky s textom
alebo logom, rendery, tmavé a rozmazané. Menej ako 2 dobré → len vizuál a napíš to do poznámky.

## Vizuály
`sablony/ticha_ponuka.html` (jeden hotel, bez fotky), `sablony/karusel_uvod.html` (1. slajd karuselu),
`sablony/karusel_slajd.html` (hotel s fotkou). Placeholdery `{{...}}`; render:
`python sablony/render.py sablony/<sablona>.html data.json vystup.png` (1080×1350, Playwright).
Výstupy ukladaj do `YYYY/MM/<slug>.png`, commit + push, použi raw URL.
Farby: #FFBD07 (zlatá), #1C1D1C, #393B3A, #F3EBDD, #E8DCC8. Písma Cormorant Garamond + Manrope.

## GoHighLevel (location 87mVlUeBL0GTPJJBqjo8)
- Facebook: `6a746bfebd6fb62c7c2ca704_87mVlUeBL0GTPJJBqjo8_861612130702690_page`
- Instagram: `6a74659f839a355cd3bb0dc2_87mVlUeBL0GTPJJBqjo8_17841446068589293`
- Jeden požiadavka = jedna platforma (FB plná verzia s adresou; IG kratšia + hashtagy, max 30).
- `create-post`: type `post`, userId/createdBy `mAfmolGUhKm95zKlOAt9`, status `in_review`,
  scheduleDate v UTC (Bratislava −2 h v lete, −1 h v zime), media `[{url, type image/png|image/jpeg, altText}]`
  (1. vizuál, 2.–4. fotky hotela), `facebookPostDetails`/`instagramPostDetails` `{type: post}`,
  `postApprovalDetails {approver, approvalStatus: pending, requesterNote}`.
- requesterNote (pre Martinu): zdroj (CK, dátum newslettra), parametre, overenie hotela (odkiaľ hodnotenie),
  odkiaľ sú fotky, na čo si dať pozor, prečo tento hotel. Stručne, po slovensky.
- Čas zverejnenia: denné príspevky nasledujúci pracovný deň 18:00; karusel sobota 10:00.

## Rytmus
- Denný výber (po–pia 8:20 a 15:20): newslettre za posledných 24 h → max 1–2 najlepšie ponuky → šablóna
  „Tichá ponuka“ (alebo iná z Vzorov) → FB + IG do GHL.
- Stredajší karusel (st 7:10): newslettre za 7 dní → 3–5 overených hotelov → úvodný slajd + slajd na hotel
  (s fotkou) → jeden FB a jeden IG príspevok s 4–6 obrázkami. Pravdivý počet ponúk v texte.
