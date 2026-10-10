# SPAM Card Browser

An unofficial card pool explorer for the card game **SPAM**, made by [waldh4ri](https://github.com/waldh4ri) to find the right cards for a build.

**Open it:** https://waldh4ri.github.io/spam-card-browser/

## Features

- Full-text search over card names, abilities, Tox, talents and keywords. Accents are ignored, `"quotes"` match a phrase and `-word` excludes.
- Filters for card element, rarity, minimum Spamtons and HP, damage and healing elements, boost types (elemental bonus, resistance, critical, accuracy…), and Tox, including Tox granted by talents.
- Card view and gallery view, with a detail panel (resistances, keyword glossary, lore) you can step through with ← →.
- Squad dock: pin up to 4 cards and see their combined HP, Spamtons and element coverage.
- English and French, light and dark themes.
- One self-contained HTML file: card art, icons and fonts are embedded, so it also works offline.

## Rebuilding after a game patch

Requires Python 3 and Pillow (`pip install pillow`).

```sh
python fetch_data.py      # downloads the latest SPAMDEX data, art and icons
python build_browser.py   # writes index.html
```

`template.html` holds the page design; `build_browser.py` merges the card data, embeds the images and fonts, and writes `index.html`.

## How this follows the SPAMDEX data terms

The data is published by Ticroco at https://spamgame.com/data/ under the [conditions d'utilisation des données de cartes](https://spamgame.com/conditions-donnees-cartes) (last updated 18 September 2026). This project is a free, non-commercial fan tool, which is the use those terms allow. How each condition is met:

| Condition | How |
|---|---|
| Credit the artist of every illustration, with a link when one is provided | Each illustration (card, gallery tile, detail panel, full-size viewer) carries the artist's name and link from the `artwork.artist` field of the data. |
| State that the project is not official | Every page ends with the notice, in English and French, and the README says it too. |
| No commercial use | Free, no ads, no tracking, no paywall, no donations. |
| Don't mislead | Art is only resized and cropped to fit (`fit: cover`, as the published layout does); the full illustration is one click away. It is never presented as the author's own, and the game's logo is not used. The project name and header mark are original. |
| Data provided as is, format may change | `fetch_data.py` reads `index.json`, uses its `latest` version and `cards` path template, and stops with a clear message if the `schema` number is not the supported one. |
| Removal on request | See below. |

Data is fetched from the documented endpoint with a descriptive User-Agent, conditional requests (`If-None-Match`) for the JSON, and no repeat image downloads.

### Removal requests

If Ticroco or an artist asks for an illustration to be withdrawn, add the card's slug (for example `esprit_feu`) on its own line in `exclude.txt`, then run `python build_browser.py` and publish the new `index.html`. That card is shown without art and without the viewer. Questions about the data terms go to support@spamgame.com. For this project, open an issue.

## Credits and terms

Unofficial fan project, not affiliated with Ticroco. “Spam” and its contents belong to their rights holders.

Card data, icons and illustrations come from the public [SPAMDEX](https://www.spamgame.com/spamdex) and are used under its [non-commercial data terms](https://spamgame.com/conditions-donnees-cartes). Every illustration is credited to its artist on the card. Not for commercial use.

Fonts: [Bricolage Grotesque](https://fonts.google.com/specimen/Bricolage+Grotesque) and [Figtree](https://fonts.google.com/specimen/Figtree), both under the SIL Open Font License.
