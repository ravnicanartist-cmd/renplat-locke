// node test/sgx.test.js <SoulGold .sav> : reads a real SoulGold save with shared/savereader_sgx.js and prints what it found
const fs = require("fs"), path = require("path");
const f = process.argv[2] || process.env.SAV;
if (!f || !fs.existsSync(f)) { console.log("no save given: skipped"); process.exit(0); }
const R = require("../shared/savereader_sgx.js");
const ids = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "soulgold", "data", "ids.json")));
const b = fs.readFileSync(f), s = R.readSave(b.buffer.slice(b.byteOffset, b.byteOffset + b.length), ids);
const bad = s.party.concat(s.boxes).filter(m => !m.name || !m.met || m.moves.some(x => x.startsWith("#")) || m.level < 1 || m.level > 100);
console.log(`${s.name} (${s.gender}), ${s.badges.length} badges, ${s.mode}, starter ${s.starterMon}; party ${s.party.length}, PC ${s.boxes.length}, caught ${s.caught.length}`);
s.party.concat(s.boxes).forEach(m => console.log(" ", m.where, m.name, "Lv", m.level, m.nature, m.ability, m.moves.join("/"), "met", m.met));
console.log(bad.length ? `${bad.length} odd Pokémon` : "all Pokémon look sane");
process.exit(bad.length ? 1 : 0);
