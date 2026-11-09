// Nuzlocke hub Boss Prep / Trainers: index.html?...&opp=<set id> opens the calc with that trainer Pokemon on the right.
// Boss Prep adds &me=<species>&lv=<level>&mv=<move>,<move>... to put your Pokemon on the left (blank set, IVs 15, Hardy).
(function () {
    var opp = new URLSearchParams(location.search).get('opp');
    if (!opp) return;
    try { localStorage["right"] = opp; } catch (e) {}
    var tries = 0;
    var t = setInterval(function () {
        tries++;
        if (tries > 150) { clearInterval(t); return; }
        if (typeof setdex === 'undefined' || !setdex || typeof setOpposing !== 'function') return;
        var sp = opp.split(' (')[0];
        if (!setdex[sp]) return;
        clearInterval(t);
        setTimeout(function () { setOpposing(opp); setLevel(); setMine(); }, 400);
    }, 100);
    // &olv= sets the trainer Pokemon's level (Blaze Black 2 Redux Challenge Mode levels differ from the calc's Normal Mode sets)
    function setLevel() {
        var olv = new URLSearchParams(location.search).get('olv');
        if (!olv) return;
        setTimeout(function () { var p2 = $('#p2'); if (p2.find('.level').val() != olv) p2.find('.level').val(olv).change(); }, 300);
    }
    function setMine() {
        var q = new URLSearchParams(location.search), me = q.get('me');
        if (!me || !setdex[me]) return;
        setTimeout(function () {
            var id = me + ' (Blank Set)', p1 = $('#p1');
            p1.find('.set-selector').val(id).change();
            p1.find('.select2-chosen').first().text(id);
            if (q.get('lv')) p1.find('.level').val(q.get('lv'));
            p1.find('.ivs').val(15);
            (q.get('mv') || '').split(',').slice(0, 4).forEach(function (m, i) {
                if (m) p1.find('.move' + (i + 1) + ' select.move-selector').val(m).change();
            });
            p1.find('.level').change();
        }, 500);
    }
})();
