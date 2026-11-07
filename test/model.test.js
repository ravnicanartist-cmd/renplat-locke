// node test/model.test.js : recomputes every cell of every fight with the JavaScript model and compares it with Python's
const fs = require("fs"), path = require("path");
const D = path.join(__dirname, "..", "data");
const META = JSON.parse(fs.readFileSync(path.join(D, "meta.json")));
const M = require("../js/model.js")(META);
let n = 0, bad = 0;
for (const f of META.fights) {
  const d = JSON.parse(fs.readFileSync(path.join(D, "fights", f.key + ".json")));
  const bosses = d.team.map(M.bossMon);
  d.pool.forEach((r, i) => {
    const p = M.mon(r.s, d.cap, { ab: r.ab, moves: r.moves });
    bosses.forEach((b, j) => {
      n++;
      const a = JSON.stringify(M.matchup(p, b)), e = JSON.stringify(d.grid[i][j]);
      if (a !== e) { bad++; if (bad < 10) console.log(f.key, r.s, b.name, "js", a, "py", e); }
    });
  });
}
console.log(`${n} matchups, ${bad} differences`);
process.exit(bad ? 1 : 0);
