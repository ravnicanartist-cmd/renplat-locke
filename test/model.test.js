// node test/model.test.js [renplat|bb2r] : recomputes every cell of every fight with the JavaScript model and compares it with Python's
const fs = require("fs"), path = require("path");
const games = process.argv[2] ? [process.argv[2]] : ["renplat", "bb2r", "sg", "soulgold"];
let total = 0, bad = 0;
for (const g of games) {
  const D = path.join(__dirname, "..", g, "data");
  const META = JSON.parse(fs.readFileSync(path.join(D, "meta.json")));
  const M = require("../shared/model.js")(META);
  const modes = META.modes ? Object.keys(META.modes) : [""];
  for (const mode of modes) {
    const fights = mode ? META.modes[mode].fights : META.fights;
    let n = 0;
    for (const f of fights) {
      const d = JSON.parse(fs.readFileSync(path.join(D, "fights", mode, f.key + ".json")));
      const bosses = d.team.map(M.bossMon);
      d.pool.forEach((r, i) => {
        const p = M.mon(r.s, d.cap, { ab: r.ab, moves: r.moves });
        bosses.forEach((b, j) => {
          n++;
          const a = JSON.stringify(M.matchup(p, b)), e = JSON.stringify(d.grid[i][j]);
          if (a !== e) { bad++; if (bad < 10) console.log(g, mode, f.key, r.s, b.name, "js", a, "py", e); }
        });
      });
    }
    total += n;
    console.log(`${g}${mode ? " " + mode : ""}: ${n} matchups`);
  }
}
console.log(`${total} matchups, ${bad} differences`);
process.exit(bad ? 1 : 0);
