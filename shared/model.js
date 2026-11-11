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
    function damage(a, d, move, intim) {
      const m = META.moves[move];
      if (!m) return 0;
      let [mt, cat, bp] = m;
      if (META.fixed[move] != null) return eff(mt, d.t) === 0 ? 0 : (META.fixed[move] === "level" ? a.lv : META.fixed[move]);
      if (!bp || bp <= 1 || cat === "Status") return 0;
      const phys = cat === "Physical";
      let A = a.st[phys ? "at" : "sa"]; const D = d.st[phys ? "df" : "sd"];
      if (phys && (a.ab === "Huge Power" || a.ab === "Pure Power")) A *= 2;
      if (phys && intim) A = Math.floor(A * 2 / 3);
      if (a.ab === "Technician" && bp <= 60) bp *= 1.5;
      const base = Math.floor(Math.floor(Math.floor(2 * a.lv / 5 + 2) * bp * A / D) / 50) + 2;
      const stab = a.t.includes(mt) ? (a.ab === "Adaptability" ? 2 : 1.5) : 1;
      const item = META.boost[a.item] === mt ? 1.2 : a.item === "Life Orb" ? 1.3
        : ((a.item === "Choice Band" && phys) || (a.item === "Choice Specs" && !phys)) ? 1.5 : 1;
      let e = eff(mt, d.t);
      if (META.immune[d.ab] === mt) e = 0;
      if (d.ab === "Thick Fat" && (mt === "Fire" || mt === "Ice")) e *= 0.5;
      return base * 0.925 * stab * e * item * (META.multi[move] || 1);
    }
    // like Python's max() over (damage, move): ties go to the later name
    // left out on the player's side: must recharge, Last Resort, moves that faint the user
    const NOUSE = new Set(["Hyper Beam", "Giga Impact", "Blast Burn", "Frenzy Plant", "Hydro Cannon", "Rock Wrecker", "Roar of Time", "Prismatic Laser",
      "Eternabeam", "Meteor Assault", "Last Resort", "Explosion", "Self-Destruct", "Selfdestruct", "Misty Explosion", "Final Gambit", "Memento"]);
    const best = (a, d, intim, skip) => a.moves.filter(m => !skip || !skip.has(m)).reduce((b, m) => {
      const x = damage(a, d, m, intim);
      return !b[1] || x > b[0] || (x === b[0] && m > b[1]) ? [x, m] : b;
    }, [0, null]);
    const pyround = x => { const f = Math.floor(x), r = x - f; return r > 0.5 ? f + 1 : r < 0.5 ? f : (f % 2 ? f + 1 : f); };
    function matchup(p, b) {
      const [pd, pm] = best(p, b, b.ab === "Intimidate", NOUSE), [bd, bm] = best(b, p, p.ab === "Intimidate");
      const first = p.st.sp >= b.st.sp;
      let win = false;
      if (pd > 0) {
        const ph = Math.ceil(b.st.hp / pd), bh = bd > 0 ? Math.ceil(p.st.hp / bd) : 99;
        win = first ? ph <= bh : ph < bh;
      }
      return [win ? 1 : 0, pm || "", pyround(pd / b.st.hp * 100 * .85 / .925), pyround(pd / b.st.hp * 100 / .925),
              bm || "", pyround(bd / p.st.hp * 100 * .85 / .925), pyround(bd / p.st.hp * 100 / .925), first ? 1 : 0];
    }
    const bossMon = m => mon(m.s, m.l, { ivs: m.iv, nature: m.n, ab: m.a, item: m.i, moves: m.m, bs: m.bs });
    return { statsOf, mon, damage, best, matchup, bossMon, eff };
  }
  if (typeof module !== "undefined") module.exports = Model; else root.Model = Model;
})(this);
