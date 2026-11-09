# Nuzlocke hub

Static pages for Drayano-hack Nuzlockes, one folder per game, sharing one tracker, one calc and one private-gist sync:

| Folder | Game | What's there |
| --- | --- | --- |
| `renplat/` | Renegade Platinum (PChal QoL 1.9.2) | Boss Prep, Nuzlocke areas, box, Pokédex, Platinum save reader |
| `bb2r/` | Blaze Black 2 Redux (PChal QoL build) | Boss Prep (gyms, Elite Four, champion, Team Plasma bosses), every trainer team by split, Normal / Challenge switch, Nuzlocke areas, box, Pokédex, B2W2 save reader, enemy AI notes |
| `index.html` | Hub | Game list and the Drayano Gauntlet (Storm Silver → Renegade Platinum → Blaze Black 2 Redux): families that died or made the Hall of Fame in an earlier game are marked "Cursed" in later ones |

Everything runs in the browser. Open the repo through any static server or GitHub Pages. The old Renegade Platinum links (`/#prep`, `/#run`, …) redirect to `renplat/`.

## Shared code (`shared/`)

- `app.js`: the tracker. Each game page sets `window.GAME` (store prefix, tabs, starters, badges, calc link, save format, page text).
- `model.js`: the 1-on-1 model (JavaScript twin of `tools/*/model.py`).
- `savereader_pt.js` (Platinum, PKHeX offsets + pret/pokeplatinum trainer flags) and `savereader_b2w2.js` (Black 2 / White 2, PKHeX offsets). B2W2 fights are worked out from badges.
- Settings and runs live in `localStorage` (`rp.*`, `bb2r.*`, `hub.*`). One GitHub token (`hub.gist`) syncs every game to one private gist, one file per game.

## Data

- `tools/renplat/`: reads the patched ROM and the Renegade Platinum documentation (see the comments in `build.py`).
- `tools/bb2r/`: no ROM needed. Species, moves, learnsets and trainer sets (with IVs and AI flags) come from hzla's Dynamic-Calc-Decomps data for the PChal QoL build (`vw2qol`, file `bb2redux1-4.js`); trainer teams for both modes, locations and items from the PChal workbooks (`ex_trainers.py`); story order and gates in `story_bb2r.py`; save-reader names in `ids_bb2r.py` (PKHeX text + growth rates).
- Level caps: each split's leader ace (Ghetsis's ace for the Plasma split, Iris's for the League), per mode.

## Tests

- `node test/model.test.js`: recomputes every matchup in both games with the JavaScript model and checks it against Python's (`181295 matchups, 0 differences`).
- `node test/b2w2.test.js`: builds a made-up B2W2 save and checks the reader gets everything back; `node test/b2w2.test.js my.sav` prints what's in a real save.
- `node test/save.test.js my.sav`: prints what's in a Platinum save.

## Calc

`calc/` is a copy of hzla's [Dynamic Calc](https://github.com/hzla/Dynamic-Calc) (built on the Smogon/Honko damage calc, MIT) with the Renegade Platinum data (`backups/rp.js`) and the PChal BB2 Redux data (`backups/bb2redux1-4.js`, from Dynamic-Calc-Decomps). Analytics are removed, sprites load from the original site. Boss Prep and the Trainers page link into it with `&opp=<trainer set>&olv=<level>` and, from a matchup, `&me=<species>&lv=<cap>&mv=<moves>` (`calc/js/renplat_links.js`). `olv` sets Challenge Mode levels, which the calc's sets don't have.
