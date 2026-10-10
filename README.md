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

## Credits and terms

Unofficial fan project, not affiliated with Ticroco. “Spam” and its contents belong to their rights holders.

Card data, icons and illustrations come from the public [SPAMDEX](https://www.spamgame.com/spamdex) and are used under its [non-commercial data terms](https://spamgame.com/conditions-donnees-cartes). Every illustration is credited to its artist on the card. Not for commercial use.

Fonts: [Bricolage Grotesque](https://fonts.google.com/specimen/Bricolage+Grotesque) and [Figtree](https://fonts.google.com/specimen/Figtree), both under the SIL Open Font License.
