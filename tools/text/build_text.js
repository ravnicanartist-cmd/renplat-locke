// Ability and move tooltips for each game -> <game>/data/text.json
// Effects: Pokémon Showdown's descriptions (@pkmn/dex) for the game's generation; type / power / accuracy / PP: the hack's own data;
// "changed in this hack" notes: the hack's documentation (src_<game>.json, made by src.py).
const fs = require("fs"), path = require("path");
const { Dex } = require("/home/claude/pkmn/node_modules/@pkmn/dex");
const HUB = "/home/claude/hub";
const GAMES = [["renplat", 4, "src_rp.json"], ["bb2r", 5, "src_bb2r.json"], ["sg", 4, "src_sg.json"]];
const NAME = { "Compoundeyes": "Compound Eyes", "Lightningrod": "Lightning Rod" };
for (const [g, gen, src] of GAMES) {
  const D = path.join(HUB, g, "data"), meta = JSON.parse(fs.readFileSync(path.join(D, "meta.json")));
  const S = JSON.parse(fs.readFileSync(path.join("/home/claude/text", src)));
  const dex = Dex.forGen(gen), late = Dex.forGen(9);
  const abil = new Set();
  Object.values(meta.mons).forEach(m => m.ab.forEach(a => abil.add(a)));
  const tr = JSON.parse(fs.readFileSync(path.join(D, "trainers.json")));
  Object.values(tr).forEach(mode => mode.forEach(sp => sp.trainers.forEach(t => t.team.forEach(m => abil.add(m.a)))));
  const fightsDir = path.join(D, "fights");
  const walk = d => fs.readdirSync(d, { withFileTypes: true }).forEach(e => e.isDirectory() ? walk(path.join(d, e.name))
    : JSON.parse(fs.readFileSync(path.join(d, e.name))).team.forEach(m => abil.add(m.a)));
  walk(fightsDir);
  const out = { ab: {}, mv: {}, general: S.general }, missing = [];
  for (const a of abil) {
    if (!a) continue;
    let x = dex.abilities.get(NAME[a] || a);
    if (!x.exists || x.isNonstandard) x = late.abilities.get(NAME[a] || a);
    if (!x.exists) { missing.push("ability " + a); continue; }
    out.ab[a] = x.shortDesc || x.desc;
  }
  for (const [n, v] of Object.entries(meta.moves)) {
    const [t, c, bp] = v, s = S.moves[n] || {};
    let x = dex.moves.get(n), orig = x.exists && !x.isNonstandard ? x : null;
    if (!orig) x = late.moves.get(n);
    if (!x.exists) missing.push("move " + n);
    const notes = [];
    if (S.notes[n]) notes.push(S.notes[n]);
    if (orig && orig.type !== t && !/Type/.test(S.notes[n] || "")) notes.push(`Type: ${orig.type} → ${t}`);
    if (!orig && x.exists) notes.push(`Not in the original Gen ${gen} games (added by this hack)`);
    out.mv[n] = [s.acc === true || s.acc == null || s.acc === 0 || s.acc === 101 ? "—" : s.acc, s.pp ?? "", x.exists ? x.shortDesc : "", notes.join("; ")];
  }
  fs.writeFileSync(path.join(D, "text.json"), JSON.stringify(out));
  console.log(g, Object.keys(out.ab).length, "abilities", Object.keys(out.mv).length, "moves", "missing:", missing.slice(0, 20));
}
