/* Keep each game's calc box ("My Box"), frags and notes separate. The calc copies on this site share one origin, so they
   would otherwise all read the same localStorage keys. On load, the previous game's values are put aside and this game's
   are brought back. */
(function () {
  try {
    var d = (new URLSearchParams(location.search).get("data") || "").toLowerCase();
    var g = /^rupture/.test(d) || !d && /\/rupture\//.test(location.pathname) ? "rupture" : /^soulgold/.test(d) ? "soulgold"
      : /^bb2redux/.test(d) ? "bb2r" : d === "03e577af7cc9856a1f42" || /^sgss/.test(d) ? "sg" : d || "default";
    var KEYS = ["customsets", "encounters", "notes", "states", "right", "left", "toDelete"], ls = localStorage, own = ls.getItem("calcbox.owner");
    if (own === g) return;
    if (own === null) own = "rupture";            // whatever was there before this existed came from the Rupture calc
    KEYS.forEach(function (k) {
      var v = ls.getItem(k);
      if (v === null) ls.removeItem("calcbox." + own + "." + k); else ls.setItem("calcbox." + own + "." + k, v);
      var mine = ls.getItem("calcbox." + g + "." + k);
      if (mine === null) ls.removeItem(k); else ls.setItem(k, mine);
    });
    ls.setItem("calcbox.owner", g);
  } catch (e) {}
})();
