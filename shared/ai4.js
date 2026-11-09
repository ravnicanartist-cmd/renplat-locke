/* Enemy AI notes for the Generation 4 games (Renegade Platinum, Sacred Gold): a short summary of the
   "Generation 4 Pokemon Trainer AI" reference (written from the trainer AI scripts in pret/pokeplatinum).
   window.AI4(note) returns the page; `note` is the game-specific paragraph about how many trainers use which flags. */
window.AI4 = note => `<div class="ainote">
  <p class="intro">A short summary of the "Generation 4 Pokémon Trainer AI" reference (built from the decompiled AI scripts), with what it means for this hack. The flags each trainer uses come from the ROM; the Trainers page tags them <i>Smart AI</i> (flags 1 + 2), <i>Partly smart AI</i> or <i>Basic AI</i>.</p>
  <h3 class="sec">This hack</h3>${note}
  <h3 class="sec">How a move is picked</h3>
  <ul><li>Every move starts at 100; each of the trainer's flags adds or subtracts points, and the highest score is used. Ties are picked at random.</li>
    <li>Points from different flags add up (−10 from flag 0 and −10 from flag 2 is −20), but within one flag they don't stack.</li>
    <li>Some moves are never "seen" as damage when it scores: Explosion / Self-Destruct, Dream Eater, charge moves (Solar Beam, Sky Attack, Skull Bash, Razor Wind), recharge moves (Hyper Beam, Giga Impact, the starter ultimates), Eruption / Water Spout, Gyro Ball, Low Kick / Grass Knot, Head Smash, Night Shade / Seismic Toss, Return / Frustration, Dragon Rage / Sonic Boom, Spit Up, Focus Punch, Superpower, Sucker Punch, Hidden Power, Natural Gift, Judgment and Psywave. They're only scored by their own rules.</li></ul>
  <h3 class="sec">Flag 0, Basic (almost every trainer)</h3>
  <ul><li>Avoids wasted turns: −10 for a move your type is immune to, or your ability blocks (Volt Absorb, Motor Drive, Water Absorb, Flash Fire, Wonder Guard, Levitate, Soundproof). <b>Dry Skin isn't checked</b> (a bug), so it will fire Water moves into it.</li>
    <li>Won't use a status move that can't land: sleep on a statused / Insomnia / Vital Spirit target, poison on Steel / Poison types or Immunity / Magic Guard / Poison Heal, Thunder Wave on Ground types or Limber, burns on Fire types or Water Veil, confusion on Own Tempo, Attract on the same gender.</li>
    <li>Also skips moves that do nothing right now: boosting a stat already at +6, Haze when nothing is boosted, a second Reflect / Light Screen / Substitute, hazards when you're on your last Pokémon or the hazard is maxed, Fake Out after the first turn, Dream Eater on an awake target, OHKO moves on a higher-level or Sturdy target, Belly Drum under 51% HP.</li>
    <li>A basic-only trainer otherwise picks at random among the moves that do something, so expect odd choices.</li></ul>
  <h3 class="sec">Flag 1, Evaluate Attack (the "smart" part)</h3>
  <ul><li>A move whose <b>highest damage roll</b> KOs you gets +4, or +6 if it's a +1 priority move (Quick Attack, Mach Punch, Aqua Jet, Bullet Punch, Ice Shard, Shadow Sneak, Vacuum Wave...). Note it uses the max roll, not the minimum like Gen 5.</li>
    <li>Every move that isn't its strongest against you gets −1, so it mostly spams its best hit.</li>
    <li>Explosion, Focus Punch and Sucker Punch usually get −2; a 4× effective move has a 31% chance of +2.</li></ul>
  <h3 class="sec">Flag 2, Expert (what it does with status moves)</h3>
  <ul><li>Paralysis moves: +3 (92%) if it's slower than you. Speed boosts: +3 (73%) if slower, −3 if already faster.</li>
    <li>Setup (Swords Dance, Nasty Plot, Calm Mind...): likely at full HP, unlikely below 70%, and discouraged past +3.</li>
    <li>Recovery: never at full HP; −8 if it's faster than you; mostly used below 70% when it's slower.</li>
    <li>Protect: discouraged after one use or when it's the one poisoned / seeded / cursed; +2 when <i>you</i> are (Toxic, Leech Seed, Curse, Perish Song, Yawn) and in doubles.</li>
    <li>Explosion / Memento / Healing Wish: discouraged at high HP, encouraged at 30% or less.</li>
    <li>Fake Out +2. U-turn gets +2 if it's the last Pokémon. Sucker Punch +1 (75%). High-crit moves +1 when super effective (50%).</li>
    <li>Trick / Switcheroo with a Choice item or Toxic / Flame Orb: +5 unless you already hold something bad.</li>
    <li>Rain / Sun / Hail / Sand: +1 if another weather is up; Swift Swim users that are slower than you set rain first.</li>
    <li>Bugs worth knowing: Facade is boosted when <i>you</i> are statused, Foresight checks its own type, Water Spout checks your HP.</li></ul>
  <h3 class="sec">The other flags</h3>
  <ul><li><b>Setup First Turn</b>: on turn 1, +2 (69%) to boosting, lowering, status, screens, Substitute and the like.</li>
    <li><b>Risky</b>: +2 (50%) to sleep, Explosion, OHKO, high-crit, confusion, Counter / Mirror Coat, Destiny Bond, Swagger, Belly Drum, Focus Punch...</li>
    <li><b>Prioritize Extremes</b>: +2 (61%) to status moves and every move the damage check ignores (see the list above).</li>
    <li><b>Baton Pass</b>: sets up on turn 1 above 60% HP and passes boosts.</li>
    <li><b>Tag Strategy</b> (doubles): never hits its partner unless it helps (Will-O-Wisp into Flash Fire, Electric moves into Volt Absorb / Motor Drive, Surf into Water Absorb); Earthquake / Surf / Discharge depend on whether the partner is immune.</li>
    <li><b>Check HP</b>: no setup or screens below 70% HP; no recovery, Rest, Destiny Bond or Reversal above 70%; no Explosion above 30%.</li>
    <li><b>Weather</b>: +5 to its weather move on turn 1 only. <b>Harassment</b>: +2 (50%) to status conditions, stat drops, Leech Seed, Encore, Spikes, Toxic Spikes, Torment and Knock Off.</li></ul>
  </div>`;
