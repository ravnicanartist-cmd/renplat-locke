// ROM (Gen 4 spelling) -> Pokémon Showdown names, so the site, the tooltips and the calc agree
const { Dex } = require("/home/claude/pkmn/node_modules/@pkmn/dex");
const t = require("/home/claude/sg/romtext.json"), d = Dex.forGen(4), late = Dex.forGen(9);
const fix = (kind, n) => { if (!n) return n; let x = d[kind].get(n); if (!x.exists) x = late[kind].get(n); return x.exists ? x.name : n; };
const out = { species: t.species.map((n, i) => i === 0 || i > 493 ? n : fix("species", n.replace("♀", "-F").replace("♂", "-M"))),
  moves: t.moves.map(n => fix("moves", n)), abilities: t.abilities.map(n => fix("abilities", n)), items: t.items.map(n => fix("items", n)) };
const miss = k => out[k].filter((n, i) => i && n === t[k][i] && !d[k === "species" ? "species" : k].get(n).exists).slice(0, 20);
console.log("unmatched moves", miss("moves"), "abilities", miss("abilities"), "species", miss("species"));
require("fs").writeFileSync("/home/claude/sg/names.json", JSON.stringify(out));
console.log(out.moves.slice(1, 12), out.species.slice(29, 33), out.items.slice(80, 90));
