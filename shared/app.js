/* Nuzlocke hub: tracker + Boss Prep + trainers for one game (window.GAME). Static page; everything runs in the browser. */
(() => {
  "use strict";
  const G = window.GAME;
  const $ = s => document.querySelector(s);
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const LOCAL = new Set(["sel", "tab", "show", "boxes", "pcboxes", "ttab", "tonly", "mode"]);     // per-device settings, not synced
  document.documentElement.dataset.game = G.id;
  const store = {
    get(k, d) { try { const v = localStorage.getItem(G.store + "." + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(G.store + "." + k, JSON.stringify(v)); } catch (e) { /* storage full or blocked */ }
      if (!LOCAL.has(k)) { try { localStorage.setItem(G.store + ".updated", JSON.stringify(Date.now())); } catch (e) {} Sync.later(); } }
  };
  let META, IDS, M, TXT = { ab: {}, mv: {} };
  const cache = {};
  const load = p => cache[p] || (cache[p] = fetch("data/" + p + "?v=" + (G.v || 1)).then(r => { if (!r.ok) throw new Error(p); return r.json(); }));

  // ---------------------------------------------------------------- state
  const S = { grp: store.get("grp", {}), tab: store.get("tab", "G"), sel: store.get("sel", {}), show: store.get("show", "all"), boxes: store.get("pcboxes", true),
              starter: store.get("starter", null), gender: store.get("gender", null), team: store.get("team", {}),
              mode: store.get("mode", (G.modes || [""])[0]), ttab: store.get("ttab", -1), tonly: store.get("tonly", false) };
  // one GitHub token and one private gist for every game in the hub (the old Renegade Platinum page kept it as rp.gist)
  try { if (!localStorage.getItem("hub.gist") && localStorage.getItem("rp.gist")) localStorage.setItem("hub.gist", localStorage.getItem("rp.gist")); } catch (e) {}
  const gist = { get() { try { return JSON.parse(localStorage.getItem("hub.gist") || "{}"); } catch (e) { return {}; } },
                 set(v) { try { localStorage.setItem("hub.gist", JSON.stringify(v)); } catch (e) {} } };
  let NUZ = store.get("nuz", { on: true, shiny: true, areas: {}, dead: {}, extra: [] });
  let STARS = new Set(store.get("stars", []));
  let SAVE = store.get("save", null);
  let RUNS = store.get("runs", []), PEND = null;      // run history (finished runs) and a run being logged
  const saveNuz = () => store.set("nuz", NUZ);
  const CURSAVE = () => SAVE;
  const TABS = G.tabs;
  const STARTERS = G.starters;
  const fightPath = key => G.modes ? `fights/${S.mode}/${key}.json` : `fights/${key}.json`;

  // ---------------------------------------------------------------- small helpers
  const TC = { Normal: "#9a9a7a", Fire: "#e2662f", Water: "#4f7fe0", Electric: "#d8b21c", Grass: "#5ea83f", Ice: "#6cc4c4", Fighting: "#b2322b",
    Poison: "#924396", Ground: "#c9a54a", Flying: "#8f7fe0", Psychic: "#e8507c", Bug: "#97a51e", Rock: "#a8913a", Ghost: "#6a558f",
    Dragon: "#6a3ce8", Dark: "#6a5546", Steel: "#9a9ab8", Fairy: "#d97fa6" };
  const type = t => `<span class="type" style="background:${TC[t] || "#555"}">${esc(t)}</span>`;
  const FORMSLUG = { "Rotom-Heat": "rotom-heat", "Rotom-Wash": "rotom-wash", "Rotom-Frost": "rotom-frost", "Rotom-Fan": "rotom-fan",
    "Rotom-Mow": "rotom-mow", "Wormadam-Sandy": "wormadam-sandy", "Wormadam-Trash": "wormadam-trash", "Giratina-Origin": "giratina-origin",
    "Shaymin-Sky": "shaymin-sky", "Deoxys-Attack": "deoxys-attack", "Deoxys-Defense": "deoxys-defense", "Deoxys-Speed": "deoxys-speed",
    "Basculin-Blue-Striped": "basculin-bluestriped", "Darmanitan-Zen": "darmanitan-zen", "Meloetta-Pirouette": "meloetta-pirouette",
    "Kyurem-White": "kyurem-white", "Kyurem-Black": "kyurem-black", "Keldeo-Resolute": "keldeo-resolute", "Tornadus-Therian": "tornadus-therian",
    "Thundurus-Therian": "thundurus-therian", "Landorus-Therian": "landorus-therian", "Castform-Sunny": "castform-sunny", "Castform-Rainy": "castform-rainy", "Castform-Snowy": "castform-snowy" };
  const slug = n => FORMSLUG[n] || String(n).toLowerCase().replace(/-f$/, "f").replace(/-m$/, "m").replace(/[^a-z0-9]/g, "");
  // G.sprites: a folder of sprites named like the calc's (SoulGold has Pokémon from every generation; the Gen 5 set stops at Genesect)
  const rslug = n => String(n).toLowerCase().replace(" ", "-").replace(".", "").replace(".", "").replace("’", "").replace(":", "-");
  const spr = (n, cls = "") => G.sprites
    ? `<img class="${cls}" loading="lazy" alt="" src="${G.sprites}${encodeURIComponent((META && META.mons[n] && META.mons[n].sp) || rslug(n))}.png" onerror="this.style.visibility='hidden'">`
    : `<img class="${cls}" loading="lazy" alt="" src="https://play.pokemonshowdown.com/sprites/gen5/${slug(n)}.png" onerror="this.style.visibility='hidden'">`;
  const fam = n => (META.mons[n] || {}).fam || n;
  const fightIdx = k => META.order[k];
  const CALC = (G.calcByMode ? G.calcByMode[S.mode] || Object.values(G.calcByMode)[0] : G.calc) + (G.modes && S.mode === "challenge" ? "&challengeMode=true" : "");
  const calcName = n => String(n).replace(/'/g, "\u2019");
  const calcLink = (opp, me, lv, mv, txt, olv) => opp ? `<a class="calc" target="_blank" rel="noopener" href="${CALC}&opp=${encodeURIComponent(opp)}${olv ? "&olv=" + olv : ""}${me ? `&me=${encodeURIComponent(calcName(me))}&lv=${lv}&mv=${encodeURIComponent(mv.join(","))}` : ""}">${txt || "Calc"}</a>` : "";
  // moves and abilities: type / category / power at a glance, the rest in a tooltip (hover, or tap on a phone)
  const TA = { Normal: "NOR", Fire: "FIR", Water: "WAT", Electric: "ELE", Grass: "GRA", Ice: "ICE", Fighting: "FIG", Poison: "POI", Ground: "GRO",
    Flying: "FLY", Psychic: "PSY", Bug: "BUG", Rock: "ROC", Ghost: "GHO", Dragon: "DRA", Dark: "DAR", Steel: "STE", Fairy: "FAI" };
  const CATS = { Physical: ["ph", "Physical"], Special: ["sp", "Special"], Status: ["st", "Status"] };
  function mv(n) {
    const d = META.moves[n];
    if (!d) return `<span class="mvx">${esc(n)}</span>`;
    const [t, c, bp] = d, cat = CATS[c] || ["st", c];
    return `<span class="mvx" data-tip="m:${esc(n)}"><i class="ty" style="background:${TC[t] || "#555"}">${TA[t] || esc(t)}</i>${esc(n)}${bp > 1 ? `<i class="bp">${bp}</i>` : ""}<i class="cat ${cat[0]}" title="${cat[1]}"></i></span>`;
  }
  const mvs = l => `<div class="mvs">${l.map(mv).join("")}</div>`;
  const ab = n => n ? `<span class="abx" data-tip="a:${esc(n)}">${esc(n)}</span>` : "";
  function tipHtml(k) {
    const kind = k[0], n = k.slice(2);
    if (kind === "a") return `<b>${esc(n)}</b><br>${esc(TXT.ab[n] || "No description found.")}`;
    const d = META.moves[n] || [], x = TXT.mv[n] || [];
    const [t, c, bp] = d;
    return `<b>${esc(n)}</b> ${type(t)} <span class="muted">${esc(c)}</span><br>Power ${bp > 1 ? bp : "—"} · Accuracy ${x[0] === "—" || x[0] == null ? "—" : x[0] + "%"}${x[1] ? " · " + x[1] + " PP" : ""}
      ${x[2] ? `<br>${esc(x[2])}` : ""}${x[3] ? `<br><span class="chg">Changed in this hack: ${esc(x[3])}</span>` : ""}`;
  }
  const tip = document.createElement("div"); tip.id = "tip"; document.body.appendChild(tip);
  let tipFor = null;
  function showTip(el) {
    tipFor = el; tip.innerHTML = tipHtml(el.dataset.tip); tip.style.display = "block";
    const r = el.getBoundingClientRect(), w = Math.min(340, innerWidth - 16);
    tip.style.maxWidth = w + "px";
    const tw = tip.offsetWidth, th = tip.offsetHeight;
    let x = Math.max(8, Math.min(innerWidth - tw - 8, r.left + r.width / 2 - tw / 2)), y = r.top - th - 10, below = y < 8;
    if (below) y = r.bottom + 10;
    tip.style.left = x + scrollX + "px"; tip.style.top = y + scrollY + "px";
    tip.classList.toggle("below", below); tip.style.setProperty("--ax", (r.left + r.width / 2 - x) + "px");
  }
  const hideTip = () => { tip.style.display = "none"; tipFor = null; };
  document.addEventListener("mouseover", ev => { const el = ev.target.closest && ev.target.closest("[data-tip]"); if (el && matchMedia("(hover: hover)").matches) showTip(el); });
  document.addEventListener("mouseout", ev => { const el = ev.target.closest && ev.target.closest("[data-tip]"); if (el && matchMedia("(hover: hover)").matches && !el.contains(ev.relatedTarget)) hideTip(); });
  addEventListener("scroll", () => { if (tipFor && !matchMedia("(hover: hover)").matches) hideTip(); }, { passive: true });
  const F = k => META.fights[fightIdx(k)];
  const tabsOf = k => META.fights[fightIdx(k)] && Object.keys(META.tabs).filter(t => META.tabs[t].includes(k));

  // ---------------------------------------------------------------- what you own / have caught
  const caughtFams = () => {
    const s = new Set();
    Object.values(NUZ.areas).forEach(a => { if (a.st === "caught" && a.s) s.add(fam(a.s)); });
    (NUZ.extra || []).forEach(x => s.add(fam(x.s)));
    if (SAVE) { SAVE.caught.forEach(n => s.add(fam(n))); SAVE.party.concat(SAVE.boxes).forEach(m => s.add(fam(m.name))); }
    return s;
  };
  const aliveFams = () => {
    const s = new Set();
    Object.entries(NUZ.areas).forEach(([a, r]) => { if (r.st === "caught" && r.s && !NUZ.dead[a]) s.add(fam(r.s)); });
    (NUZ.extra || []).forEach(x => { if (!x.dead) s.add(fam(x.s)); });
    if (SAVE) SAVE.party.concat(SAVE.boxes).forEach(m => s.add(fam(m.name)));
    return s;
  };
  let ALIVE = new Set(), CAUGHT = new Set(), CURSED = new Set();
  // Drayano Gauntlet: families that died, or entered the Hall of Fame, in an earlier game of the gauntlet
  function cursedFams() {
    const out = new Set();
    let g; try { g = JSON.parse(localStorage.getItem("hub.gauntlet") || "{}"); } catch (e) { g = {}; }
    if (!g.on) return out;
    const order = (g.order || []).map(x => x.id), mine = order.indexOf(G.id);
    if (mine < 0) return out;
    for (const id of order.slice(0, mine)) {
      const m = (g.manual || {})[id] || {};
      if (g.banDead !== false) (m.dead || []).forEach(n => out.add(fam(n)));
      if (g.banHof !== false) (m.hof || []).forEach(n => out.add(fam(n)));
      if (g.banDead === false) continue;
      const pre = (g.order.find(x => x.id === id) || {}).store;
      if (pre) { try { const nz = JSON.parse(localStorage.getItem(pre + ".nuz") || "null");
        if (nz) { Object.entries(nz.areas || {}).forEach(([a, r]) => { if (r.s && nz.dead && nz.dead[a]) out.add(fam(r.s)); });
          (nz.extra || []).forEach(x => { if (x.dead) out.add(fam(x.s)); }); } } catch (e) {} }
    }
    return out;
  }
  const refreshOwned = () => { ALIVE = aliveFams(); CAUGHT = caughtFams(); CURSED = cursedFams(); };
  const isMine = r => STARS.has(fam(r.s)) || (r.from || []).some(f => STARS.has(fam(f))) || ALIVE.has(fam(r.s));
  function nuzTag(r) {
    if (!NUZ.on) return null;
    const f = fam(r.s);
    if (ALIVE.has(f)) return ["boss", "Yours"];
    if (CURSED.has(f)) return ["nz-dupe", "Cursed (gauntlet)"];
    if (CAUGHT.has(f)) return ["nz-dupe", "Dupe"];
    if (!r.areas.length) return ["nz-gift", "Gift / trade (free extra)"];
    const free = r.areas.filter(a => !NUZ.areas[a]);
    return free.length ? ["nz-free", "Catch: " + free.join(", ")] : ["nz-used", "Areas used"];
  }
  // where to get it, places in Nuzlocke areas you haven't used yet first
  function whereShort(r) {
    const used = w => NUZ.on && Object.keys(NUZ.areas).some(a => NUZ.areas[a] && NUZ.areas[a].s && w.startsWith(a));
    const l = r.where.slice().sort((x, y) => used(x) - used(y));
    return l.slice(0, 2).join("; ").replace(/\(grass \((day|night|morning)\)\)/g, "(grass, $1)") + (l.length > 2 ? ` +${l.length - 2} more` : "");
  }
  const catchable = r => { const t = nuzTag(r); return t && (t[0] === "nz-free" || t[0] === "nz-gift"); };

  // ---------------------------------------------------------------- fights beaten (from the save)
  function beatenMax(SAVE = CURSAVE()) {    // the tracker's save, or the one being logged in Run history
    if (!SAVE) return -1;
    let mx = -1;
    const BADGE = G.badges || {};
    META.fights.forEach((f, i) => {
      // Renegade Platinum: flags 1360+1064 / 1360+1065 (Cheryl, Mira) are shared with other game flags, so those two are inferred
      const bc = (G.badgeCount || {})[f.key];   // SoulGold gyms 5-7: beaten once you have that many of their badges
      const hit = (f.ids || []).some(id => id !== 1064 && id !== 1065 && (SAVE.beaten || []).includes(id)) || (BADGE[f.key] && SAVE.badges.includes(BADGE[f.key]))
        || (bc && bc[0].filter(b => SAVE.badges.includes(b)).length >= bc[1]) || (f.key === G.championKey && SAVE.champion);
      if (hit) mx = Math.max(mx, i);
    });
    return mx;
  }
  const isBeaten = k => fightIdx(k) <= beatenMax();

  // ---------------------------------------------------------------- variants (starter / gender / random E4 team)
  function pickVariant(key, vars) {
    let best = 0, bs = -1;
    vars.forEach((v, i) => {
      let s = 0;
      if (v.starter && S.starter) s += v.starter === S.starter ? 4 : -9;
      if (v.gender && S.gender) s += v.gender === S.gender ? 2 : -9;
      if (v.team) s += v.team === (S.team[key] || 1) ? 1 : -9;
      if (v.leader) s += v.leader === (S.team[key] || autoLeader(vars)) ? 1 : -9;
      if (s > bs) { bs = s; best = i; }
    });
    return best;
  }
  // SoulGold gyms 5-7: Chuck, Jasmine and Pryce in any order. Default to a leader whose badge you don't have yet.
  function autoLeader(vars) {
    const L = vars.map(v => v.leader), B = G.leaderBadge || {};
    return (SAVE && L.find(l => !SAVE.badges.includes(B[l]))) || L[0];
  }
  function chips(key, vars) {
    let h = "";
    if (vars.some(v => v.leader)) h += `<span class="muted">Leader:</span>` + vars.map(v => v.leader).map(l => `<button data-leader="${l}" data-key="${key}" class="${(S.team[key] || autoLeader(vars)) === l ? "on" : ""}">${l}${SAVE && SAVE.badges.includes((G.leaderBadge || {})[l]) ? " ✓" : ""}</button>`).join("");
    if (vars.some(v => v.starter)) h += `<span class="muted">Your starter:</span>` + STARTERS.map(s => `<button data-starter="${s}" class="${S.starter === s ? "on" : ""}">${s}</button>`).join("");
    if (vars.some(v => v.gender)) h += `<span class="muted">&nbsp;You play as:</span>` + (G.genders || [["M", "a boy"], ["F", "a girl"]]).map(([g, t]) => `<button data-gender="${g}" class="${S.gender === g ? "on" : ""}">${t}</button>`).join("");
    if (vars.some(v => v.team)) h += `<span class="muted">Team (picked at random by the game):</span>` + [1, 2, 3, 4].map(n => `<button data-team="${n}" data-key="${key}" class="${(S.team[key] || 1) === n ? "on" : ""}">Team ${n}</button>`).join("");
    return h ? `<div class="chips">${h}</div>` : "";
  }

  // ---------------------------------------------------------------- the save
  function saveBar() {
    const inp = `<input type="file" id="savefile" accept=".sav,.dsv,.bin,application/octet-stream">`;
    if (!SAVE) return `<div class="savebar"><label class="savebtn">Read your save (.sav)${inp}</label>
      <span class="muted">Loads your party, PC boxes, badges, ${G.save === "pt" ? "beaten trainers, " : ""}starter and Pokédex, then jumps to your next fight. It's read in your browser; with sync on, the result is kept in your private gist.</span></div>`;
    return `<div class="savebar on"><b>${esc(SAVE.name || "Your save")}</b><span>${SAVE.gender === "F" ? "Girl" : "Boy"} · ${SAVE.badges.length} badge${SAVE.badges.length === 1 ? "" : "s"}${SAVE.starter ? " · starter " + esc(SAVE.starterMon || SAVE.starter) : ""} · ${SAVE.hours}h ${String(SAVE.minutes).padStart(2, "0")}m</span>
      <span class="muted">${SAVE.party.length} in party, ${SAVE.boxes.length} in the PC · read ${esc(new Date(SAVE.read).toLocaleString())}</span>
      <label class="savebtn small">Read again${inp}</label><button class="savebtn small" id="forget">Forget</button></div>`;
  }
  async function readFile(file) {
    const buf = await file.arrayBuffer();
    const prev = SAVE;
    SAVE = ({ b2w2: window.SaveReaderB2W2, hgss: window.SaveReaderHGSS, sgx: window.SaveReaderSGX }[G.save] || window.SaveReader).readSave(buf, IDS, META);
    store.set("save", SAVE);
    S.gender = SAVE.gender; store.set("gender", S.gender);
    const st = SAVE.starter || STARTERS.find(s => SAVE.party.concat(SAVE.boxes).some(m => fam(m.name) === s));
    if (st) { S.starter = st; store.set("starter", st); }
    S.sel = {}; store.set("sel", S.sel);
    autoFill(prev);
    // games with a difficulty setting stored in the save (SoulGold): follow it
    if (G.modes && SAVE.mode && G.modes.includes(SAVE.mode) && SAVE.mode !== S.mode) { store.set("mode", SAVE.mode); location.reload(); }
  }
  // Nuzlocke: fill areas from where your Pokémon were met; starters and gifts are free extras
  function autoFill(prev) {
    if (!NUZ.on) return;
    const giftAt = {}, wildAt = {};
    META.areas.forEach(a => a.mons.forEach(([s, an, how]) => {
      const o = ["gift", "egg", "fossil", "trade", "static"].includes(how) ? giftAt : wildAt;
      (o[a.name] = o[a.name] || new Set()).add(fam(s));
    }));
    const starterFam = SAVE.starterMon ? fam(SAVE.starterMon) : SAVE.starter ? fam(SAVE.starter) : null;
    SAVE.party.concat(SAVE.boxes).forEach(m => {
      const f = fam(m.name);
      let a = (G.metAlias || {})[m.met] || m.met;
      // an area that shares its met location with another (SoulGold: fossils revived at the Ruins of Alph lab)
      const sub = META.areas.find(x => x.met === a && x.mons.some(mm => fam(mm[0]) === f));
      if (sub) a = sub.name;
      if (!a || !META.areas.some(x => x.name === a)) return;
      if (f === starterFam) { if (!(NUZ.extra || []).some(x => fam(x.s) === f)) (NUZ.extra = NUZ.extra || []).push({ s: m.name, where: "Starter", auto: 1 }); return; }
      const wild = wildAt[a] && wildAt[a].has(f), gift = giftAt[a] && giftAt[a].has(f);
      if (gift && !wild) { if (!(NUZ.extra || []).some(x => fam(x.s) === f)) (NUZ.extra = NUZ.extra || []).push({ s: m.name, where: a, auto: 1 }); return; }
      if (m.shiny && NUZ.shiny) { if (!(NUZ.extra || []).some(x => x.pid === m.pid)) (NUZ.extra = NUZ.extra || []).push({ s: m.name, where: a + " (shiny)", pid: m.pid, auto: 1 }); return; }
      if (!NUZ.areas[a]) NUZ.areas[a] = { s: m.name, st: "caught", auto: 1 };
    });
    saveNuz();
  }
  const saveMon = m => M.mon(m.name, m.level, { ivs: m.ivs, evs: m.evs, nature: m.nature, ab: m.ability, item: m.item, moves: m.moves });

  // ---------------------------------------------------------------- Boss Prep
  let CUR = null;
  function monCard(m, extra) {
    const d = META.mons[m.s];
    return `<div class="mon">${spr(m.s)}<div class="nm">${esc(m.s)} <span class="muted">Lv ${m.l}</span></div>
      <div class="sub">${d ? d.t.map(type).join("") : ""}</div>
      <div class="sub">${ab(m.a)}${m.n ? " · " + esc(m.n) : ""}${m.i ? " · @ " + esc(m.i) : ""} · IVs ${m.iv}</div>
      ${mvs(m.m)}${extra || ""}${calcLink(m.calc, null, 0, [], "Open in the calc", m.l)}</div>`;
  }
  const cellHtml = c => `<td class="mu ${c[0] ? "w" : "l"}"><a>${c[0] ? "✓" : "✗"}</a><span>${esc(c[1] || "—")} ${c[1] ? c[2] + "–" + c[3] + "%" : ""}</span>
      <span class="muted">takes ${c[4] ? c[5] + "–" + c[6] + "%" : "nothing"}${c[7] ? "" : " · slower"}</span></td>`;
  function sentence(c, m) {
    return `<b>${c[0] ? "✓" : "✗"} vs ${esc(m.s)}</b>: ${c[7] ? "you move first" : "it moves first"}. ${c[1] ? `Your ${esc(c[1])} does ${c[2]}–${c[3]}%` : "You have no damaging move that hits it"}${c[4] ? `; its ${esc(c[4])} does ${c[5]}–${c[6]}% to you.` : "; it can't damage you."}`;
  }

  // moves that matter in a double battle
  const SPREAD = new Set(["Earthquake", "Rock Slide", "Surf", "Discharge", "Blizzard", "Heat Wave", "Muddy Water", "Dazzling Gleam", "Hyper Voice", "Icy Wind", "Bulldoze", "Lava Plume", "Sludge Wave",
    "Eruption", "Water Spout", "Razor Leaf", "Air Cutter", "Swift", "Snarl", "Electroweb", "Glaciate", "Struggle Bug", "Petal Blizzard", "Boomburst", "Explosion", "Self-Destruct", "Selfdestruct", "Magnitude",
    "Powder Snow", "Twister", "Breaking Swipe", "Parabolic Charge", "Origin Pulse", "Precipice Blades", "Diamond Storm", "Make It Rain", "Matcha Gotcha", "Mortal Spin", "Acid", "Incinerate", "Brutal Swing", "Clanging Scales", "Overdrive", "Burning Jealousy", "Disarming Voice", "Bleakwind Storm", "Sandsear Storm", "Wildbolt Storm", "Springtide Storm", "Thousand Arrows", "Land's Wrath", "Core Enforcer", "Dragon Energy", "Astral Barrage", "Glacial Lance", "Shell Trap", "Sparkling Aria", "Tera Starstorm", "Hyperspace Hole", "Silver Wind", "Ominous Wind", "Leaf Tornado", "Relic Song"]);
  const ALLY = new Set(["Earthquake", "Surf", "Discharge", "Lava Plume", "Sludge Wave", "Bulldoze", "Explosion", "Self-Destruct", "Selfdestruct", "Magnitude", "Boomburst", "Petal Blizzard", "Parabolic Charge", "Brutal Swing", "Mortal Spin", "Sparkling Aria"]);
  const SUPPORT = new Set(["Protect", "Detect", "Fake Out", "Follow Me", "Rage Powder", "Helping Hand", "Wide Guard", "Quick Guard", "Tailwind", "Trick Room", "Light Screen", "Reflect", "Aurora Veil", "Taunt", "Encore", "Spore", "Sleep Powder", "Thunder Wave", "Will-O-Wisp", "Ally Switch", "After You", "Coaching", "Life Dew", "Heal Pulse", "Decorate", "Spiky Shield", "King's Shield", "Baneful Bunker", "Rain Dance", "Sunny Day", "Sandstorm", "Hail", "Snowscape", "Perish Song", "Feint", "Imprison", "Safeguard", "Swagger", "Flatter", "Charm", "Fake Tears", "Screech", "Icy Wind", "Electroweb", "Snarl"]);
  function doublesBox(team) {
    const who = set => { const o = {}; team.forEach(m => m.m.forEach(x => { if (set.has(x)) (o[x] = o[x] || []).push(m.s); })); return Object.entries(o); };
    const sp = who(SPREAD), su = who(SUPPORT), lead = team.slice(0, 2);
    const li = (arr, f) => arr.map(([mv, ms]) => `<li>${mvs([mv])} <span class="muted">${esc([...new Set(ms)].join(", "))}${f ? f(mv) : ""}</span></li>`).join("");
    return `<div class="dblbox"><b>Double battle</b>: two of theirs face two of yours at once. The ✓ / ✗ grid below is still each Pokémon 1-on-1, so read it as "who handles what", then plan pairs.
      <div class="dblcols"><div><b>They lead with</b><div class="hteam">${lead.map(m => `<span>${spr(m.s)}${esc(m.s)} <span class="muted">Lv ${m.l}</span></span>`).join("")}</div>
      <span class="muted">Both can hit the same target in one turn: check your lead survives the two leads' best moves added together.</span></div>
      <div><b>Moves that hit both of yours</b>${sp.length ? `<ul class="ml">${li(sp, mv => ALLY.has(mv) ? " · also hits its own partner" : "")}</ul>` : `<br><span class="muted">None on this team.</span>`}</div>
      <div><b>Support moves to expect</b>${su.length ? `<ul class="ml">${li(su)}</ul>` : `<br><span class="muted">None on this team.</span>`}</div></div>
      <span class="muted">Spread moves do 75% of their usual damage when they hit two targets. Your own Protect, Fake Out, Wide Guard and spread moves are worth much more here than in singles.</span></div>`;
  }

  async function prep() {
    refreshOwned();
    const keys = META.tabs[S.tab] || META.tabs.G;
    const bmax = beatenMax();
    let key = S.sel[S.tab];
    if (!key || !keys.includes(key)) key = (SAVE && keys.find(k => fightIdx(k) > bmax)) || keys[0];
    const f = F(key), d = await load(fightPath(key));
    const vi = pickVariant(key, d.variants.map(v => v.v)), cols = d.variants[vi].cols, team = cols.map(c => d.team[c]);
    const N = d.pool.length;
    CUR = { d, cols, team, key };
    let h = `<p class="intro">Pick a fight, or read your save. The page lists every Pokémon you could have by then and works out who wins each 1-on-1 at your level cap.
      Tap ☆ on the ones you have (in a Nuzlocke, the ones you've caught are filled in from the Areas page and your save).</p>` + saveBar();
    h += `<div class="prepf tabs">` + TABS.map(([k, t]) => `<button data-tab="${k}" class="${S.tab === k ? "on" : ""}">${t}</button>`).join("") + `</div>`;
    h += `<div class="bosspick">` + keys.map(k => { const x = F(k), won = SAVE && fightIdx(k) <= bmax;
      return `<button data-k="${k}" class="${k === key ? "on" : ""} ${won ? "done" : ""} g-${S.tab === "A" ? ((tabsOf(k) || []).find(t => t !== "A") || "") : S.tab}" title="${esc(x.loc)} · cap ${x.cap}${x.kind === "double" ? " · double battle" : ""}">${won ? "✓ " : ""}${esc(x.label)}${x.kind === "double" ? ' <span class="x2">2v2</span>' : ""}</button>`; }).join("") + `</div>`;
    h += chips(key, d.variants.map(v => v.v));
    const BT = M.bossTeam(team), WN = { rain: "Rain", sun: "Harsh sun", sand: "Sandstorm", hail: "Hail / snow" };
    const kindTag = f.kind === "double" ? `<span class="tag dbl big">2 v 2 · Double battle</span>` : f.kind === "multi" ? `<span class="tag dbl">Double / multi battle: matchups are still 1-on-1</span>` : f.kind === "gauntlet" ? `<span class="tag dbl">Back-to-back fights</span>` : "";
    h += `<div class="prephead"><b>${esc(f.label)}</b> <span class="muted">${esc(f.loc)} · level cap ${d.cap} · ${N} Pokémon you could have</span>${kindTag}
      ${isBeaten(key) ? '<span class="tag boss">✓ Beaten (from your save)</span>' : ""}</div>`;
    h += `<div class="team">` + team.map((m, j) => {
      const c = cols[j], k = d.grid.filter(row => row[c][0]).length, pct = N ? Math.round(k / N * 100) : 0;
      return monCard(m, (BT[j] && BT[j].w ? `<div class="sub"><span class="tag wx" title="This Pokémon is expected to fight in this weather (its own ability or move, or the lead's). The matchups below already count it.">${WN[BT[j].w]}</span></div>` : "") + `<div class="beat"><div class="barw"><div class="fill ${pct < 20 ? "lo" : pct < 40 ? "mid" : ""}" style="width:${pct}%"></div></div><span>${k} of ${N} beat it 1-on-1</span></div>`);
    }).join("") + `</div>`;
    if (f.kind === "double" || f.kind === "multi") h += doublesBox(team);
    const notes = [f.note].concat(f.notes || []).filter(Boolean);
    if (notes.length) h += `<p class="muted">${notes.map(esc).join(" · ")}</p>`;

    // your real Pokémon
    if (SAVE) {
      const bosses = M.bossTeam(team);
      const list = SAVE.party.concat(S.boxes ? SAVE.boxes : []);
      h += `<h3 class="sec">Your Pokémon vs ${esc(f.label)}</h3>
        <p class="prepf"><label class="chk"><input type="checkbox" id="pcboxes" ${S.boxes ? "checked" : ""}> Include PC boxes</label>
        <span class="muted">Your real levels, natures, IVs, EVs, abilities, items and moves from the save.</span></p>`;
      h += `<div class="wrap"><table class="prep mine"><thead><tr><th>Pokémon</th><th class="n">Wins</th>` + team.map(m => `<th class="bm">${spr(m.s)}<br>${esc(m.s)} ${m.l}</th>`).join("") + `</tr></thead><tbody>`;
      const covered = team.map(() => false);
      list.forEach((m, k) => {
        const p = saveMon(m);
        if (!p) return;
        const cells = bosses.map(b => M.matchup(p, b)), wins = cells.filter(c => c[0]).length;
        if (m.where === "Party") cells.forEach((c, j) => { if (c[0]) covered[j] = true; });
        h += `<tr data-text="${esc((m.name + " " + m.moves.join(" ")).toLowerCase())}"><td class="pk">${spr(m.name)}<div><b>${esc(m.name)}</b> <span class="muted">Lv ${m.level}</span>
          ${m.where === "Party" ? '<span class="tag boss">Party</span>' : `<span class="tag">PC</span>`}${m.level > d.cap ? `<span class="tag over">Over the cap (${d.cap})</span>` : ""}${m.hp === 0 ? '<span class="tag over">Fainted</span>' : ""}
          <br><span class="muted">${esc(m.nature)} · ${ab(m.ability)}${m.item ? " · @ " + esc(m.item) : ""}</span>${mvs(m.moves)}</div></td>
          <td class="n"><b>${wins}</b>/${team.length}</td>${cells.map(cellHtml).join("")}</tr>`;
      });
      h += `</tbody></table></div>`;
      const gaps = team.filter((m, j) => !covered[j]);
      h += gaps.length ? `<p class="note">Nothing in your party wins 1-on-1 against ${gaps.map(m => "<b>" + esc(m.s) + "</b>").join(", ")}.</p>` : `<p class="muted">Something in your party wins 1-on-1 against every Pokémon on this team.</p>`;
    }

    // your team (stars / caught)
    const order = d.pool.map((r, i) => i).sort((a, b) => d.grid[b].reduce((s, c) => s + c[0], 0) - d.grid[a].reduce((s, c) => s + c[0], 0) || (d.pool[a].s < d.pool[b].s ? -1 : 1));
    const winsOf = i => cols.reduce((s, c) => s + d.grid[i][c][0], 0);
    order.sort((a, b) => winsOf(b) - winsOf(a) || (d.pool[a].s < d.pool[b].s ? -1 : 1));
    const mineIdx = order.filter(i => isMine(d.pool[i]));
    h += `<h3 class="sec">Your team vs ${esc(f.label)}</h3>`;
    if (!mineIdx.length) h += `<p class="muted">Tap ☆ next to the Pokémon you have in the table below${NUZ.on ? ", log catches on the Areas page," : ""} or read your save.</p>`;
    h += `<div class="cover">` + team.map((m, j) => {
      const c = cols[j], win = mineIdx.filter(i => d.grid[i][c][0]);
      let body;
      if (win.length) body = win.map(i => `${esc(d.pool[i].s)} <span class="muted">(${esc(d.grid[i][c][1])} ${d.grid[i][c][2]}–${d.grid[i][c][3]}%)</span>`).join("<br>");
      else {
        const opts = order.filter(i => !isMine(d.pool[i]) && d.grid[i][c][0] && (!NUZ.on || catchable(d.pool[i]))).slice(0, 3);
        body = `<span class="bad">None of yours wins this 1-on-1.</span>` + (opts.length ? `<br>Options you could get: ` + opts.map(i => { const r = d.pool[i], t = nuzTag(r);
          return `<br>• <b>${esc(r.s)}</b> <span class="muted">${esc(r.s !== r.from[0] ? "from " + r.from.join("/") + ", " : "")}${esc((t && t[0] === "nz-free") ? t[1] : r.where.slice(0, 2).join("; "))}</span>`; }).join("") : `<br><span class="muted">Nothing obtainable by now wins it 1-on-1 either.</span>`);
      }
      return `<div class="cv ${win.length ? "" : "gap"}">${spr(m.s)}<div><b>${esc(m.s)}</b> <span class="muted">Lv ${m.l}</span><br>${body}</div></div>`;
    }).join("") + `</div>`;

    // every Pokémon you could have
    const nNew = (d.new[S.tab] || d.new.A || []).length;
    h += `<h3 class="sec">Every Pokémon you could have by ${esc(f.label)}</h3>
      <div class="prepf"><span class="muted">Show:</span>` + [["all", "All"], ["mine", "Only mine"], ["new", `New since the last fight in this tab (${nNew})`]].concat(NUZ.on ? [["catch", "Catchable now"]] : [])
        .map(([k, t]) => `<button data-show="${k}" class="${S.show === k ? "on" : ""}">${t}</button>`).join("") + `</div>
      <p class="muted">Sorted by number of wins. Tap a row for the reasoning. ✓ means a good 1-on-1 matchup, not a guaranteed win.</p>`;
    const newSet = new Set(d.new[S.tab] || d.new.A || []);
    const shown = order.filter(i => S.show === "mine" ? isMine(d.pool[i]) : S.show === "new" ? newSet.has(i) : S.show === "catch" ? catchable(d.pool[i]) : true);
    h += `<div class="wrap"><table class="prep"><thead><tr><th></th><th>Pokémon</th><th class="n">Wins</th>` + team.map(m => `<th class="bm">${spr(m.s)}<br>${esc(m.s)} ${m.l}</th>`).join("") + `</tr></thead><tbody>`;
    shown.forEach(i => {
      const r = d.pool[i], on = isMine(r), t = nuzTag(r);
      h += `<tr class="pr" data-i="${i}" data-text="${esc((r.s + " " + r.from.join(" ") + " " + r.where.join(" ")).toLowerCase())}">
        <td><button class="star ${on ? "on" : ""}" data-f="${esc(fam(r.s))}" title="I have this one">${on ? "★" : "☆"}</button></td>
        <td class="pk">${spr(r.s)}<div><b>${esc(r.s)}</b> ${META.mons[r.s].t.map(type).join("")}${newSet.has(i) ? '<span class="tag new">New</span>' : ""}${t ? `<span class="tag ${t[0]}">${esc(t[1])}</span>` : ""}
        <br><span class="muted">${r.s !== r.from[0] || r.from.length > 1 ? "from " + esc(r.from.join(" / ")) + " · " : ""}${esc(whereShort(r))}</span></div></td>
        <td class="n"><b>${winsOf(i)}</b>/${team.length}</td>${cols.map(c => cellHtml(d.grid[i][c])).join("")}</tr>`;
    });
    if (!shown.length) h += `<tr><td colspan="${3 + team.length}" class="muted">Nothing to show with this filter.</td></tr>`;
    h += `</tbody></table></div>`;

    // what's new since the previous fight in this tab
    const sn = d.since[S.tab] || d.since.A;
    if (sn) {
      h += `<h3 class="sec">TMs and items you can get since the previous fight in this tab</h3><div class="since">
        <div><b>TMs / HMs</b><br>${sn.tm.length ? sn.tm.map(esc).join("<br>") : '<span class="muted">None new.</span>'}</div>
        <div><b>Evolution items</b><br>${sn.items.length ? sn.items.map(esc).join(", ") : '<span class="muted">None new.</span>'}</div>
        <div><b>Other</b><br>${sn.rods.concat(sn.other).length ? sn.rods.concat(sn.other).map(esc).join("<br>") : '<span class="muted">Nothing else new.</span>'}</div></div>`;
    }
    h += `<h3 class="sec">How this is worked out</h3><div class="how">${G.how(d.cap)}
      <p><b>Stats.</b> Yours: IVs 15, neutral nature, first ability, no item, no EVs. The boss: its real IVs, nature, ability, item and moves from the ROM and the documentation.</p>
      <p><b>The fight.</b> Each side uses its strongest damaging move every turn (STAB, the type chart, Huge/Pure Power, Intimidate, Technician, Thick Fat, Filter / Solid Rock, Tinted Lens, Scrappy, Mold Breaker, immunity abilities, fixed-damage and multi-hit moves). Your side never picks recharge moves, self-KO moves, Last Resort or moves that only work in special situations. Whoever is faster moves first; you win if you knock it out before it knocks you out.</p>
      <p><b>Held items.</b> The boss's item is counted: type boosters, Life Orb, Choice Band / Specs / Scarf, Muscle Band, Wise Glasses, Expert Belt, Gems, Eviolite, Assault Vest, Air Balloon, Focus Sash (survives the first hit), the berries that halve one super-effective hit, Sitrus / Oran Berry and Leftovers healing. Sturdy and Multiscale work the same way in the games that have them. Your own Pokémon read from a save use their real items too.</p>
      <p><b>Weather.</b> If a boss Pokémon (or the team's lead) sets rain, sun, sand or hail with its ability or a weather move, its matchups are worked out in that weather: Fire and Water damage, Swift Swim / Chlorophyll / Sand Rush speed, Rock types' Special Defense in sand, Weather Ball, Solar Power. A weather ability on your own Pokémon replaces it.</p>
      <p><b>Not modelled:</b> status moves, stat boosts and setup, switching, critical hits, accuracy, priority moves, two-turn moves, Trick Room / Tailwind, and the AI's choices. Double battles are still shown 1-on-1. So ✓ means a good 1-on-1 matchup, not a guaranteed win, and "X of N beat it" is the share of the Pokémon you could have that win that matchup.</p></div>`;
    return h;
  }
  function prepDetail(tr) {
    const nx = tr.nextElementSibling;
    if (nx && nx.classList.contains("det")) { nx.remove(); return; }
    const { d, cols, team } = CUR, i = +tr.dataset.i, r = d.pool[i];
    tr.insertAdjacentHTML("afterend", `<tr class="det"><td colspan="${3 + team.length}"><div class="cols">
      <div><b>Matchups at level ${d.cap}</b><ul class="ml">${cols.map((c, j) => { const g = d.grid[i][c], mv = [g[1]].concat(r.moves.filter(x => x !== g[1])).filter(Boolean).slice(0, 4);
        return `<li>${sentence(g, team[j])} ${calcLink(team[j].calc, r.s, d.cap, mv, null, team[j].l)}</li>`; }).join("")}</ul></div>
      <div><b>Moves counted</b> <span class="muted">(ability ${ab(r.ab)})</span><br>${r.moves.length ? mvs(r.moves) : '<span class="muted">No damaging moves.</span>'}
      <br><br><b>Where</b><br>${r.where.map(esc).join("<br>")}</div></div></td></tr>`);
  }

  // ---------------------------------------------------------------- Areas (Nuzlocke)
  function areaGroups() {
    const g = [];
    META.areas.forEach(a => {
      if (a.split) { const title = `${a.split} split (level cap ${META.caps[a.split]})`; let grp = g.find(x => x.title === title); if (!grp) g.push(grp = { title, areas: [] }); grp.areas.push(a); return; }
      const gi = a.gate == null ? 999 : a.gate;
      const nextBoss = META.fights.slice(gi + 1).find(f => (G.leaders || []).includes(f.key));
      const title = gi === 999 ? "After the Elite Four" : nextBoss ? `Before ${nextBoss.label.replace(/ \+.*/, "")} (cap ${nextBoss.cap})` : "Late game";
      let grp = g.find(x => x.title === title);
      if (!grp) g.push(grp = { title, areas: [] });
      grp.areas.push(a);
    });
    return g;
  }
  function run() {
    refreshOwned();
    const used = Object.values(NUZ.areas).filter(a => a.st).length, dead = Object.keys(NUZ.dead).length;
    let h = `<p class="intro">Your Nuzlocke, area by area in story order. Log the first encounter in each area. Families you've already caught are struck through (dupes clause)${NUZ.shiny ? "; shinies go in the extras as the shiny clause allows" : ""}. Gifts, starters and trades are free extras. Reading your save fills in areas from where each of your Pokémon was met.</p>
      ${saveBar()}<div class="sum"><b>${used}</b> areas used · <b>${ALIVE.size}</b> families alive · <b>${dead}</b> dead · <label class="chk"><input type="checkbox" id="nzon" ${NUZ.on ? "checked" : ""}> Nuzlocke mode</label></div>`;
    const FREE = ["gift", "egg", "fossil", "trade", "static"], bmaxR = SAVE ? beatenMax() : 1e9;
    h += `<p class="prepf"><button class="btn small" data-grpall="1">Open all</button> <button class="btn small" data-grpall="0">Close all</button> <span class="muted">Tap a Pokémon to log it as the area's catch; tap it again to undo.</span></p>`;
    areaGroups().forEach(g => {
      const gUsed = g.areas.filter(a => (NUZ.areas[a.name] || {}).st).length, gLeft = g.areas.filter(a => !(NUZ.areas[a.name] || {}).st && a.mons.some(m => !FREE.includes(m[2]))).length;
      const reached = g.areas.some(a => a.split ? true : (a.gate == null ? false : a.gate <= bmaxR));
      const isOpen = S.grp[g.title] != null ? S.grp[g.title] : (reached && (gLeft > 0 || !SAVE));
      h += `<details class="grp" data-g="${esc(g.title)}" ${isOpen ? "open" : ""}><summary>${esc(g.title)} <span class="gcount">${gUsed} used${gLeft ? ` · <b>${gLeft} open</b>` : ""}</span></summary>`;
      g.areas.forEach(a => {
        // one entry per species and method; times of day (morning / day / night) are merged into one label
        const byKey = new Map();
        a.mons.forEach(m => { const base = m[2].replace(/ \((morning|day|evening|night)\)$/, ""), t = (/\((morning|day|evening|night)\)$/.exec(m[2]) || [])[1], k = m[0] + "|" + base;
          const e = byKey.get(k) || byKey.set(k, [m[0], m[1], base, m[3], m[4], new Set()]).get(k); if (t) e[5].add(t); });
        const mons = [...byKey.values()].map(e => [e[0], e[1], e[5].size && e[5].size < 3 ? `${e[2]} (${[...e[5]].join(", ")})` : e[2], e[3], e[4]]);
        const r = NUZ.areas[a.name] || {}, wild = mons.filter(m => !["gift", "egg", "fossil", "trade", "static"].includes(m[2])), gifts = mons.filter(m => !wild.includes(m));
        const specs = [...new Set(wild.map(m => m[0]).concat(r.st === "caught" && r.s ? [r.s] : []))];   // an evolved catch from the save stays selectable
        const opts = specs.map(s => `<option value="${esc(s)}" ${r.s === s ? "selected" : ""}>${esc(s)}${CURSED.has(fam(s)) && r.s !== s ? " (cursed)" : CAUGHT.has(fam(s)) && r.s !== s ? " (dupe)" : ""}</option>`).join("");
        const isDead = NUZ.dead[a.name];
        h += `<div class="area ${r.st === "caught" ? (isDead ? "dead" : "used") : r.st ? "fail" : ""}" data-text="${esc((a.name + " " + specs.join(" ")).toLowerCase())}">
          <div class="ah"><b>${esc(a.name)}</b>${r.auto ? '<span class="tag">from your save</span>' : ""}${isDead ? '<span class="tag over">Dead</span>' : ""}
          ${wild.length ? `<span class="ast">${r.st === "caught" ? `Caught <b>${esc(r.s)}</b>` : r.st === "failed" ? "Failed (fainted / fled)" : r.st === "skip" ? "Skipped" : '<span class="muted">Not used yet</span>'}</span>
            <span class="acts2"><button class="btn small ${r.st === "failed" ? "on" : ""}" data-ast="failed" data-a="${esc(a.name)}">Failed</button><button class="btn small ${r.st === "skip" ? "on" : ""}" data-ast="skip" data-a="${esc(a.name)}">Skip</button>
            ${r.st === "caught" ? `<button class="btn small ${isDead ? "" : "red"}" data-dead="${esc(a.name)}">${isDead ? "Undo death" : "It died"}</button>` : ""}</span>` : '<span class="muted">Gifts only</span>'}</div>
          <div class="enc pick">${wild.map(m => `<button class="${(CAUGHT.has(fam(m[0])) || CURSED.has(fam(m[0]))) && r.s !== m[0] ? "dupe" : ""} ${r.st === "caught" && r.s === m[0] ? "on" : ""}" data-pick="${esc(m[0])}" data-a="${esc(a.name)}" title="${esc(m[1])}${CAUGHT.has(fam(m[0])) && r.s !== m[0] ? " · dupe: you already have this family" : ""}">${spr(m[0])}${esc(m[0])} <span class="muted">${esc(m[2])}</span></button>`).join("")}${r.st === "caught" && r.s && !wild.some(m => m[0] === r.s) ? `<button class="on" data-pick="${esc(r.s)}" data-a="${esc(a.name)}">${spr(r.s)}${esc(r.s)} <span class="muted">yours</span></button>` : ""}</div>
          ${gifts.length ? `<div class="enc">${gifts.map(m => `<span title="${esc(m[1])}">${spr(m[0])}${esc(m[0])} <span class="muted">${esc(m[2])} · free</span></span>`).join("")}</div>` : ""}
          ${(G.repel || {})[a.name] ? `<div class="repel"><b>Repel trick</b> (lead with this level and use a Repel): ${G.repel[a.name].map(esc).join("; ")}</div>` : ""}</div>`;
      });
      h += `</details>`;
    });
    return h;
  }

  // ---------------------------------------------------------------- Trainers (every team, split by split)
  async function trainers() {
    const T = (await load("trainers.json"))[G.modes ? S.mode : "all"];
    const bmax = beatenMax();
    // open on the split you're in: the first one whose leader isn't beaten yet
    let ti = S.ttab;
    if (ti < 0 || ti >= T.length) { ti = SAVE ? T.findIndex(x => { const f = META.fights.find(f => f.split === x.split && (G.leaders || []).includes(f.key)); return !f || fightIdx(f.key) > bmax; }) : 0; if (ti < 0) ti = T.length - 1; }
    const sp = T[ti];
    let h = `<p class="intro">Every trainer's team, split by split, in the order you meet them${G.modes ? ` (${S.mode} mode)` : ""}. Red edge: you have to fight them. Move chips show type, power and physical / special / status; hover or tap a move or an ability for what it does in this game. ${G.trainersNote || ""}</p>`;
    h += `<div class="prepf tabs ttabs">` + T.map((x, i) => `<button data-ttab="${i}" class="${i === ti ? "on" : ""}">${esc(x.label || x.split)} <span class="muted">${x.cap}</span></button>`).join("") + `</div>`;
    const mine = S.starter;
    const list = sp.trainers.filter(t => !S.tonly || t.mand);
    const nm = sp.trainers.filter(t => t.mand).length;
    h += `<div class="prephead"><b>${esc(sp.label || sp.split)} split</b> <span class="muted">level cap ${sp.cap} · ${sp.trainers.length} trainers, ${nm} you have to fight</span>
      <label class="chk"><input type="checkbox" id="tonly" ${S.tonly ? "checked" : ""}> Only the ones you have to fight</label></div>`;
    let loc = null;
    list.forEach(t => {
      const pick = (t.notes || []).map(n => /If you chose (\w+)/.exec(n)).find(Boolean);
      if (pick && mine && !mine.startsWith(pick[1])) return;   // rival teams for the other starters
      if (t.loc !== loc) { loc = t.loc; h += `<h3 class="sec tloc">${esc(loc)}</h3>`; }
      const tags = (t.mand ? '<span class="tag over">Must fight</span>' : '<span class="tag">Optional</span>') + (t.partner ? '<span class="tag dbl">Your partner</span>' : "")
        + (t.ai & 128 ? '<span class="tag dbl">Double battle</span>' : "")
        + (t.ai == null ? "" : G.aiLabels ? ((t.ai & 6) === 6 ? `<a class="tag ai" href="#ai" title="${G.aiLabels[0][1]}">${G.aiLabels[0][0]}</a>` : `<a class="tag" href="#ai" title="${G.aiLabels[1][1]}">${G.aiLabels[1][0]}</a>`)
          : (t.ai & 6) === 6 ? '<a class="tag ai" href="#ai" title="AI flags 1 + 2: looks for KOs and plays around your team">Smart AI</a>'
          : t.ai & 6 ? '<a class="tag ai" href="#ai">Partly smart AI</a>' : '<a class="tag" href="#ai" title="Picks any move that has an effect">Basic AI</a>');
      h += `<div class="trainer ${t.mand ? "mand" : ""} ${t.partner ? "partner" : ""}" data-text="${esc((t.name + " " + t.loc + " " + t.team.map(m => m.s + " " + m.m.join(" ")).join(" ")).toLowerCase())}">
        <div class="th"><b>${esc(t.name)}</b>${tags}${(t.notes || []).length ? ` <span class="muted">${esc(t.notes.join(" · "))}</span>` : ""}</div>
        <div class="tteam">${t.team.map(m => { const d = META.mons[m.s];
          return `<div class="tm">${spr(m.s)}<div><b>${esc(m.s)}</b> <span class="muted">Lv ${m.l}</span><div class="sub">${d ? d.t.map(type).join("") : ""}</div>
          <span class="muted">${ab(m.a)}${m.n ? " · " + esc(m.n) : ""}${m.i ? ` · @ ${esc(m.i)}` : ""}</span>${mvs(m.m)}${calcLink(m.calc, null, 0, [], "Calc", m.l)}</div></div>`; }).join("")}</div></div>`;
    });
    if (!list.length) h += `<p class="muted">Nobody to show.</p>`;
    return h;
  }

  // ---------------------------------------------------------------- Enemy AI notes
  const ai = () => G.ai || `<p class="muted">No notes for this game.</p>`;

  // ---------------------------------------------------------------- Box & graveyard
  function box() {
    refreshOwned();
    const byFam = {};
    if (SAVE) SAVE.party.concat(SAVE.boxes).forEach(m => { (byFam[fam(m.name)] = byFam[fam(m.name)] || []).push(m); });
    const rows = Object.entries(NUZ.areas).filter(([a, r]) => r.st === "caught" && r.s).map(([a, r]) => ({ area: a, s: r.s, dead: !!NUZ.dead[a] }))
      .concat((NUZ.extra || []).map((x, i) => ({ area: x.where, s: x.s, dead: !!x.dead, extra: i })));
    const card = x => { const sv = (byFam[fam(x.s)] || [])[0];
      const n = sv ? sv.name : x.s;
      return `<div class="card" data-text="${esc((n + " " + x.area).toLowerCase())}">${spr(n)}<div><b>${esc(n)}</b> ${sv ? `<span class="muted">Lv ${sv.level} · ${esc(sv.where)}</span>` : ""}${sv && sv.hp === 0 ? '<span class="tag over">Fainted in party</span>' : ""}
        <br><span class="muted">${esc(x.area)}${x.extra != null ? " · extra" : ""}</span>${sv ? `<br><span class="muted">${esc(sv.nature)} · ${ab(sv.ability)}</span>${mvs(sv.moves)}` : ""}</div>
        <div class="acts"><button class="btn ${x.dead ? "" : "red"}" ${x.extra != null ? `data-xdead="${x.extra}"` : `data-dead="${esc(x.area)}"`}>${x.dead ? "Revive (undo)" : "It died"}</button></div></div>`; };
    const alive = rows.filter(x => !x.dead), dead = rows.filter(x => x.dead);
    let h = `<p class="intro">Everything you've caught in this run. Mark a Pokémon dead when it faints; it moves to the graveyard and its area stays used.</p>${saveBar()}`;
    if (SAVE) {
      const tracked = new Set(rows.map(x => fam(x.s)));
      const fainted = SAVE.party.filter(m => m.hp === 0);
      const missing = alive.filter(x => !byFam[fam(x.s)]);
      if (fainted.length || missing.length) h += `<div class="sum"><b>From your save</b><ul>${fainted.map(m => `<li>${esc(m.name)} has 0 HP in your party.</li>`).join("")}
        ${missing.map(x => `<li>${esc(x.s)} (${esc(x.area)}) isn't in your party or boxes. Did it die or get released?</li>`).join("")}</ul></div>`;
      const untracked = SAVE.party.concat(SAVE.boxes).filter(m => !tracked.has(fam(m.name)));
      if (untracked.length) h += `<p class="muted">In your save but not logged: ${untracked.map(m => esc(m.name) + " (" + esc(m.met || "?") + ")").join(", ")}.</p>`;
    }
    h += `<h3 class="sec">Alive (${alive.length})</h3><div class="boxg">${alive.map(card).join("") || '<p class="muted">Nothing logged yet. Use the Areas page or read your save.</p>'}</div>`;
    h += `<h3 class="sec">Graveyard (${dead.length})</h3><div class="boxg">${dead.map(card).join("") || '<p class="muted">Nobody yet.</p>'}</div>`;
    return h;
  }

  // ---------------------------------------------------------------- Pokédex
  function dex() {
    const where = {};
    META.areas.forEach(a => a.mons.forEach(([s, an, how]) => { (where[s] = where[s] || new Set()).add(`${an} (${how})`); }));
    const ev = {};
    Object.entries(META.evos).forEach(([a, l]) => l.forEach(e => { (ev[a] = ev[a] || []).push(`→ ${e.to} (${e.kind === "level" ? "Lv " + e.p : e.kind === "friendship" ? "friendship" : e.kind === "move" ? "level up knowing " + e.p : e.kind === "place" ? "level up in " + e.p : e.p})`); }));
    let h = `<p class="intro">${G.dexIntro}</p>
      <div class="wrap"><table class="dex"><thead><tr><th></th><th>#</th><th>Pokémon</th><th>Types</th><th class="n">HP</th><th class="n">Atk</th><th class="n">Def</th><th class="n">SpA</th><th class="n">SpD</th><th class="n">Spe</th><th class="n">Total</th><th>Abilities</th></tr></thead><tbody>`;
    Object.entries(META.mons).forEach(([n, d]) => {
      const w = [...(where[n] || [])];
      h += `<tr class="row" data-text="${esc((n + " " + d.t.join(" ") + " " + d.ab.join(" ") + " " + w.join(" ")).toLowerCase())}"><td>${spr(n)}</td><td class="muted">${d.no}</td><td><b>${esc(n)}</b>
        ${ev[n] ? `<br><span class="muted">${esc(ev[n].join(", "))}</span>` : ""}${w.length ? `<br><span class="muted">${esc(w.slice(0, 4).join("; "))}${w.length > 4 ? "…" : ""}</span>` : ""}</td>
        <td>${d.t.map(type).join("")}</td>${d.bs.map(x => `<td class="n">${x}</td>`).join("")}<td class="n"><b>${d.bs.reduce((a, b) => a + b, 0)}</b></td><td>${d.ab.filter(a => a && a.trim() !== "-").map(ab).join(" / ")}</td></tr>`;
    });
    return h + `</tbody></table></div>`;
  }

  // ---------------------------------------------------------------- Run history (finished runs, for your own stats)
  const RESULTS = { wipe: ["Wiped", "over"], won: ["Beat the game", "boss"], quit: ["Stopped", ""] };
  const readerFor = () => ({ b2w2: window.SaveReaderB2W2, hgss: window.SaveReaderHGSS, sgx: window.SaveReaderSGX }[G.save] || window.SaveReader);
  function trackerDeaths() {
    const out = [];
    Object.keys(NUZ.dead || {}).forEach(a => { const r = NUZ.areas[a]; if (r && r.s) out.push(r.s + " (" + a + ")"); });
    (NUZ.extra || []).forEach(x => { if (x.dead) out.push(x.s + " (" + (x.where || "extra") + ")"); });
    return out;
  }
  function hist() {
    let h = `<p class="intro">Log each run when it ends: read the save from that moment, say where it ended, and it's kept here (and in your gist, with sync on). Deaths come from the "It died" buttons on the Nuzlocke and Box pages; you can change the number before saving.</p>`;
    h += `<h3 class="sec">Log a finished run</h3><div class="sum">`;
    if (!PEND) {
      h += `<label class="savebtn">Read the save from this run (.sav)<input type="file" id="histsave" accept=".sav,.dsv,.bin,application/octet-stream"></label>
        ${SAVE ? ` <button class="btn" id="histcur">Use the save already read (${esc(SAVE.name || "save")}, ${SAVE.badges.length} badges, ${SAVE.hours}h ${String(SAVE.minutes).padStart(2, "0")}m)</button>` : ""}
        <p class="muted">The save is only read for this log; your tracker isn't changed.</p>`;
    } else {
      const sv = PEND, bi = beatenMax(sv), next = META.fights[bi + 1], dl = trackerDeaths();
      h += `<p><b>${esc(sv.name || "Your save")}</b> · ${sv.badges.length} badge${sv.badges.length === 1 ? "" : "s"} · ${sv.hours}h ${String(sv.minutes).padStart(2, "0")}m${sv.mode ? " · " + esc(sv.mode) : G.modes ? " · " + esc(S.mode) : ""} · ${sv.party.length} in party, ${sv.boxes.length} in the PC</p>
        <div class="hteam">${sv.party.map(m => `<span>${spr(m.name)}${esc(m.name)} <span class="muted">Lv ${m.level}</span></span>`).join("")}</div>
        <p><label>How it ended <select class="field" id="hres">${Object.entries(RESULTS).map(([k, v]) => `<option value="${k}">${v[0]}</option>`).join("")}</select></label>
        <label>Where <select class="field" id="hwhere">${(() => { const gs = []; META.fights.forEach(f => { const k = f.split || ""; let g = gs.find(x => x[0] === k); if (!g) gs.push(g = [k, []]); g[1].push(f); });
          return gs.map(([k, fs]) => `<optgroup label="${esc(k ? k + " split" : "Fights")}">${fs.map(f => `<option value="${esc(f.key)}" ${next && f.key === next.key ? "selected" : ""}>${esc(f.label)}</option>`).join("")}</optgroup>`).join(""); })()}<option value="">Somewhere else</option></select></label></p>
        <p><input class="field" id="hnote" placeholder="Where exactly / notes (e.g. Route 42, wild Gyarados crit)" style="width:min(520px,100%)">
        <label>Deaths <input class="field" id="hdeaths" type="number" min="0" value="${dl.length}" style="width:70px"></label></p>
        ${dl.length ? `<p class="muted">Logged deaths: ${esc(dl.join(", "))}</p>` : ""}
        <p><label class="chk"><input type="checkbox" id="hclear"> Also clear the Nuzlocke tracker and the read save for a new run</label></p>
        <button class="btn pri" id="hsave">Save to history</button> <button class="btn" id="hcancel">Cancel</button>`;
    }
    h += `</div>`;
    const runs = RUNS.slice().sort((a, b) => b.date - a.date);
    h += `<h3 class="sec">Your runs (${runs.length})</h3>`;
    if (!runs.length) return h + `<p class="muted">Nothing logged yet.</p>`;
    const wipes = runs.filter(r => r.result === "wipe"), cnt = {};
    wipes.forEach(r => { const k = r.whereLabel || r.note || "?"; cnt[k] = (cnt[k] || 0) + 1; });
    const top = Object.entries(cnt).sort((a, b) => b[1] - a[1])[0];
    const avg = k => (runs.reduce((a, r) => a + (r[k] || 0), 0) / runs.length);
    h += `<div class="sum"><b>${runs.length}</b> run${runs.length === 1 ? "" : "s"} · <b>${wipes.length}</b> wipe${wipes.length === 1 ? "" : "s"} · <b>${runs.filter(r => r.result === "won").length}</b> won
      · ${avg("badges").toFixed(1)} badges on average · ${avg("deaths").toFixed(1)} deaths on average${top ? ` · most wipes: <b>${esc(top[0])}</b> (${top[1]})` : ""}
      · longest: ${(m => `${m / 60 | 0}h ${String(m % 60).padStart(2, "0")}m`)(Math.max(...runs.map(r => r.hours * 60 + r.minutes)))}</div>`;
    h += `<div class="wrap"><table class="hist"><thead><tr><th>Date</th><th>Ended</th><th>Where</th><th class="n">Badges</th><th class="n">Time</th><th class="n">Deaths</th><th>Team</th><th></th></tr></thead><tbody>`;
    runs.forEach(r => {
      const res = RESULTS[r.result] || ["?", ""];
      h += `<tr data-text="${esc([r.whereLabel, r.note, r.mode].concat(r.party.map(m => m.name)).join(" ").toLowerCase())}">
        <td>${esc(new Date(r.date).toLocaleDateString())}${r.mode ? `<br><span class="muted">${esc(r.mode)}</span>` : ""}</td><td><span class="tag ${res[1]}">${res[0]}</span></td>
        <td>${esc(r.whereLabel || "")}${r.note ? `<br><span class="muted">${esc(r.note)}</span>` : ""}</td><td class="n">${r.badges}</td><td class="n">${r.hours}h ${String(r.minutes).padStart(2, "0")}m</td>
        <td class="n">${r.deaths}${r.dead && r.dead.length ? `<br><span class="muted" title="${esc(r.dead.join(", "))}">who?</span>` : ""}</td>
        <td><details><summary class="hteam">${r.party.map(m => `<span>${spr(m.name)}<span class="muted">${m.level}</span></span>`).join("")}</summary>
          <ul class="ml">${r.party.map(m => `<li><b>${esc(m.name)}</b> Lv ${m.level} · ${esc(m.nature || "")} · ${ab(m.ability)}${m.item ? " · @ " + esc(m.item) : ""}${mvs(m.moves || [])}</li>`).join("")}</ul>
          <p class="muted">${r.pc} in the PC · ${r.areas} areas used${r.dead && r.dead.length ? " · died: " + esc(r.dead.join(", ")) : ""}</p></details></td>
        <td><button class="btn small red" data-delrun="${esc(r.id)}">Delete</button></td></tr>`;
    });
    return h + `</tbody></table></div>`;
  }
  function saveRun() {
    const sv = PEND, k = $("#hwhere").value, f = META.fights.find(x => x.key === k), dl = trackerDeaths();
    const run = { id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), date: Date.now(), game: G.id, mode: sv.mode || (G.modes ? S.mode : ""),
      result: $("#hres").value, where: k, whereLabel: f ? f.label : "", note: $("#hnote").value.trim(), deaths: Math.max(0, +$("#hdeaths").value || 0), dead: dl,
      name: sv.name, badges: sv.badges.length, hours: sv.hours, minutes: sv.minutes, starter: sv.starterMon || sv.starter || S.starter || "",
      party: sv.party.map(m => ({ name: m.name, nick: m.nick || "", level: m.level, nature: m.nature, ability: m.ability, item: m.item, moves: m.moves })),
      pc: sv.boxes.length, areas: Object.values(NUZ.areas).filter(a => a.st === "caught").length };
    RUNS.push(run); store.set("runs", RUNS);
    if ($("#hclear").checked) { NUZ = { on: NUZ.on, shiny: NUZ.shiny, areas: {}, dead: {}, extra: [] }; saveNuz(); SAVE = null; store.set("save", null); }
    PEND = null;
  }

  // ---------------------------------------------------------------- Save & sync
  function data() {
    const g = gist.get();
    let h = `<p class="intro">Read your save, keep your run in sync between devices, and back it up.</p>${saveBar()}`;
    if (SAVE) {
      const won = META.fights.filter((f, i) => i <= beatenMax());
      h += `<div class="sum"><b>What the save reader found</b><ul>
        <li>Trainer ${esc(SAVE.name)} (${SAVE.gender === "F" ? "girl" : "boy"}), ID ${SAVE.tid}, play time ${SAVE.hours}h ${SAVE.minutes}m${!SAVE.block || SAVE.block === "main" ? "" : ` (from the ${SAVE.block} save copy, the newer one)`}</li>
        <li>Badges: ${SAVE.badges.length ? SAVE.badges.map(esc).join(", ") : "none"}</li>
        <li>Starter: ${esc(SAVE.starterMon ? SAVE.starterMon + (SAVE.starter ? " (" + SAVE.starter + ")" : "") : SAVE.starter || "not chosen yet")}</li>${SAVE.mode ? `<li>Difficulty: ${esc(SAVE.mode)}${SAVE.caps ? " · level caps: " + esc(SAVE.caps) : ""}</li>` : ""}
        <li>Party: ${SAVE.party.length ? SAVE.party.map(m => `${esc(m.name)} Lv ${m.level} (${esc(m.moves.join(", "))})`).join("; ") : "empty"}</li>
        <li>PC boxes: ${SAVE.boxes.length} Pokémon</li><li>Pokédex: ${SAVE.caught.length} caught</li>
        <li>Story fights won: ${won.length ? esc(won.map(f => f.label).join(", ")) : "none yet"}</li></ul></div>`;
    }
    h += `<h3 class="sec">Rules</h3><div class="sum"><label class="chk"><input type="checkbox" id="nzon" ${NUZ.on ? "checked" : ""}> Nuzlocke mode (first encounter per area, dupes clause)</label><br>
      <label class="chk"><input type="checkbox" id="nzshiny" ${NUZ.shiny ? "checked" : ""}> Shiny clause (shinies don't use the area)</label>
      <p class="muted">Your other rules (no resets, set mode, no items in battle, level caps) aren't something the page can check, except the caps: Pokémon over the cap are tagged in Boss Prep.</p></div>`;
    h += `<h3 class="sec">Sync between devices (private gist)</h3><div class="sum">
      <p class="muted">Keeps your run, stars and the last save you read in a private gist on your GitHub account. Make a token at GitHub → Settings → Developer settings → Personal access tokens → Fine-grained, with only "Gists: read and write", then paste it here on each device. The token stays on this device.</p>
      <input class="field" id="gtoken" type="password" placeholder="GitHub token" value="${esc(g.token || "")}" style="width:280px"> <button class="btn pri" id="gsave">Save token and sync</button>
      ${g.token ? `<button class="btn" id="gpull">Pull from gist</button><button class="btn" id="gpush">Push to gist</button><button class="btn red" id="gforget">Stop syncing on this device</button>` : ""}
      <p class="muted" id="gstat">${esc(Sync.status)}</p></div>`;
    h += `<h3 class="sec">Backup</h3><div class="sum"><button class="btn" id="bdown">Download a backup</button> <label class="btn">Restore a backup<input type="file" id="bup" accept=".json" style="display:none"></label>
      <button class="btn red" id="reset">Start a new run</button></div>`;
    return h;
  }

  // ---------------------------------------------------------------- gist sync
  const Sync = {
    status: "", t: null,
    blob() { let ga = null; try { ga = JSON.parse(localStorage.getItem("hub.gauntlet") || "null"); } catch (e) {}
      return { v: 1, game: G.id, updated: store.get("updated", 0), nuz: NUZ, stars: [...STARS], save: SAVE, starter: S.starter, gender: S.gender, team: S.team, gauntlet: ga, runs: RUNS }; },
    apply(b) {
      try { const here = JSON.parse(localStorage.getItem("hub.gauntlet") || "null");
        if (b.gauntlet && (!here || (b.gauntlet.updated || 0) > (here.updated || 0))) localStorage.setItem("hub.gauntlet", JSON.stringify(b.gauntlet)); } catch (e) {}
      NUZ = b.nuz || NUZ; STARS = new Set(b.stars || []); SAVE = b.save || null;
      if (b.runs) { const ids = new Set(RUNS.map(r => r.id)); RUNS = RUNS.concat(b.runs.filter(r => !ids.has(r.id))); }   // run history: keep runs from both sides
      S.starter = b.starter || S.starter; S.gender = b.gender || S.gender; S.team = b.team || S.team;
      const put = (k, v) => { try { localStorage.setItem(G.store + "." + k, JSON.stringify(v)); } catch (e) {} };
      put("nuz", NUZ); put("stars", [...STARS]); put("save", SAVE); put("starter", S.starter); put("gender", S.gender); put("team", S.team); put("runs", RUNS); put("updated", b.updated || Date.now());
    },
    async api(method, url, body) {
      const g = gist.get();
      const r = await fetch("https://api.github.com" + url, { method, headers: { Authorization: "Bearer " + g.token, Accept: "application/vnd.github+json", ...(body ? { "Content-Type": "application/json" } : {}) }, body: body ? JSON.stringify(body) : undefined });
      if (!r.ok) throw new Error("GitHub said " + r.status);
      return r.json();
    },
    async find() {
      const g = gist.get();
      if (g.id) return g.id;
      const list = await this.api("GET", "/gists?per_page=100");
      const hit = list.find(x => x.files && x.files[G.gist]) || list.find(x => (x.description || "").startsWith("Nuzlocke hub"));
      if (hit) { g.id = hit.id; gist.set(g); }
      return g.id;
    },
    async push() {
      const g = gist.get();
      if (!g.token) return;
      const files = { [G.gist]: { content: JSON.stringify(this.blob()) } };
      const id = await this.find();
      if (id) await this.api("PATCH", "/gists/" + id, { files });
      else { const r = await this.api("POST", "/gists", { description: "Nuzlocke hub", public: false, files }); g.id = r.id; gist.set(g); }
      this.status = "Pushed " + new Date().toLocaleTimeString();
    },
    async pull(force) {
      const g = gist.get();
      if (!g.token) return false;
      const id = await this.find();
      if (!id) { this.status = "No gist yet; it'll be made on the first push."; return false; }
      const r = await this.api("GET", "/gists/" + id);
      const f = r.files[G.gist];
      if (!f) { this.status = "Nothing for this game in the gist yet."; return false; }
      let txt = f.content;
      if (f.truncated) txt = await (await fetch(f.raw_url)).text();
      const b = JSON.parse(txt);
      if (force || (b.updated || 0) > store.get("updated", 0)) { this.apply(b); this.status = "Pulled " + new Date().toLocaleTimeString(); return true; }
      this.status = "Up to date " + new Date().toLocaleTimeString();
      return false;
    },
    later() { if (!gist.get().token) return; clearTimeout(this.t); this.t = setTimeout(() => this.push().catch(e => { this.status = "Sync failed: " + e.message; }), 2500); }
  };

  // ---------------------------------------------------------------- shell
  const PAGES = { prep, run, box, dex, data, trainers, ai, hist };
  async function show() {
    const page = (location.hash || "#prep").slice(1).split("/")[0];
    const fn = PAGES[page] || prep;
    document.querySelectorAll("#nav a").forEach(a => a.classList.toggle("on", a.getAttribute("href") === "#" + (PAGES[page] ? page : "prep")));
    try { $("#main").innerHTML = await fn(); } catch (e) { $("#main").innerHTML = `<p class="bad">Something went wrong: ${esc(e.message)}</p>`; console.error(e); }
    filter();
  }
  function filter() {
    const q = $("#q").value.trim().toLowerCase();
    document.querySelectorAll("#main [data-text]").forEach(el => { el.style.display = !q || el.dataset.text.includes(q) ? "" : "none"; });
  }
  // redraw without losing your place: scroll position, search text and which sections are open
  const keep = fn => { const y = scrollY; return show().then(() => { if ($("#q").value) filter(); scrollTo(0, y); }); };
  document.addEventListener("click", ev => {
    const t = ev.target;
    const tp = t.closest("[data-tip]");
    if (tp) { tipFor === tp ? hideTip() : showTip(tp); ev.stopPropagation(); return; }
    if (tipFor && !t.closest("#tip")) hideTip();
    const sm = t.closest("details.grp > summary");
    if (sm) { const d = sm.parentElement; setTimeout(() => { S.grp[d.dataset.g] = d.open; store.set("grp", S.grp); }, 0); }
    if (t.dataset.mode) { if (t.dataset.mode !== S.mode) { store.set("mode", t.dataset.mode); location.reload(); } return; }
    if (t.dataset.ttab != null) { S.ttab = +t.dataset.ttab; store.set("ttab", S.ttab); show(); return; }
    if (t.id === "tonly") { S.tonly = !S.tonly; store.set("tonly", S.tonly); keep(); return; }
    const st = t.closest(".star");
    if (st) { const f = st.dataset.f; STARS.has(f) ? STARS.delete(f) : STARS.add(f); store.set("stars", [...STARS]); keep(); return; }
    const b = t.closest(".bosspick button");
    if (b) { S.sel[S.tab] = b.dataset.k; store.set("sel", S.sel); keep(); return; }
    const tb = t.closest(".tabs button");
    if (tb) { S.tab = tb.dataset.tab; store.set("tab", S.tab); show(); return; }
    if (t.dataset.starter) { S.starter = t.dataset.starter; store.set("starter", S.starter); keep(); return; }
    if (t.dataset.gender) { S.gender = t.dataset.gender; store.set("gender", S.gender); keep(); return; }
    if (t.dataset.team) { S.team[t.dataset.key] = +t.dataset.team; store.set("team", S.team); keep(); return; }
    if (t.dataset.leader) { S.team[t.dataset.key] = t.dataset.leader; store.set("team", S.team); keep(); return; }
    if (t.dataset.show) { S.show = t.dataset.show; store.set("show", S.show); keep(); return; }
    const pk = t.closest("[data-pick]");
    if (pk) { const a = pk.dataset.a, sp = pk.dataset.pick, r = NUZ.areas[a];
      if (r && r.st === "caught" && r.s === sp) { delete NUZ.areas[a]; delete NUZ.dead[a]; } else { NUZ.areas[a] = { s: sp, st: "caught" }; }
      saveNuz(); keep(); return; }
    if (t.dataset.ast) { const a = t.dataset.a, v = t.dataset.ast, r = NUZ.areas[a];
      if (r && r.st === v) delete NUZ.areas[a]; else NUZ.areas[a] = { st: v };
      delete NUZ.dead[a]; saveNuz(); keep(); return; }
    if (t.dataset.grpall) { const o = t.dataset.grpall === "1"; document.querySelectorAll("details.grp").forEach(d => { S.grp[d.dataset.g] = o; }); store.set("grp", S.grp); keep(); return; }
    if (t.dataset.dead) { const a = t.dataset.dead; NUZ.dead[a] ? delete NUZ.dead[a] : (NUZ.dead[a] = Date.now()); saveNuz(); keep(); return; }
    if (t.dataset.xdead) { const x = NUZ.extra[+t.dataset.xdead]; x.dead = !x.dead; saveNuz(); keep(); return; }
    if (t.id === "histcur") { PEND = SAVE; keep(); return; }
    if (t.id === "hcancel") { PEND = null; keep(); return; }
    if (t.id === "hsave") { saveRun(); keep(); return; }
    if (t.dataset.delrun) { if (confirm("Delete this run from your history?")) { RUNS = RUNS.filter(r => r.id !== t.dataset.delrun); store.set("runs", RUNS); keep(); } return; }
    if (t.id === "forget") { SAVE = null; store.set("save", null); keep(); return; }
    if (t.id === "bdown") { const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([JSON.stringify(Sync.blob())], { type: "application/json" })); a.download = G.id + "-nuzlocke-backup.json"; a.click(); return; }
    if (t.id === "reset") { if (confirm("Clear this run's areas, deaths and extras? Your stars and save stay.")) { NUZ = { on: true, shiny: NUZ.shiny, areas: {}, dead: {}, extra: [] }; saveNuz(); keep(); } return; }
    if (t.id === "gsave") { const g = gist.get(); g.token = $("#gtoken").value.trim(); gist.set(g);
      Sync.pull(false).then(() => Sync.push()).catch(e => { Sync.status = "Sync failed: " + e.message; }).then(() => keep()); return; }
    if (t.id === "gpull") { Sync.pull(true).catch(e => { Sync.status = "Pull failed: " + e.message; }).then(() => keep()); return; }
    if (t.id === "gpush") { Sync.push().catch(e => { Sync.status = "Push failed: " + e.message; }).then(() => keep()); return; }
    if (t.id === "gforget") { gist.set({}); Sync.status = "Not syncing on this device."; keep(); return; }
    const tr = t.closest("tr.pr");
    if (tr && !t.closest("button")) prepDetail(tr);
  });
  document.addEventListener("change", ev => {
    const t = ev.target;
    if (t.id === "savefile" && t.files[0]) { readFile(t.files[0]).then(() => keep()).catch(e => alert("Couldn't read that save: " + e.message)); return; }
    if (t.id === "histsave" && t.files[0]) { t.files[0].arrayBuffer().then(b => { PEND = readerFor().readSave(b, IDS, META); keep(); }).catch(e => alert("Couldn't read that save: " + e.message)); return; }
    if (t.id === "pcboxes") { S.boxes = t.checked; store.set("pcboxes", S.boxes); keep(); return; }
    if (t.id === "nzon") { NUZ.on = t.checked; saveNuz(); keep(); return; }
    if (t.id === "nzshiny") { NUZ.shiny = t.checked; saveNuz(); return; }
    if (t.dataset.area) { const a = t.dataset.area, v = t.value;
      if (!v) delete NUZ.areas[a]; else if (v[0] === "!") NUZ.areas[a] = { st: v.slice(1) }; else NUZ.areas[a] = { s: v, st: "caught" };
      if (!NUZ.areas[a] || NUZ.areas[a].st !== "caught") delete NUZ.dead[a];
      saveNuz(); keep(); return; }
    if (t.id === "bup" && t.files[0]) { t.files[0].text().then(x => { Sync.apply(JSON.parse(x)); keep(); }).catch(e => alert("Couldn't read that backup: " + e.message)); }
  });
  // header: nav for this game, and the Normal / Challenge switch
  if (!G.nav.some(([h]) => h === "#hist")) { const i = G.nav.findIndex(([h]) => h === "#data"); G.nav.splice(i < 0 ? G.nav.length : i, 0, ["#hist", "Run history"]); }
  $("#nav").innerHTML = G.nav.map(([h, t]) => `<a href="${h}"${/^https?:|calc\/|index\.html\?data=/.test(h) ? ' target="_blank" rel="noopener"' : ""}>${t}</a>`).join("");
  if (G.modes) {
    const mb = document.createElement("div"); mb.className = "modes"; mb.id = "modes";
    mb.innerHTML = `<span class="muted">Difficulty:</span>` + G.modes.map(m => `<button data-mode="${m}" class="${S.mode === m ? "on" : ""}">${m[0].toUpperCase() + m.slice(1)}</button>`).join("");
    $(".tools").prepend(mb);
  }
  $("#q").addEventListener("input", filter);
  addEventListener("hashchange", () => { $("#q").value = ""; hideTip(); show(); });
  Promise.all([load("meta.json"), load("ids.json"), load("text.json").catch(() => TXT)]).then(async ([m, i, tx]) => {
    META = m; IDS = i; TXT = tx;
    if (META.modes) { if (!META.modes[S.mode]) S.mode = Object.keys(META.modes)[0]; Object.assign(META, META.modes[S.mode]); }
    M = Model(META);
    await show();
    if (gist.get().token) Sync.pull(false).then(ch => { if (ch) show(); }).catch(e => { Sync.status = "Sync failed: " + e.message; });
  }).catch(e => { $("#main").innerHTML = `<p class="bad">Couldn't load the data: ${esc(e.message)}</p>`; });
})();
