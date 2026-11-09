// node test/hgss.test.js [file.sav] : with a file, prints what the HeartGold / Sacred Gold reader finds in it;
// without one, builds a made-up save (party + box + badges + dex) and checks the reader gets it all back
const fs = require("fs"), path = require("path");
const D = path.join(__dirname, "../sg/data");
const ids = JSON.parse(fs.readFileSync(path.join(D, "ids.json"))), meta = JSON.parse(fs.readFileSync(path.join(D, "meta.json")));
const R = require("../shared/savereader_hgss.js");
const show = s => { console.log(JSON.stringify({ ...s, party: s.party.length, boxes: s.boxes.length, caught: s.caught.length }));
  for (const m of s.party.concat(s.boxes)) console.log(m.where, m.name, "Lv" + m.level, m.nature, m.ability, m.item, m.moves.join("/"), "IV", Object.values(m.ivs).join("/"), m.met); };
if (process.argv[2]) { show(R.readSave(fs.readFileSync(process.argv[2]), ids, meta)); process.exit(0); }

const POS = [0,1,2,3, 0,1,3,2, 0,2,1,3, 0,3,1,2, 0,2,3,1, 0,3,2,1, 1,0,2,3, 1,0,3,2, 2,0,1,3, 3,0,1,2, 2,0,3,1, 3,0,2,1,
             1,2,0,3, 1,3,0,2, 2,1,0,3, 3,1,0,2, 2,3,0,1, 3,2,0,1, 1,2,3,0, 1,3,2,0, 2,1,3,0, 3,1,2,0, 2,3,1,0, 3,2,1,0];
const w16 = (b, o, v) => { b[o] = v & 255; b[o + 1] = v >> 8 & 255; }, w32 = (b, o, v) => { w16(b, o, v & 0xFFFF); w16(b, o + 2, v >>> 16); };
const g4 = s => [...s].map(c => ids.g4.indexOf(c));
function crypt(b, s, e, seed) { for (let i = s; i < e; i += 2) { seed = (Math.imul(0x41C64E6D, seed) + 0x6073) >>> 0; const x = seed >>> 16; b[i] ^= x & 255; b[i + 1] ^= x >>> 8; } }
function pk4({ sp, pid, lv, exp, ab, item, moves, ivs, met, nick, party }) {
  const d = new Uint8Array(party ? 236 : 136);
  w32(d, 0, pid); w16(d, 8, sp); w16(d, 0x0A, item); w16(d, 0x0C, 12345); w16(d, 0x0E, 54321); w32(d, 0x10, exp); d[0x15] = ab;
  moves.forEach((m, i) => w16(d, 0x28 + i * 2, m));
  w32(d, 0x38, ivs[0] | ivs[1] << 5 | ivs[2] << 10 | ivs[3] << 15 | ivs[4] << 20 | ivs[5] << 25);
  g4(nick).forEach((c, i) => w16(d, 0x48 + i * 2, c)); w16(d, 0x48 + nick.length * 2, 0xFFFF);
  w16(d, 0x46, 3002); w16(d, 0x80, met); d[0x84] = 5;
  if (party) { d[0x8C] = lv; w16(d, 0x8E, 20); w16(d, 0x90, 24); }
  let sum = 0; for (let i = 8; i < 136; i += 2) sum = (sum + (d[i] | d[i + 1] << 8)) & 0xFFFF; w16(d, 6, sum);
  const sv = ((pid & 0x3E000) >>> 0xD) % 24, out = new Uint8Array(d);
  for (let i = 0; i < 4; i++) out.set(d.subarray(8 + i * 32, 8 + i * 32 + 32), 8 + POS[sv * 4 + i] * 32);
  crypt(out, 8, 136, sum); if (party) crypt(out, 136, 236, pid);
  return out;
}
const GEN = 0xF628, STO = 0x12310, SG = 0xF700, buf = new Uint8Array(0x80000);
for (const [base, size, count] of [[0, GEN, 5], [SG, STO, 5], [0x40000, GEN, 4], [0x40000 + SG, STO, 4]]) { w32(buf, base + size - 0x14, count); w32(buf, base + size - 0xC, size); }
g4("Carlos").forEach((c, i) => w16(buf, 0x64 + i * 2, c)); w16(buf, 0x64 + 12, 0xFFFF);
w16(buf, 0x64 + 0x10, 12345); buf[0x64 + 0x18] = 0; buf[0x64 + 0x1A] = 0b111; buf[0x64 + 0x1F] = 0b1; w16(buf, 0x64 + 0x22, 3); buf[0x64 + 0x24] = 7;
[158, 161, 21].forEach(sp => { buf[0x12B8 + 4 + ((sp - 1) >> 3)] |= 1 << ((sp - 1) & 7); });
const mv = n => ids.moves.indexOf(n), loc = n => ids.loc.indexOf(n);
buf[0x94] = 1;
buf.set(pk4({ sp: 159, pid: 0x12345678, lv: 18, exp: 5000, ab: ids.abilities.indexOf("Torrent"), item: ids.items.indexOf("Mystic Water"),
  moves: [mv("Scratch"), mv("Water Gun"), mv("Bite")], ivs: [31, 20, 10, 5, 0, 31], met: loc("New Bark Town"), nick: "Croco", party: true }), 0x98);
buf.set(pk4({ sp: 21, pid: 0x0BADBEEF, lv: 0, exp: 560, ab: 51, item: 0, moves: [mv("Peck"), mv("Growl")], ivs: [1, 2, 3, 4, 5, 6], met: loc("Route 46"), nick: "Spearow" }),
  SG + 0x1000 * 1 + 136 * 2);
if (process.env.WRITE) fs.writeFileSync(process.env.WRITE, buf);
const s = R.readSave(buf.buffer, ids, meta);
show(s);
const ok = [s.name === "Carlos", s.gender === "M", s.tid === 12345, s.hours === 3 && s.minutes === 7, s.badges.join() === "Zephyr,Hive,Plain,Boulder",
  s.starter === "Totodile", s.caught.length === 3, s.party.length === 1, s.party[0].name === "Croconaw", s.party[0].level === 18,
  s.party[0].item === "Mystic Water", s.party[0].moves.join() === "Scratch,Water Gun,Bite", s.party[0].ivs.sp === 5 && s.party[0].ivs.sd === 31,
  s.party[0].met === "New Bark Town", s.party[0].nick === "Croco", s.party[0].hp === 20, s.boxes.length === 1, s.boxes[0].where === "Box 2",
  s.boxes[0].name === "Spearow", s.boxes[0].level === 8, s.boxes[0].met === "Route 46", s.block === "first"];
console.log(ok.every(Boolean) ? "all checks passed" : "FAILED: " + ok.map((x, i) => x ? "" : i).filter(String).join(","));
process.exit(ok.every(Boolean) ? 0 : 1);
