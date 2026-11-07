// node test/save.test.js <file.sav> : prints what the reader finds
const fs = require("fs"), path = require("path");
const ids = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/ids.json")));
const meta = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/meta.json")));
const R = require("../js/savereader_pt.js");
const s = R.readSave(fs.readFileSync(process.argv[2]), ids, meta);
console.log(JSON.stringify({ ...s, boxes: s.boxes.length + " in boxes", caught: s.caught.length + " caught" }, null, 1));
for (const m of s.party.concat(s.boxes)) console.log(m.where, m.name, "Lv" + m.level, m.nature, m.ability, m.item, m.moves.join("/"), "IV", Object.values(m.ivs).join("/"), m.met, m.shiny ? "SHINY" : "");
