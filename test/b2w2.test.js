// node test/b2w2.test.js [file.sav] : with a file, prints what the B2W2 reader finds in it;
// without one, builds a made-up save (party + box + badges + dex) and checks the reader gets it all back
const fs = require("fs"), path = require("path");
const D = path.join(__dirname, "../bb2r/data");
const ids = JSON.parse(fs.readFileSync(path.join(D, "ids.json"))), meta = JSON.parse(fs.readFileSync(path.join(D, "meta.json")));
const R = require("../shared/savereader_b2w2.js");
const show = s => { console.log(JSON.stringify({ ...s, party: s.party.length, boxes: s.boxes.length, caught: s.caught.length }));
  for (const m of s.party.concat(s.boxes)) console.log(m.where, m.name, "Lv" + m.level, m.nature, m.ability, m.item, m.moves.join("/"), "IV", Object.values(m.ivs).join("/"), m.met, m.shiny ? "SHINY" : ""); };
if (process.argv[2]) { show(R.readSave(fs.readFileSync(process.argv[2]), ids, meta)); process.exit(0); }

const POS = [0,1,2,3, 0,1,3,2, 0,2,1,3, 0,3,1,2, 0,2,3,1, 0,3,2,1, 1,0,2,3, 1,0,3,2, 2,0,1,3, 3,0,1,2, 2,0,3,1, 3,0,2,1,
             1,2,0,3, 1,3,0,2, 2,1,0,3, 3,1,0,2, 2,3,0,1, 3,2,0,1, 1,2,3,0, 1,3,2,0, 2,1,3,0, 3,1,2,0, 2,3,1,0, 3,2,1,0];
const w16 = (b, o, v) => { b[o] = v & 255; b[o + 1] = v >> 8 & 255; }, w32 = (b, o, v) => { w16(b, o, v & 0xFFFF); w16(b, o + 2, v >>> 16); };
function crypt(b, s, e, seed) { for (let i = s; i < e; i += 2) { seed = (Math.imul(0x41C64E6D, seed) + 0x6073) >>> 0; const x = seed >>> 16; b[i] ^= x & 255; b[i + 1] ^= x >>> 8; } }
function pk5({ sp, pid, lv, exp, nat, ab, item, moves, ivs, met, nick, form = 0, party }) {
  const d = new Uint8Array(party ? 220 : 136);
  w32(d, 0, pid); w16(d, 8, sp); w16(d, 0x0A, item); w16(d, 0x0C, 12345); w16(d, 0x0E, 54321); w32(d, 0x10, exp); d[0x15] = ab;
  moves.forEach((m, i) => w16(d, 0x28 + i * 2, m));
  w32(d, 0x38, ivs[0] | ivs[1] << 5 | ivs[2] << 10 | ivs[3] << 15 | ivs[4] << 20 | ivs[5] << 25);
  d[0x40] = form << 3; d[0x41] = nat; [...nick].forEach((c, i) => w16(d, 0x48 + i * 2, c.charCodeAt(0))); w16(d, 0x48 + nick.length * 2, 0xFFFF);
  w16(d, 0x80, met); d[0x84] = 5;
  if (party) { d[0x8C] = lv; w16(d, 0x8E, 20); w16(d, 0x90, 24); }
  let sum = 0; for (let i = 8; i < 136; i += 2) sum = (sum + (d[i] | d[i + 1] << 8)) & 0xFFFF; w16(d, 6, sum);
  const sv = ((pid & 0x3E000) >>> 0xD) % 24, out = new Uint8Array(d);
  for (let i = 0; i < 4; i++) out.set(d.subarray(8 + i * 32, 8 + i * 32 + 32), 8 + POS[sv * 4 + i] * 32);
  crypt(out, 8, 136, sum); if (party) crypt(out, 136, 220, pid);
  return out;
}
const buf = new Uint8Array(0x80000);
[..."Carlos"].forEach((c, i) => w16(buf, 0x19404 + i * 2, c.charCodeAt(0))); w16(buf, 0x19404 + 12, 0xFFFF);
w16(buf, 0x19414, 12345); buf[0x19421] = 0; w16(buf, 0x19424, 3); buf[0x19426] = 7;
buf[0x21104] = 0b111;                                         // Basic, Toxic, Insect
w32(buf, 0x21404, 495 << 12);                                 // first species registered: Snivy
[495, 504, 519].forEach(sp => { buf[0x21408 + ((sp - 1) >> 3)] |= 1 << ((sp - 1) & 7); });
const mv = n => ids.moves.indexOf(n);
buf[0x18E04] = 1;
buf.set(pk5({ sp: 495, pid: 0x12345678, lv: 14, exp: 2000, nat: 3, ab: ids.abilities.indexOf("Contrary"), item: ids.items.indexOf("Oran Berry"),
  moves: [mv("Tackle"), mv("Leer"), mv("Vine Whip")], ivs: [31, 20, 10, 5, 0, 31], met: 117, nick: "Leafy", party: true }), 0x18E08);
buf.set(pk5({ sp: 504, pid: 0x0BADBEEF, lv: 0, exp: 560, nat: 10, ab: ids.abilities.indexOf("Run Away"), item: 0, moves: [mv("Tackle"), 4],
  ivs: [1, 2, 3, 4, 5, 6], met: 125, nick: "Patrat" }), 0x400 + 0x1000 * 1 + 136 * 2);
if (process.env.WRITE) fs.writeFileSync(process.env.WRITE, buf);            // WRITE=made-up.sav keeps the file for browser tests
const s = R.readSave(buf.buffer, ids, meta);
show(s);
const ok = [s.name === "Carlos", s.gender === "M", s.tid === 12345, s.hours === 3 && s.minutes === 7, s.badges.join() === "Basic,Toxic,Insect",
  s.starter === "Snivy", s.caught.join() === "Snivy,Patrat,Pidove", s.party.length === 1, s.party[0].name === "Snivy", s.party[0].level === 14,
  s.party[0].nature === "Adamant", s.party[0].ability === "Contrary", s.party[0].item === "Oran Berry", s.party[0].moves.join() === "Tackle,Leer,Vine Whip",
  s.party[0].ivs.sp === 5 && s.party[0].ivs.sd === 31, s.party[0].met === "Aspertia City", s.party[0].nick === "Leafy", s.party[0].hp === 20,
  s.boxes.length === 1, s.boxes[0].where === "Box 2", s.boxes[0].name === "Patrat", s.boxes[0].level === 8, s.boxes[0].met === "Route 20",
  s.boxes[0].moves[1] === "Power-Up Punch"];
console.log(ok.every(Boolean) ? "all checks passed" : "FAILED: " + ok.map((x, i) => x ? "" : i).filter(String).join(","));
process.exit(ok.every(Boolean) ? 0 : 1);
