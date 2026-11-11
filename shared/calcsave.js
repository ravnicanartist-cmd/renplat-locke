/* Fill the calc's "My Box" from the save you read on the game's own page (Nuzlocke hub). The hub keeps the read save in
   localStorage under "<game>.save"; the calcs live on the same site, so they can use it directly, no second upload.
   Runs once per newly read save: builds the box, then reloads so the calc picks it up the usual way. */
(function () {
  var d = (new URLSearchParams(location.search).get("data") || "").toLowerCase();
  var store = /^soulgold/.test(d) ? "soulgold" : /^bb2redux/.test(d) || d === "945a33720dbd6bc04488" ? "bb2r"
    : d === "26138cc1d500b0cf7334" ? "rp" : d === "03e577af7cc9856a1f42" ? "sg" : null;
  if (!store) return;                                   // Emerald Rupture keeps its own .sav button
  var save;
  try { save = JSON.parse(localStorage.getItem(store + ".save") || "null"); } catch (e) { return; }
  if (!save || !save.party) return;
  var stamp = store + ":" + (save.read || "") + ":" + (save.party.length + (save.boxes || []).length);
  if (localStorage.getItem("calcsave.done") === stamp) return;
  var key = function (s) { return String(s).toLowerCase().replace(/♀/g, "f").replace(/♂/g, "m").replace(/[^a-z0-9]/g, ""); };
  var tries = 0;
  (function wait() {
    if (typeof pokedex === "undefined" || !Object.keys(pokedex).length || typeof SETDEX_BW === "undefined") {
      if (++tries < 60) setTimeout(wait, 250);
      return;
    }
    var names = {};
    Object.keys(pokedex).forEach(function (n) { names[key(n)] = n; });
    var sets = {}, missing = [];
    var ivs = function (v) { v = v || {}; return { hp: v.hp | 0, at: v.at | 0, df: v.df | 0, sa: v.sa | 0, sd: v.sd | 0, sp: v.sp | 0 }; };
    save.party.concat(save.boxes || []).forEach(function (m) {
      var n = names[key(m.name)] || names[key(String(m.name).split("-")[0])];
      if (!n) { missing.push(m.name); return; }
      if (sets[n]) return;                              // one "My Box" set per species: the party one wins
      sets[n] = { "My Box": { level: m.level, ability: m.ability, item: m.item || "", nature: m.nature, moves: (m.moves || []).slice(0, 4),
        ivs: ivs(m.ivs), evs: ivs(m.evs), nn: m.nick || "", met: m.met || "", isCustomSet: true } };
    });
    if (!Object.keys(sets).length) return;
    localStorage.setItem("customsets", JSON.stringify(sets));
    localStorage.setItem("calcsave.done", stamp);
    if (missing.length) console.log("calcsave: not in this calc:", missing);
    location.reload();
  })();
})();
