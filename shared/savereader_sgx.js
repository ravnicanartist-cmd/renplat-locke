/* SoulGold (eemeliri, pokeemerald-expansion) .sav reader: trainer, badges, difficulty, starter, Pokédex, party and all 21 PC boxes.
   Save format "BX21": 14 rotated sectors per slot (sector id at 0xFF4, signature 0x21325842 at 0xFF8, save counter at 0xFFC),
   Pokémon stored unencrypted (expansion BoxPokemon: 68 bytes with a 12-letter nickname, party 96), boxes in sectors 5–13 plus overflow sectors 30/31,
   a tail in the last SaveBlock1 sector and auxiliary sectors 28/29. Offsets were checked against a real v1.2.1 save. */
(function (root) {
  "use strict";
  const SECTOR = 4096, DATA = 3968, SIG = 0x21325842, SIGOLD = 0x08012025;
  const SB1_PARTY_COUNT = 0x234, SB1_PARTY = 0x238, PARTY_SIZE = 96, BOX_SIZE = 68;
  const FLAGS = 0x1870, SYS = 0xACC, VARS = 0x1B42, DEX_CAUGHT = 0x3279, DEX_BYTES = 129;
  const STORE_BOXES = 404, BOXES = 21, SLOTS = 30, REG = DATA * 9, TAIL = REG + DATA, BX18 = 41624, SB1_TAIL = 1562;
  const BADGES = ["Zephyr", "Hive", "Plain", "Fog", "Storm", "Mineral", "Glacier", "Rising"];
  const STARTER_TYPE = ["Grass starter", "Fire starter", "Water starter"];
  const u16 = (d, o) => d[o] | (d[o + 1] << 8);
  const u32 = (d, o) => (d[o] | (d[o + 1] << 8) | (d[o + 2] << 16) | (d[o + 3] << 24)) >>> 0;
  const CH = {};
  CH[0] = " ";
  for (let i = 0; i < 10; i++) CH[0xA1 + i] = String(i);
  for (let i = 0; i < 26; i++) { CH[0xBB + i] = String.fromCharCode(65 + i); CH[0xD5 + i] = String.fromCharCode(97 + i); }
  Object.assign(CH, { 0xAB: "!", 0xAC: "?", 0xAD: ".", 0xAE: "-", 0xB0: "…", 0xB1: "“", 0xB2: "”", 0xB3: "‘", 0xB4: "’", 0xB5: "♂", 0xB6: "♀",
                      0xB8: ",", 0xBA: "/", 0x1B: "é", 0xF0: ":" });
  function str(d, o, n) { let s = ""; for (let i = 0; i < n; i++) { const c = d[o + i]; if (c === 0xFF) break; s += CH[c] ?? ""; } return s.trim(); }
  const EXP = [n => n ** 3, n => n <= 50 ? Math.floor(n ** 3 * (100 - n) / 50) : n <= 68 ? Math.floor(n ** 3 * (150 - n) / 100)
      : n <= 98 ? Math.floor(n ** 3 * Math.floor((1911 - 10 * n) / 3) / 500) : Math.floor(n ** 3 * (160 - n) / 100),
    n => n <= 15 ? Math.floor(n ** 3 * (Math.floor((n + 1) / 3) + 24) / 50) : n <= 36 ? Math.floor(n ** 3 * (n + 14) / 50) : Math.floor(n ** 3 * (Math.floor(n / 2) + 32) / 50),
    n => Math.floor(1.2 * n ** 3 - 15 * n ** 2 + 100 * n - 140), n => Math.floor(4 * n ** 3 / 5), n => Math.floor(5 * n ** 3 / 4)];
  function levelFromExp(exp, gr) { const f = EXP[gr] || EXP[0]; let l = 1; while (l < 100 && f(l + 1) <= exp) l++; return l; }

  function slots(d) {
    const out = [];
    for (const [k, base] of [[0, 0], [1, 14 * SECTOR]]) {
      const secs = {}; let cnt = -1, ok = 0;
      for (let i = 0; i < 14; i++) {
        const o = base + i * SECTOR;
        if (o + SECTOR > d.length) break;
        const id = u16(d, o + 0xFF4), sig = u32(d, o + 0xFF8);
        if ((sig !== SIG && sig !== SIGOLD) || id > 13) continue;
        secs[id] = o; cnt = Math.max(cnt, u32(d, o + 0xFFC)); ok++;
        if (sig === SIGOLD) secs.old = true;
      }
      if (ok === 14) out.push({ slot: k, secs, cnt });
    }
    return out.sort((a, b) => b.cnt - a.cnt)[0];
  }
  function readMon(m, size, ids, where) {
    const pid = u32(m, 0), ot = u32(m, 4);
    const w0 = u32(m, 32), w1 = u32(m, 36), w2 = u32(m, 40), w3 = u32(m, 44), w4 = u32(m, 48), w8 = u32(m, 64);
    const sp = w0 & 0x7FF;
    if (!sp || !ids.species[sp]) return null;
    if ((m[21] >> 2) & 1 || (w4 >>> 31) & 1) return null;                 // egg
    const name = ids.species[sp];
    const exp = w1 & 0xFFFFFF;
    const level = size === PARTY_SIZE && m[80] ? m[80] : levelFromExp(exp, ids.gr[sp] || 0);
    const metId = ((w2 >>> 16) & 0xFF) | ((((w4 >>> 22) & 1) | (((w4 >>> 23) & 31) << 1) | (((w4 >>> 28) & 1) << 6)) << 8);
    const abn = (w4 >>> 29) & 3, abs = ids.abil[sp] || [];
    const nat = ((pid % 25) ^ (m[20] >>> 3)) % 25;                       // mints change the nature without touching the PID
    const sv = ((ot >>> 16) ^ (ot & 0xFFFF) ^ (pid >>> 16) ^ (pid & 0xFFFF)) >>> 0;
    const item = (w0 >>> 16) & 0x3FF;
    const moves = [w3 & 0x7FF, (w3 >>> 16) & 0x7FF, w4 & 0x7FF, (w4 >>> 11) & 0x7FF].filter(Boolean).map(x => ids.moves[x] || "#" + x);
    return { name, species: sp, nick: str(m, 8, 12), level, exp, nature: ids.natures[nat],
             ivs: { hp: w8 & 31, at: (w8 >>> 5) & 31, df: (w8 >>> 10) & 31, sp: (w8 >>> 15) & 31, sa: (w8 >>> 20) & 31, sd: (w8 >>> 25) & 31 },
             evs: { hp: m[56], at: m[57], df: m[58], sp: m[59], sa: m[60], sd: m[61] },
             ability: abs[abn] || abs[0] || "", item: ids.items[item] || "", moves,
             shiny: (sv < 256) !== !!((u16(m, 30) >>> 14) & 1), pid, metLevel: (w2 >>> 24) & 0x7F, met: ids.loc[metId] || "", metId,
             hp: size === PARTY_SIZE ? u16(m, 82) : null, maxhp: size === PARTY_SIZE ? u16(m, 84) : null, where };
  }

  function readSave(buf, ids) {
    const d = new Uint8Array(buf);
    if (d.length < 0x20000) throw new Error("This file is too small to be a SoulGold save (it should be 128 KB).");
    const S = slots(d);
    if (!S) throw new Error("This doesn't look like a SoulGold save (no complete save slot found).");
    if (S.secs.old) throw new Error("This save is from an older SoulGold version: load it in v1.2.1 and save once, then read it again.");
    const sec = id => d.subarray(S.secs[id], S.secs[id] + DATA);
    const sb2 = sec(0);
    const sb1 = new Uint8Array(DATA * 4);
    for (let i = 0; i < 4; i++) sb1.set(sec(1 + i), i * DATA);
    const flag = n => (sb1[FLAGS + (n >> 3)] >> (n & 7)) & 1;
    const vr = i => u16(sb1, VARS + i * 2);
    const opt = u16(sb2, 0x16);
    const out = { name: str(sb2, 0, 8), gender: sb2[8] ? "F" : "M", tid: u16(sb2, 0xA), sid: u16(sb2, 0xC), hours: u16(sb2, 0xE), minutes: sb2[0x10],
                  badges: BADGES.filter((b, i) => flag(SYS + 7 + i)), champion: !!flag(SYS + 4),
                  mode: (opt >> 3) & 1 ? "hard" : "normal", caps: ["off", "soft", "hard"][(opt >> 9) & 7] || "",
                  scaling: { trainers: !!((opt >> 1) & 1), wild: !!((opt >> 2) & 1) },
                  party: [], boxes: [], caught: [], beaten: [], starter: null, starterMon: null };
    const sv = vr(0x23), ss = vr(0xB8);
    if (ss && ids.species[ss]) { out.starterMon = ids.species[ss]; out.starter = STARTER_TYPE[sv] || null; }
    const pc = Math.min(sb1[SB1_PARTY_COUNT], 6);
    for (let i = 0; i < pc; i++) { const m = readMon(sb1.subarray(SB1_PARTY + i * PARTY_SIZE, SB1_PARTY + (i + 1) * PARTY_SIZE), PARTY_SIZE, ids, "Party"); if (m) out.party.push(m); }
    // PC storage: one 43456-byte block spread over several sectors
    function storage(off, n) {
      const o = new Uint8Array(n); let p = 0;
      while (n > 0) {
        let base, pos, av;
        if (off < REG) { base = S.secs[5 + Math.floor(off / DATA)]; pos = off % DATA; av = DATA - pos; }
        else if (off < TAIL) { base = (30 + S.slot) * SECTOR; pos = off - REG; av = DATA - pos; }
        else if (off < BX18) { base = S.secs[4]; pos = SB1_TAIL + off - TAIL; av = BX18 - off; }
        else { base = (28 + S.slot) * SECTOR; pos = 12 + off - BX18; av = DATA - pos; }
        const c = Math.min(n, av);
        if (base + pos + c <= d.length) o.set(d.subarray(base + pos, base + pos + c), p);
        p += c; off += c; n -= c;
      }
      return o;
    }
    const st = storage(0, STORE_BOXES + BOXES * SLOTS * BOX_SIZE);
    if (u32(st, 0) === 0x31325842) {
      for (let b = 0; b < BOXES; b++) for (let k = 0; k < SLOTS; k++) {
        const o = STORE_BOXES + (b * SLOTS + k) * BOX_SIZE;
        const m = readMon(st.subarray(o, o + BOX_SIZE), BOX_SIZE, ids, "Box " + (b + 1));
        if (m) out.boxes.push(m);
      }
    }
    for (let n = 1; n <= DEX_BYTES * 8; n++) if ((sb1[DEX_CAUGHT + ((n - 1) >> 3)] >> ((n - 1) & 7)) & 1 && ids.species[n]) out.caught.push(ids.species[n]);   // national dex no. = species id for base forms
    out.read = new Date().toISOString();
    return out;
  }
  const api = { readSave, levelFromExp };
  if (typeof module !== "undefined") module.exports = api; else root.SaveReaderSGX = api;
})(this);
