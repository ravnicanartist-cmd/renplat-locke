/* Pokémon Platinum / Renegade Platinum save reader. Runs in the browser; nothing is uploaded.
   Every offset comes from PKHeX (SAV4Pt.cs, SAV4.cs, SAV4BlockDetection.cs, PK4.cs, PokeCrypto.cs, Zukan4.cs) and
   the trainer-flag numbers from pret/pokeplatinum (generated/vars_flags.txt):
     two save copies (0x00000 and 0x40000); each has a general block (0xCF2C bytes) and a storage block (0x121E4 bytes)
     the newer copy of each block has the larger footer counters (major, then minor) at block end - 0x14
     general: trainer name 0x68 (16 bytes), gender 0x80, badges 0x82, party count 0x9C, party 0xA0 (236 bytes each),
              event work (vars) 0xDAC, event flags 0xFEC, Pokédex 0x1328 (caught = region 0)
     storage: box data at +4, 18 boxes x 30 slots x 136 bytes
     a trainer counts as beaten when flag 1360 + trainer id is set; VAR_PLAYER_STARTER is work 48 */
(function (root) {
  const GEN = 0xCF2C, STO = 0x121E4, PARTY = 0xA0, T1 = 0x68, FLAGS = 0xFEC, WORK = 0xDAC, DEX = 0x1328;
  const POS = [0,1,2,3, 0,1,3,2, 0,2,1,3, 0,3,1,2, 0,2,3,1, 0,3,2,1, 1,0,2,3, 1,0,3,2, 2,0,1,3, 3,0,1,2, 2,0,3,1, 3,0,2,1,
               1,2,0,3, 1,3,0,2, 2,1,0,3, 3,1,0,2, 2,3,0,1, 3,2,0,1, 1,2,3,0, 1,3,2,0, 2,1,3,0, 3,1,2,0, 2,3,1,0, 3,2,1,0];
  const u16 = (d, o) => d[o] | (d[o + 1] << 8), u32 = (d, o) => (d[o] | (d[o + 1] << 8) | (d[o + 2] << 16) | (d[o + 3] << 24)) >>> 0;

  function newer(d, a, b, size) {                       // SAV4BlockDetection.CompareFooters
    const fa = a + size - 0x14, fb = b + size - 0x14;
    const ok = o => u32(d, o + 8) === size;               // footer stores the block size
    if (!ok(fa)) return b; if (!ok(fb)) return a;
    const cmp = (x, y) => x === y ? 0 : (x === 0xFFFFFFFF ? -1 : y === 0xFFFFFFFF ? 1 : (x > y ? 1 : -1));
    const c = cmp(u32(d, fa), u32(d, fb)) || cmp(u32(d, fa + 4), u32(d, fb + 4));
    return c >= 0 ? a : b;
  }
  function crypt(buf, start, end, seed) {               // PokeCrypto.CryptArray: LCG 0x41C64E6D, 0x6073
    for (let i = start; i < end; i += 2) {
      seed = (Math.imul(0x41C64E6D, seed) + 0x6073) >>> 0;
      const x = seed >>> 16;
      buf[i] ^= x & 0xFF; buf[i + 1] ^= x >>> 8;
    }
  }
  function decrypt(raw) {                                // PokeCrypto.Decrypt45
    const d = new Uint8Array(raw);
    const pid = u32(d, 0), chk = u16(d, 6), sv = ((pid & 0x3E000) >>> 0xD) % 24;
    crypt(d, 8, 136, chk);
    if (d.length > 136) crypt(d, 136, d.length, pid);
    const out = new Uint8Array(d);
    for (let i = 0; i < 4; i++) out.set(d.subarray(8 + POS[sv * 4 + i] * 32, 8 + POS[sv * 4 + i] * 32 + 32), 8 + i * 32);
    return out;
  }
  function str(d, o, len, T) {
    let s = "";
    for (let i = 0; i < len; i += 2) {
      const v = u16(d, o + i);
      if (v === 0xFFFF || v === 0) break;
      s += v < T.length ? T[v] : "?";
    }
    return s.replace(/\u0000/g, "");
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
                     Wormadam: ["Wormadam", "Wormadam-Sandy", "Wormadam-Trash"], Giratina: ["Giratina", "Giratina-Origin"],
                     Shaymin: ["Shaymin", "Shaymin-Sky"], Deoxys: ["Deoxys", "Deoxys-Attack", "Deoxys-Defense", "Deoxys-Speed"] };

  function readMon(raw, ids, meta, where) {
    if (u32(raw, 0) === 0 && u16(raw, 6) === 0) return null;
    const d = decrypt(raw);
    const sp = u16(d, 0x08);
    if (!sp || sp > 493) return null;
    const pid = u32(d, 0), iv32 = u32(d, 0x38);
    if ((iv32 >>> 30) & 1) return null;                    // egg
    const base = ids.species[sp].replace("♀", "-F").replace("♂", "-M");
    const form = d[0x40] >>> 3;
    const name = (FORMNAME[base] || [])[form] || base;
    const md = meta.mons[name] || meta.mons[base];
    const gr = md ? md.gr : 0;
    const exp = u32(d, 0x10);
    const level = d.length > 136 && d[0x8C] ? d[0x8C] : levelFromExp(exp, gr);
    const ivs = { hp: iv32 & 31, at: (iv32 >>> 5) & 31, df: (iv32 >>> 10) & 31, sp: (iv32 >>> 15) & 31, sa: (iv32 >>> 20) & 31, sd: (iv32 >>> 25) & 31 };
    const evs = { hp: d[0x18], at: d[0x19], df: d[0x1A], sp: d[0x1B], sa: d[0x1C], sd: d[0x1D] };
    const moves = [0, 1, 2, 3].map(i => u16(d, 0x28 + i * 2)).filter(Boolean).map(m => ids.moves[m] || ("#" + m));
    // ability: Gen 4 picks the slot from PID bit 0; mapped through Renegade Platinum's species table
    const abs = md ? md.ab : [];
    const ability = abs.length > 1 && (pid & 1) ? abs[1] : (abs[0] || ids.abilities[d[0x15]]);
    const tid = u16(d, 0x0C), sid = u16(d, 0x0E);
    const met = u16(d, 0x46) || u16(d, 0x80);
    return { name, species: sp, nick: str(d, 0x48, 22, ids.g4), level, exp, nature: ids.natures[pid % 25], ivs, evs,
             ability, abilityId: d[0x15], item: ids.items[u16(d, 0x0A)] && u16(d, 0x0A) ? ids.items[u16(d, 0x0A)] : "",
             moves, shiny: ((tid ^ sid ^ (pid >>> 16) ^ (pid & 0xFFFF)) >>> 0) < 8, pid,
             metLevel: d[0x84] & 0x7F, met: ids.loc[met] || (met >= 2000 ? "Gift / trade" : ""), metId: met,
             hp: d.length > 136 ? u16(d, 0x8E) : null, maxhp: d.length > 136 ? u16(d, 0x90) : null, where };
  }

  function readSave(buf, ids, meta) {
    const d = new Uint8Array(buf);
    if (d.length < 0x80000) throw new Error("This file is too small to be a Platinum save (it should be 512 KB).");
    const g = newer(d, 0, 0x40000, GEN), s = newer(d, GEN, 0x40000 + GEN, STO);
    if (u32(d, g + GEN - 0x14 + 8) !== GEN) throw new Error("This doesn't look like a Platinum save.");
    const G = d.subarray(g, g + GEN), S = d.subarray(s, s + STO);
    const flag = i => (G[FLAGS + (i >> 3)] >> (i & 7)) & 1;
    const out = { name: str(G, T1, 16, ids.g4), gender: G[T1 + 0x18] ? "F" : "M", badges: [],
                  tid: u16(G, T1 + 0x10), sid: u16(G, T1 + 0x12), money: u32(G, T1 + 0x14),
                  hours: u16(G, T1 + 0x22), minutes: G[T1 + 0x24], party: [], boxes: [], caught: [], beaten: [],
                  starter: null, block: g ? "second" : "first" };
    const b = G[T1 + 0x1A];
    ["Coal", "Forest", "Cobble", "Fen", "Relic", "Mine", "Icicle", "Beacon"].forEach((n, i) => { if (b >> i & 1) out.badges.push(n); });
    const st = u16(G, WORK + 48 * 2);
    if (st) out.starter = ids.species[st];
    const pc = Math.min(G[PARTY - 4], 6);
    for (let i = 0; i < pc; i++) {
      const m = readMon(G.subarray(PARTY + i * 236, PARTY + (i + 1) * 236), ids, meta, "Party");
      if (m) out.party.push(m);
    }
    for (let bx = 0; bx < 18; bx++) for (let k = 0; k < 30; k++) {
      const o = 4 + (bx * 30 + k) * 136;
      const m = readMon(S.subarray(o, o + 136), ids, meta, "Box " + (bx + 1));
      if (m) out.boxes.push(m);
    }
    for (let sp = 1; sp <= 493; sp++) if ((G[DEX + 4 + ((sp - 1) >> 3)] >> ((sp - 1) & 7)) & 1) out.caught.push(ids.species[sp].replace("♀", "-F").replace("♂", "-M"));
    for (let t = 1; t < 1100; t++) if (flag(ids.tflag + t)) out.beaten.push(t);
    out.read = new Date().toISOString();
    return out;
  }
  const api = { readSave, decrypt, levelFromExp };
  if (typeof module !== "undefined") module.exports = api; else root.SaveReader = api;
})(this);
