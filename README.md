# Renegade Platinum Nuzlocke + Boss Prep

A static page for a Nuzlocke of **Pokémon Renegade Platinum (PChal / Kalaay QoL build)**:

- **Boss Prep**: every gym, Elite Four member, Team Galactic fight, Barry / Dawn / Lucas fight and other required fight in story order. For each one: the boss team, every Pokémon you could have by then and who wins each 1-on-1 at your level cap, your own team's coverage, and the TMs and items that opened up since the last fight.
- **Areas**: first-encounter tracker by area, with the dupes and shiny clauses.
- **Box / graveyard**, **Pokédex**, and **Save & sync** (read your `.sav` in the browser; optional sync to a private gist).

Everything runs in the browser. Open `index.html` through any static server, or GitHub Pages.

## Data

`tools/build.py` writes `data/`. It reads the patched ROM (species, learnsets, TM compatibility, evolutions, moves, trainer teams, in-game text) and the Renegade Platinum documentation workbook (trainer natures and abilities, areas, gifts, TM locations, tutors). `tools/story.py` holds the hand-written story order and when each area, method, TM and evolution item can first be reached. Neither the ROM nor the workbook is in this repo.

`node test/model.test.js` recomputes every matchup with the JavaScript model and checks it against Python's (`104420 matchups, 0 differences`).

The save reader (`js/savereader_pt.js`) follows PKHeX's Platinum code for every offset; the trainer-flag numbering comes from pret/pokeplatinum.

## Calc

`calc/` is a copy of hzla's [Dynamic Calc](https://github.com/hzla/Dynamic-Calc) (built on the Smogon/Honko damage calc, MIT) with its Renegade Platinum data (`calc/backups/rp.js`). It opens on Renegade Platinum, its large sprite folders load from the original site, and analytics are removed. Boss Prep links into it with `&opp=<trainer set>` and, from a matchup, `&me=<species>&lv=<cap>&mv=<moves>` (`calc/js/renplat_links.js`).
