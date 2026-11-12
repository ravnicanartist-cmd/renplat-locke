/* The 1-on-1 model. Same rules, in the same order, as build/build.py, so a cell computed here for your own
   Pokémon matches a cell from the data files exactly (checked by test/model.test.js). */
(function (root) {
  const KEYS = ["hp", "at", "df", "sa", "sd", "sp"];
  function Model(META) {
    const statsOf = (bs, lv, ivs, nature, evs) => {
      const n = META.natures[nature] || [], st = {};
      KEYS.forEach((k, i) => {
        const iv = typeof ivs === "number" ? ivs : ivs[k], ev = evs ? Math.floor((evs[k] || 0) / 4) : 0, b = bs[i];
        st[k] = k === "hp" ? Math.floor((2 * b + iv + ev) * lv / 100) + lv + 10
          : Math.floor((Math.floor((2 * b + iv + ev) * lv / 100) + 5) * (k === n[0] ? 1.1 : k === n[1] ? 0.9 : 1));
      });
      return st;
    };
    const mon = (name, lv, o) => {
      const d = META.mons[name];
      if (!d) return null;
      o = o || {};
      return { name, lv, t: d.t, ab: o.ab || d.ab[0], item: o.item || "", moves: o.moves || [],
               st: statsOf(o.bs || d.bs, lv, o.ivs == null ? 15 : o.ivs, o.nature || "Hardy", o.evs) };
    };
    const eff = (mt, types) => types.reduce((x, t) => x * ((META.chart[mt] || {})[t] ?? 1), 1);
    const WAB = { "Drizzle": "rain", "Drought": "sun", "Sand Stream": "sand", "Snow Warning": "hail", "Primordial Sea": "rain", "Desolate Land": "sun" };
    const WMOVE = { "Rain Dance": "rain", "Sunny Day": "sun", "Sandstorm": "sand", "Hail": "hail", "Snowscape": "hail", "Chilly Reception": "hail" };
    const WBALL = { rain: "Water", sun: "Fire", sand: "Rock", hail: "Ice" };
    const WSPEED = { "Swift Swim": "rain", "Chlorophyll": "sun", "Sand Rush": "sand", "Slush Rush": "hail" };
    const RESIST = { "Occa Berry": "Fire", "Passho Berry": "Water", "Wacan Berry": "Electric", "Rindo Berry": "Grass", "Yache Berry": "Ice",
      "Chople Berry": "Fighting", "Kebia Berry": "Poison", "Shuca Berry": "Ground", "Coba Berry": "Flying", "Payapa Berry": "Psychic",
      "Tanga Berry": "Bug", "Charti Berry": "Rock", "Kasib Berry": "Ghost", "Haban Berry": "Dragon", "Colbur Berry": "Dark",
      "Babiri Berry": "Steel", "Roseli Berry": "Fairy" };
    const BREAK = ["Mold Breaker", "Teravolt", "Turboblaze"];
    const EVOS = META.evos || {};
    const mtype = (move, w) => move === "Weather Ball" && w ? WBALL[w] : META.moves[move][0];
    function effd(a, d, mt) {
      let e = eff(mt, a.ab === "Scrappy" && (mt === "Normal" || mt === "Fighting") ? d.t.filter(t => t !== "Ghost") : d.t);
      if (!BREAK.includes(a.ab)) {
        if (META.immune[d.ab] === mt) e = 0;
        if (d.ab === "Thick Fat" && (mt === "Fire" || mt === "Ice")) e *= 0.5;
        if (d.ab === "Heatproof" && mt === "Fire") e *= 0.5;
        if (d.ab === "Wonder Guard" && e <= 1) e = 0;
        if (["Filter", "Solid Rock", "Prism Armor"].includes(d.ab) && e > 1) e *= 0.75;
      }
      if (d.item === "Air Balloon" && mt === "Ground") e = 0;
      if (a.ab === "Tinted Lens" && e > 0 && e < 1) e *= 2;
      return e;
    }
    function damage(a, d, move, intim, w) {
      const m = META.moves[move];
      if (!m) return 0;
      w = w || "";
      let [, cat, bp] = m; const mt = mtype(move, w);
      if (META.fixed[move] != null) return eff(mt, d.t) === 0 ? 0 : (META.fixed[move] === "level" ? a.lv : META.fixed[move]);
      if (!bp || bp <= 1 || cat === "Status") return 0;
      if (move === "Synchronoise" && !a.t.some(t => d.t.includes(t))) return 0;   // only hits targets that share a type with the user
      if (move === "Weather Ball" && w) bp *= 2;
      if (move === "Acrobatics" && (a.item === "" || a.item === "Flying Gem")) bp *= 2;
      const phys = cat === "Physical", f32 = x => Math.floor(x * 3 / 2);
      let A = a.st[phys ? "at" : "sa"], D = d.st[phys ? "df" : "sd"];
      if (phys && (a.ab === "Huge Power" || a.ab === "Pure Power")) A *= 2;
      if ((a.item === "Light Ball" && a.name === "Pikachu") || (phys && a.item === "Thick Club" && (a.name === "Cubone" || a.name === "Marowak"))) A *= 2;
      if (phys && a.ab === "Hustle") A = f32(A);
      if (!phys && a.ab === "Solar Power" && w === "sun") A = f32(A);
      if (phys && intim) A = Math.floor(A * 2 / 3);
      if (d.item === "Eviolite" && EVOS[d.name]) D = f32(D);
      if (!phys && d.item === "Assault Vest") D = f32(D);
      if (!phys && w === "sand" && d.t.includes("Rock")) D = f32(D);
      if (phys && d.ab === "Fur Coat" && !BREAK.includes(a.ab)) D *= 2;
      if (a.ab === "Technician" && bp <= 60) bp *= 1.5;
      const base = Math.floor(Math.floor(Math.floor(2 * a.lv / 5 + 2) * bp * A / D) / 50) + 2;
      const stab = a.t.includes(mt) ? (a.ab === "Adaptability" ? 2 : 1.5) : 1;
      const e = effd(a, d, mt);
      const item = META.boost[a.item] === mt ? 1.2 : a.item === "Life Orb" ? 1.3
        : ((a.item === "Choice Band" && phys) || (a.item === "Choice Specs" && !phys)) ? 1.5
        : ((a.item === "Muscle Band" && phys) || (a.item === "Wise Glasses" && !phys)) ? 1.1
        : (a.item === "Expert Belt" && e > 1) ? 1.2 : 1;
      let wm = 1;
      if (w === "rain") wm = mt === "Water" ? 1.5 : mt === "Fire" ? 0.5 : 1;
      if (w === "sun") wm = mt === "Fire" ? 1.5 : mt === "Water" ? 0.5 : 1;
      if (w === "sand" && a.ab === "Sand Force" && ["Rock", "Ground", "Steel"].includes(mt)) wm = 1.3;
      return base * 0.925 * stab * e * item * (META.multi[move] || 1) * wm;
    }
    // how many of a's hits knock d out: the first hit can be changed by a berry, a Gem, Multiscale, a Focus Sash...
    function hits(a, d, move, dn, w) {
      if (dn <= 0) return 99;
      const hp = d.st.hp, mt = mtype(move, w), mb = BREAK.includes(a.ab);
      let d1 = dn;
      if (a.item === mt + " Gem" && move !== "Acrobatics") d1 = d1 * 1.5;
      if (RESIST[d.item] === mt && eff(mt, d.t) > 1) d1 = d1 * 0.5;
      if (d.item === "Chilan Berry" && mt === "Normal") d1 = d1 * 0.5;
      if ((d.ab === "Multiscale" || d.ab === "Shadow Shield") && !mb) d1 = d1 * 0.5;
      if (d.ab === "Disguise" && !mb) d1 = 0;
      if (d1 >= hp && (d.item === "Focus Sash" || (META.sturdy && d.ab === "Sturdy" && !mb))) d1 = hp - 1;
      if (d1 >= hp) return 1;
      const extra = d.item === "Sitrus Berry" ? Math.floor(hp / 4) : d.item === "Oran Berry" ? 10 : d.item === "Berry Juice" ? 20 : 0;
      const heal = (d.item === "Leftovers" || (d.item === "Black Sludge" && d.t.includes("Poison"))) ? Math.floor(hp / 16) : 0;
      if (dn - heal <= 0) return 99;
      return 1 + Math.ceil((hp - d1 + extra) / (dn - heal));
    }
    const speed = (m, w) => {
      let s = m.st.sp;
      if (m.item === "Choice Scarf") s = Math.floor(s * 3 / 2);
      if (w && WSPEED[m.ab] === w) s *= 2;
      return s;
    };
    // like Python's max() over (damage, move): ties go to the later name
    // left out on the player's side: must recharge, Last Resort, moves that faint the user
    const NOUSE = new Set(["Hyper Beam", "Giga Impact", "Blast Burn", "Frenzy Plant", "Hydro Cannon", "Rock Wrecker", "Roar of Time", "Prismatic Laser",
      "Eternabeam", "Meteor Assault", "Last Resort", "Explosion", "Self-Destruct", "Selfdestruct", "Misty Explosion", "Final Gambit", "Memento",
      "Dream Eater", "Future Sight", "Doom Desire", "Focus Punch", "Fake Out", "First Impression", "Belch", "Snore"]);   // second line: only work in special situations
    const best = (a, d, intim, skip, w) => a.moves.filter(m => !skip || !skip.has(m)).reduce((b, m) => {
      const x = damage(a, d, m, intim, w);
      return !b[1] || x > b[0] || (x === b[0] && m > b[1]) ? [x, m] : b;
    }, [0, null]);
    const pyround = x => { const f = Math.floor(x), r = x - f; return r > 0.5 ? f + 1 : r < 0.5 ? f : (f % 2 ? f + 1 : f); };
    const weatherOf = (p, b) => WAB[p.ab] || b.w || "";
    function matchup(p, b) {
      const w = weatherOf(p, b);
      const [pd, pm] = best(p, b, b.ab === "Intimidate", NOUSE, w), [bd, bm] = best(b, p, p.ab === "Intimidate", null, w);
      const first = speed(p, w) >= speed(b, w);
      let win = false;
      if (pd > 0) {
        const ph = hits(p, b, pm, pd, w), bh = hits(b, p, bm, bd, w);
        win = first ? ph <= bh : ph < bh;
      }
      return [win ? 1 : 0, pm || "", pyround(pd / b.st.hp * 100 * .85 / .925), pyround(pd / b.st.hp * 100 / .925),
              bm || "", pyround(bd / p.st.hp * 100 * .85 / .925), pyround(bd / p.st.hp * 100 / .925), first ? 1 : 0];
    }
    const bossMon = m => mon(m.s, m.l, { ivs: m.iv, nature: m.n, ab: m.a, item: m.i, moves: m.m, bs: m.bs });
    // the boss team with the weather each one fights under: its own weather ability or move, else the lead's
    const bossTeam = team => {
      const ms = team.map(bossMon), own = x => WAB[x.ab] || (x.moves.map(m => WMOVE[m]).find(Boolean)) || "";
      const lead = ms.length ? own(ms[0]) : "";
      ms.forEach(x => { x.w = own(x) || lead; });
      return ms;
    };
    return { statsOf, mon, damage, best, matchup, bossMon, bossTeam, eff, hits, speed, weatherOf };
  }
  if (typeof module !== "undefined") module.exports = Model; else root.Model = Model;
})(this);
