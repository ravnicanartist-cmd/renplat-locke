/* Pokémon Black 2 / White 2 (Blaze Black 2 Redux) save reader. Runs in the browser; nothing is uploaded.
   Offsets from PKHeX (SAV5B2W2.cs, SaveBlockAccessor5B2W2.cs, PlayerData5.cs, Misc5.cs, Zukan5.cs, PK5.cs, PokeCrypto.cs):
     boxes   0x00400 + box * 0x1000, 30 slots x 136 bytes, 24 boxes
     party   0x18E00: count at +4, Pokémon at +8 (220 bytes each)
     trainer 0x19400: name +4 (UTF-16), TID +0x14, SID +0x16, gender +0x21, play time +0x24 (hours u16, minutes, seconds)
     misc    0x21100: money +0, badges +4
     dex     0x21400: packed info +4 (first species seen = the starter, bits 12-21), caught bits +8
   B2W2 has no simple "trainer beaten" flag table we can map, so fights are worked out from your badges. */
(function (root) {
  const BOX = 0x400, PARTY = 0x18E00, TR = 0x19400, MISC = 0x21100, DEX = 0x21400;
  const POS = [0,1,2,3, 0,1,3,2, 0,2,1,3, 0,3,1,2, 0,2,3,1, 0,3,2,1, 1,0,2,3, 1,0,3,2, 2,0,1,3, 3,0,1,2, 2,0,3,1, 3,0,2,1,
               1,2,0,3, 1,3,0,2, 2,1,0,3, 3,1,0,2, 2,3,0,1, 3,2,0,1, 1,2,3,0, 1,3,2,0, 2,1,3,0, 3,1,2,0, 2,3,1,0, 3,2,1,0];
  const u16 = (d, o) => d[o] | (d[o + 1] << 8), u32 = (d, o) => (d[o] | (d[o + 1] << 8) | (d[o + 2] << 16) | (d[o + 3] << 24)) >>> 0;
  function crypt(buf, start, end, seed) {
    for (let i = start; i < end; i += 2) {
      seed = (Math.imul(0x41C64E6D, seed) + 0x6073) >>> 0;
      const x = seed >>> 16;
      buf[i] ^= x & 0xFF; buf[i + 1] ^= x >>> 8;
    }
  }
  function decrypt(raw) {
    const d = new Uint8Array(raw);
    const pid = u32(d, 0), chk = u16(d, 6), sv = ((pid & 0x3E000) >>> 0xD) % 24;
    crypt(d, 8, 136, chk);
    if (d.length > 136) crypt(d, 136, d.length, pid);
    const out = new Uint8Array(d);
    for (let i = 0; i < 4; i++) out.set(d.subarray(8 + POS[sv * 4 + i] * 32, 8 + POS[sv * 4 + i] * 32 + 32), 8 + i * 32);
    return out;
  }
  const SPECIAL = { 0x246D: "♂", 0x246E: "♀", 0x2467: "×", 0x2468: "÷" };
  function str(d, o, len) {
    let s = "";
    for (let i = 0; i < len; i += 2) {
      const v = u16(d, o + i);
      if (v === 0xFFFF || v === 0) break;
      s += SPECIAL[v] || String.fromCharCode(v);
    }
    return s;
  }
  const EXP = [n => n ** 3, n => n <= 50 ? Math.floor(n ** 3 * (100 - n) / 50) : n <= 68 ? Math.floor(n ** 3 * (150 - n) / 100)
      : n <= 98 ? Math.floor(n ** 3 * Math.floor((1911 - 10 * n) / 3) / 500) : Math.floor(n ** 3 * (160 - n) / 100),
    n => n <= 15 ? Math.floor(n ** 3 * (Math.floor((n + 1) / 3) + 24) / 50) : n <= 36 ? Math.floor(n ** 3 * (n + 14) / 50) : Math.floor(n ** 3 * (Math.floor(n / 2) + 32) / 50),
    n => Math.floor(1.2 * n ** 3 - 15 * n ** 2 + 100 * n - 140), n => Math.floor(4 * n ** 3 / 5), n => Math.floor(5 * n ** 3 / 4)];
  function levelFromExp(exp, gr) {
    const f = EXP[gr] || EXP[0];
    let l = 1;
    while (l < 100 && f(l + 1) <= exp) l++;
    return l;
  }
  const FORMNAME = { Rotom: ["Rotom", "Rotom-Heat", "Rotom-Wash", "Rotom-Frost", "Rotom-Fan", "Rotom-Mow"],
    Wormadam: ["Wormadam", "Wormadam-Sandy", "Wormadam-Trash"], Giratina: ["Giratina", "Giratina-Origin"], Shaymin: ["Shaymin", "Shaymin-Sky"],
    Deoxys: ["Deoxys", "Deoxys-Attack", "Deoxys-Defense", "Deoxys-Speed"], Basculin: ["Basculin", "Basculin-Blue-Striped"],
    Kyurem: ["Kyurem", "Kyurem-White", "Kyurem-Black"], Keldeo: ["Keldeo", "Keldeo-Resolute"], Meloetta: ["Meloetta", "Meloetta-Pirouette"],
    Tornadus: ["Tornadus", "Tornadus-Therian"], Thundurus: ["Thundurus", "Thundurus-Therian"], Landorus: ["Landorus", "Landorus-Therian"] };

  function readMon(raw, ids, meta, where) {
    if (u32(raw, 0) === 0 && u16(raw, 6) === 0) return null;
    const d = decrypt(raw);
    const sp = u16(d, 0x08);
    if (!sp || sp > 649) return null;
    const pid = u32(d, 0), iv32 = u32(d, 0x38);
    if ((iv32 >>> 30) & 1) return null;                         // egg
    const base = ids.species[sp], form = d[0x40] >>> 3;
    const fn = (FORMNAME[base] || [])[form];
    const name = fn && meta.mons[fn] ? fn : base;
    const exp = u32(d, 0x10);
    const level = d.length > 136 && d[0x8C] ? d[0x8C] : levelFromExp(exp, ids.gr[sp]);
    const ivs = { hp: iv32 & 31, at: (iv32 >>> 5) & 31, df: (iv32 >>> 10) & 31, sp: (iv32 >>> 15) & 31, sa: (iv32 >>> 20) & 31, sd: (iv32 >>> 25) & 31 };
    const evs = { hp: d[0x18], at: d[0x19], df: d[0x1A], sp: d[0x1B], sa: d[0x1C], sd: d[0x1D] };
    const moves = [0, 1, 2, 3].map(i => u16(d, 0x28 + i * 2)).filter(Boolean).map(m => ids.moves[m] || ("#" + m));
    // Gen 5 keeps the ability itself in the Pokémon (set from Blaze Black 2 Redux's species table when it was made)
    const md = meta.mons[name] || {}, abs = md.ab || [];
    const ability = ids.abilities[d[0x15]] || abs[0] || "";
    const tid = u16(d, 0x0C), sid = u16(d, 0x0E);
    const met = u16(d, 0x80), egg = u16(d, 0x7E);
    const item = u16(d, 0x0A);
    return { name, species: sp, nick: str(d, 0x48, 22), level, exp, nature: ids.natures[d[0x41]] || ids.natures[pid % 25], ivs, evs,
             ability, abilityId: d[0x15], hidden: !!(d[0x42] & 1), item: item && ids.items[item] ? ids.items[item] : "", moves,
             shiny: ((tid ^ sid ^ (pid >>> 16) ^ (pid & 0xFFFF)) >>> 0) < 8, pid,
             metLevel: d[0x84] & 0x7F, met: egg ? "Egg" : (met < ids.loc.length ? ids.loc[met] : met >= 30000 ? "Gift / trade" : ""), metId: met,
             hp: d.length > 136 ? u16(d, 0x8E) : null, maxhp: d.length > 136 ? u16(d, 0x90) : null, where };
  }

  function readSave(buf, ids, meta) {
    const d = new Uint8Array(buf);
    if (d.length < 0x26000) throw new Error("This file is too small to be a Black 2 / White 2 save (it should be 512 KB).");
    const pc = d[PARTY + 4];
    if (pc > 6) throw new Error("This doesn't look like a Black 2 / White 2 save (is it from a different game?).");
    const out = { name: str(d, TR + 4, 16), gender: d[TR + 0x21] ? "F" : "M", tid: u16(d, TR + 0x14), sid: u16(d, TR + 0x16),
                  hours: u16(d, TR + 0x24), minutes: d[TR + 0x26], money: u32(d, MISC), badges: [], party: [], boxes: [], caught: [],
                  beaten: [], starter: null, block: "main" };
    const b = d[MISC + 4];
    ["Basic", "Toxic", "Insect", "Bolt", "Quake", "Jet", "Legend", "Wave"].forEach((n, i) => { if (b >> i & 1) out.badges.push(n); });
    for (let i = 0; i < pc; i++) {
      const m = readMon(d.subarray(PARTY + 8 + i * 220, PARTY + 8 + (i + 1) * 220), ids, meta, "Party");
      if (m) out.party.push(m);
    }
    for (let bx = 0; bx < 24; bx++) for (let k = 0; k < 30; k++) {
      const o = BOX + bx * 0x1000 + k * 136;
      const m = readMon(d.subarray(o, o + 136), ids, meta, "Box " + (bx + 1));
      if (m) out.boxes.push(m);
    }
    for (let sp = 1; sp <= 649; sp++) if ((d[DEX + 8 + ((sp - 1) >> 3)] >> ((sp - 1) & 7)) & 1) out.caught.push(ids.species[sp]);
    const first = (u32(d, DEX + 4) >>> 12) & 0x3FF;            // the first species registered: the starter
    if (first && first <= 649) out.starter = ids.species[first];
    out.read = new Date().toISOString();
    return out;
  }
  const api = { readSave, decrypt, levelFromExp };
  if (typeof module !== "undefined") module.exports = api; else root.SaveReaderB2W2 = api;
})(this);
