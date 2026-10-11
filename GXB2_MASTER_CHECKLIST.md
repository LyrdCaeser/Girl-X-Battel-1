> **Integración local — 2026-09-28, ChatGPT.** Copia del checklist aportado, colocada junto a [LEEME.md](LEEME.md). El adjunto recuperado y las copias de Downloads son idénticos (SHA256 original: `fd04ca6ee675e7acc5a1a8f15daa39e984660416c76fa0d2546e627a94b62e5e`). La ruta solicitada `/mnt/data/GXB2_MASTER_CHECKLIST.md` no existe en este Mac; no se modificaron las fuentes.
>
> **Cómo usarlo:** este documento define alcance/protocolo; [LEEME](LEEME.md) explica inicio y fuentes; [ESTADO_PROYECTO](ESTADO_PROYECTO.md) documenta qué está implementado/parcial/no verificado con evidencia; [VALIDACION](VALIDACION.md) registra pruebas; [DESIGN_DECISIONS](DESIGN_DECISIONS.md) separa adaptaciones locales del original. Leer después [AI_WORKBOARD](AI_WORKBOARD.md) para reclamar tarea y revisar bloqueos.
>
> **Las casillas originales de las secciones 1–38 se conservan.** El estado evaluado está en la matriz por sección de ESTADO_PROYECTO; una casilla vacía heredada no afirma que se haya revisado el código y no exista implementación. Las etiquetas originales de investigación/existencia tampoco son certificaciones nuevas. No se declara completo ningún sistema global con `[X]` en esta auditoría.
>
> **Estado vigente (30/09/2026):** consulta la [actualización 40](#40-actualización-de-cobertura--2026-09-30) antes de los apuntes históricos. Incorpora las tandas WAVE-019–048; `[T]` se refiere al alcance implementado y probado de cada tanda, mientras que el sistema global sigue `[P]` si faltan reglas, pantallas o validación.

# GxB2 Reborn — Master Reconstruction Checklist

> Living coordination document for reconstruction/preservation of *Girls X Battle 2* as an offline-capable project.
> Last structural update: 2026-09-30

---

## 0. MULTI-AGENT PROTOCOL — READ FIRST

This file is intended to be shared by ChatGPT, Claude, Nava, and any future agent working on the project.

### Golden rules

1. **Read this file before modifying the project.**
2. Read `AI_WORKBOARD.md` if present.
3. Never assume that existing code is complete or correct.
4. Before starting a task, claim it with an owner tag.
5. Record the files/directories that will be touched before making substantial edits.
6. Do not modify files actively locked by another agent unless the user explicitly authorizes coordination on the same task.
7. Preserve original behavior first. Rebalancing/redesign belongs in a separate decision layer.
8. Do not silently remove an original feature because it depends on a server. Mark it for offline replacement.
9. When a new system, asset, currency, endpoint, screen, field, mode, event, or mechanic is discovered, add it here.
10. At the end of a task, update its implementation status and add enough notes that another agent can continue without reconstructing the reasoning from scratch.

### Status syntax

**Evidence / existence**

- `[C]` Confirmed to have existed in GxB2
- `[P?]` Probable / indirect evidence
- `[?]` Needs investigation

**Research status**

- `[ ]` Rules/data unknown
- `[R]` Partially researched
- `[D]` Sufficiently documented to reproduce

**Implementation status**

- `[ ]` Not started
- `[W:GPT]` Claimed / being worked on by ChatGPT
- `[W:CLAUDE]` Claimed / being worked on by Claude
- `[W:NAVA]` Claimed / being worked on by Nava
- `[P]` Partial implementation
- `[T]` Implemented, needs testing/verification
- `[X]` Implemented and tested
- `[M]` Implemented intentionally differently from original
- `[-]` Intentionally excluded
- `[BLOCKED]` Cannot proceed until dependency/data is recovered

### Recommended task record

```yaml
id: GXB2-COMBAT-001
name: Damage Formula
existence: confirmed
research: documented
implementation: in_progress
owner: ChatGPT

files_locked:
  - server/combat/damage.py
  - server/combat/status.py
  - data/combat.json

dependencies:
  - GXB2-GIRLS-STATS
  - GXB2-COMBAT-ATTRIBUTES

last_update: YYYY-MM-DD
notes:
  - Reconstruct original behavior first.
  - Balance changes go in DESIGN_DECISIONS.md.
```

### Completion rule

A feature is **not `[X]` merely because a screen opens**. Where applicable verify:

- UI/navigation
- game logic
- persistence/save-load
- rewards/costs
- reset/time behavior
- edge cases
- relevant assets/audio
- offline behavior

---

# 1. PROJECT / INFRASTRUCTURE

- [ ] `[C][R]` Application startup
- [ ] `[C][R]` Loading sequence
- [ ] `[C][ ]` Original login/account flow documentation
- [ ] `[C][ ]` Original server selection behavior
- [ ] `[C][ ]` Original account identifiers
- [ ] `[?][ ]` Guest account behavior
- [ ] `[?][ ]` Account binding/migration behavior
- [ ] `[C][ ]` Maintenance/server notices
- [ ] `[C][ ]` Version/update checks
- [ ] `[C][ ]` Remote configuration
- [ ] `[C][ ]` Network request map
- [ ] `[C][ ]` API response map
- [ ] `[C][ ]` Error handling / retry dialogs
- [ ] `[C][ ]` Server time dependency
- [ ] `[C][ ]` Daily reset
- [ ] `[C][ ]` Weekly reset
- [ ] `[C][ ]` Monthly/seasonal reset where applicable
- [ ] `[C][ ]` RNG behavior
- [ ] `[?][ ]` RNG seeding / server-side randomness
- [ ] `[C][ ]` Player database schema
- [ ] `[C][ ]` Inventory persistence
- [ ] `[C][ ]` Girl-state persistence
- [ ] `[C][ ]` Quest/event persistence
- [ ] `[C][ ]` Mail persistence
- [ ] `[C][ ]` Settings persistence
- [ ] `[?][ ]` Analytics/telemetry calls — document, do not require for offline play

## Offline replacement

- [ ] Local account/profile
- [ ] Local database/save
- [ ] Local API replacement
- [T][M] Local clock abstraction (reloj monótono, LOCAL-057; frontera del día abierta)
- [ ] Daily reset scheduler
- [ ] Weekly reset scheduler
- [ ] Event scheduler
- [ ] Deterministic/testable RNG option
- [ ] Save backup
- [ ] Save restore
- [ ] Save migration/versioning
- [ ] Multiple local save slots (optional redesign)
- [ ] Original-player-data import pipeline ⭐
- [ ] Validate imported data without corrupting source

---

# 2. PLAYER PROFILE / ACCOUNT

- [ ] `[C][ ]` Player name
- [ ] `[C][ ]` Player ID
- [ ] `[C][ ]` Player level
- [ ] `[C][ ]` Player EXP
- [ ] `[C][ ]` Avatar
- [ ] `[C][ ]` Avatar frames
- [ ] `[?][ ]` Signature/profile message
- [ ] `[C][ ]` Personal information/profile screen
- [ ] `[C][ ]` Personalize/customization
- [T][M] `[C][R]` VIP level — tabla `vip` original (17 niveles); EXP local por logros (LOCAL-050, `gxb2/vip.py`)
- [P][M] `[C][R]` VIP rewards/privileges — aplicados: bono idle, Midas, Internship, Excursión, High Stakes/Slots; sin aplicar aún: `partners_limit`, `quiz_buy_times`, `battle_speed`, `login_double`, regalos VIP
- [ ] `[C][ ]` Achievements
- [ ] `[C][ ]` Feature unlocks by player level
- [ ] `[?][ ]` Account statistics
- [ ] `[?][ ]` Login history / creation date fields

## Offline redesign

- [T][M] VIP benefits obtainable through normal play (panel en Mi perfil)
- [ ] No paid-only progression requirement
- [ ] Preserve VIP UI/history where useful for save compatibility

---

# 3. BATTLE GIRLS — MASTER DATABASE

## Houses / factions

- [ ] `[C][D]` Ghost
- [ ] `[C][D]` Human
- [ ] `[C][D]` Monster
- [ ] `[C][D]` Fairy
- [ ] `[C][D]` Demon
- [ ] `[C][D]` Angel
- [ ] `[C][R]` Cosmos
- [ ] `[?][ ]` Historical faction naming/version changes

## Per-girl data

- [ ] ID/internal name
- [ ] Display name/localizations
- [ ] House/faction
- [ ] Class
- [ ] Base rarity
- [ ] Maximum original rarity
- [ ] Level
- [ ] Level cap
- [ ] EXP curve
- [ ] Base stats
- [ ] Stat growth
- [ ] Skill data
- [ ] Passive data
- [ ] Skill unlock thresholds
- [ ] Elite/advanced skills where applicable
- [ ] Biography
- [ ] Character art
- [ ] Battle assets
- [ ] Voice data
- [ ] Skin references
- [ ] Shard references
- [ ] Acquisition methods
- [ ] Historical balance/version notes

## Girl progression

- [ ] `[C][ ]` Level up
- [ ] `[C][ ]` Star-up / promotion
- [x] `[C][M]` Graduate / graduation — recetas originales + LOCAL-072: ruta 1–3★ hasta10★, selección y revisión de materiales, UI corregida, filtros on/off y orden sin duplicados (057); 318 pruebas OK. Balance ampliado pendiente de ajustar jugando.
- [ ] `[C][ ]` Limit Break / advanced progression
- [ ] `[C][ ]` Reverse / regression
- [ ] `[C][ ]` Replace
- [ ] `[C][ ]` Lock/unlock
- [ ] `[C][ ]` Girl shards
- [ ] `[C][ ]` Food/material girls
- [ ] `[?][ ]` Late-game girl-specific progression systems

## Reborn balance goals — DO NOT MIX WITH ORIGINAL DATA

- [ ] Allow low-star girls to remain viable at endgame
- [ ] Investigate extending 1★–4★ girls to high progression tiers
- [ ] Reduce single dominant endgame meta
- [ ] Rock-paper-scissors/counterplay study
- [ ] Preserve character identity while buffing obsolete units
- [ ] Maintain an optional original-balance ruleset

---

# 4. EQUIPMENT / CHARACTER BUILD

## Gear

- [ ] `[C][ ]` Gear slots
- [ ] `[C][ ]` Gear rarity
- [ ] `[C][ ]` Gear stats
- [ ] `[C][ ]` Gear sets
- [ ] `[C][ ]` Gear equip/unequip
- [ ] `[C][ ]` Gear upgrade/forge
- [ ] `[C][ ]` Auto-forge
- [ ] `[?][ ]` Gear selling/dismantling

## Crystal

- [ ] `[C][ ]` Crystal system
- [ ] `[C][ ]` Crystal tiers
- [ ] `[C][ ]` Crystal upgrade
- [ ] `[C][ ]` Attribute reroll
- [ ] `[?][ ]` Attribute locking
- [ ] `[C][ ]` Upgrade/reroll costs

## Antique

- [ ] `[C][ ]` Antique database
- [ ] `[C][ ]` Antique rarity/tier
- [ ] `[C][ ]` Antique attributes
- [ ] `[C][ ]` Antique upgrade
- [ ] `[C][ ]` Exclusive/special antiques
- [ ] `[C][ ]` Acquisition sources
- [ ] `[?][ ]` Antique comparison/balance data
- [ ] Offline: formerly paid-only antiques obtainable normally

---

# 5. SKINS / FASHION / OUTFITS

- [ ] `[C][D]` Skin database (community wiki documents hundreds; reconcile with client data)
- [ ] `[C][ ]` Skin ownership
- [ ] `[C][ ]` Skin equip
- [ ] `[C][ ]` Skin stat bonuses
- [ ] `[C][ ]` Skin rarity/category
- [ ] `[C][ ]` Skin Store
- [ ] `[C][ ]` Fashion Points
- [ ] `[C][ ]` Fashion Level
- [ ] `[C][ ]` Theme collections
- [ ] `[C][ ]` Animated skins where applicable
- [ ] `[C][ ]` Oath skins
- [ ] `[C][ ]` Dating/special skins
- [ ] `[C][ ]` Outfit sets
- [ ] `[C][ ]` Outfit skills
- [ ] `[?][ ]` Fantasy Book / related collection mechanics
- [ ] `[?][ ]` Skin-specific voices/animations

---

# 6. RELATIONSHIPS / CHARACTER INTERACTION

- [ ] `[C][D][T]` Intimacy — cap 10000/12000 tras Oath, 5 corazones cada 2000 (relations.py)
- [ ] `[C][D][T]` Gifts — 40 regalos, ×10, Compose 44#10 (LOCAL-026a)
- [ ] `[C][D][T]` Gift preferences — gift_type1/2 → 40/20/0 y voz de reacción 25/23/24
- [ ] `[C][R][P]` Intimacy thresholds/rewards — bonus de appointment mostrado; no aplicado aún a HeroAttr
- [ ] `[C][R][P]` Dating — DatesList/Dates window; sin minijuego de cita
- [ ] `[C][ ]` Dating scenes
- [ ] `[C][D][T]` Oath
- [ ] `[C][D][T]` Oath requirements/cost — 10000 intimidad + 45#1
- [ ] `[C][ ]` Oath scenes
- [ ] `[C][ ]` Oath rewards
- [ ] `[C][ ]` Oath frames/visual indicators
- [ ] `[C][D][T]` Character voice lines — partner_dialog + sound1/2, conversión mp3 bajo demanda
- [ ] `[C][ ]` Character profile/files
- [ ] `[C][ ]` Personal stories
- [ ] `[?][ ]` Touch/home-screen reactions

---

# 7. COMBAT ENGINE

## Formation

- [ ] `[C][ ]` Team composition
- [ ] `[C][ ]` Front/back positions
- [ ] `[C][ ]` Formation restrictions
- [ ] `[C][ ]` Lineup presets
- [ ] `[C][ ]` House/faction aura/bonus if applicable
- [ ] `[C][ ]` Faction advantage relationships

## Turn engine

- [ ] `[C][ ]` Round order
- [ ] `[C][ ]` Speed calculation
- [ ] `[C][ ]` Normal attack
- [ ] `[C][ ]` Active skill trigger
- [ ] `[C][ ]` Energy gain
- [ ] `[C][ ]` Energy spending
- [ ] `[C][ ]` Passive triggers
- [ ] `[C][ ]` Target selection
- [ ] `[C][ ]` Death
- [ ] `[C][ ]` Revive
- [ ] `[C][ ]` Battle end conditions
- [ ] `[C][ ]` Maximum rounds/timeouts

## Stats / formula

- [ ] `[C][R]` Damage formula
- [ ] `[C][ ]` Attack
- [ ] `[C][ ]` HP
- [ ] `[C][ ]` Armor
- [ ] `[C][ ]` Armor Break
- [ ] `[C][ ]` Crit
- [ ] `[C][ ]` Crit Damage
- [ ] `[C][ ]` Precision
- [ ] `[C][ ]` Block
- [ ] `[C][ ]` Speed
- [ ] `[C][ ]` Skill Damage
- [ ] `[C][ ]` Holy Damage / special damage
- [ ] `[C][ ]` Damage Reduction
- [ ] `[C][ ]` Control Immunity
- [ ] `[?][ ]` Other late-game attributes

## Effects

- [ ] Buff engine
- [ ] Debuff engine
- [ ] Damage-over-time
- [ ] Healing
- [ ] Shields
- [ ] Crowd control
- [ ] CC immunity
- [ ] Stat modifiers
- [ ] Triggered effects
- [ ] On-hit effects
- [ ] On-death effects
- [ ] Round-start/end effects
- [ ] Dispel/cleanse

## Battle presentation

- [ ] Battle sprites/models
- [ ] Attack animation
- [ ] Skill animation
- [ ] FX
- [ ] Damage/heal numbers
- [ ] Status icons
- [ ] Battle speed controls
- [ ] Skip
- [ ] Raid/instant result where applicable
- [ ] Victory screen
- [ ] Defeat screen
- [ ] Reward screen

---

# 8. CAMPAIGN / MAIN STORY

- [x] `[C][D][T][P]` Yume Academy main story — gxb2/story.py + web/story.js: escenas de campaña antes y después del combate y Memories (LOCAL-039)
- [ ] `[C][R]` Chapter list and ordering
- [ ] `[C][R]` Episode list
- [ ] `[C][ ]` Stage map/progression
- [ ] `[C][ ]` Stage requirements
- [ ] `[C][ ]` Normal stages
- [ ] `[C][ ]` Boss stages
- [ ] `[C][ ]` Stage rewards
- [ ] `[C][ ]` First-clear rewards
- [ ] `[C][ ]` Story triggers
- [ ] `[C][ ]` Dialog/script data
- [ ] `[C][ ]` Backgrounds
- [ ] `[C][ ]` CGs
- [ ] `[C][ ]` Story replay via Memories
- [ ] `[?][ ]` Later chapters beyond currently documented wiki coverage

---

# 9. IDLE / AUTO BATTLE

- [ ] `[C][D]` Auto/idle battle system
- [ ] `[C][ ]` Idle timer
- [ ] `[C][ ]` Maximum accumulated time
- [ ] `[C][ ]` Player EXP generation
- [ ] `[C][ ]` Coin generation
- [ ] `[C][ ]` EXP Juice generation
- [ ] `[C][ ]` Gear drops
- [ ] `[C][ ]` Girl shard drops
- [ ] `[C][ ]` Other item drops
- [ ] `[C][ ]` Campaign-stage-dependent loot table
- [ ] `[?][ ]` Scavenger/special idle drops
- [ ] `[C][ ]` Claim UI
- [ ] `[C][ ]` Offline elapsed-time calculation

## Reborn redesign

- [ ] Improve endgame usefulness
- [ ] Keep progression meaningful without forcing purchases
- [ ] Tune event-material income so events can reasonably be completed F2P
- [ ] Preserve optional original reward tables

---

# 10. PVE MODES

## Tests

- [ ] `[C][D]` Tests mode exists
- [ ] Stage structure
- [ ] Enemy data
- [ ] Rewards
- [ ] Reset behavior
- [ ] Progression

## Patrol

- [ ] `[C][D][T][M]` Patrol — gxb2/patrol.py + web/patrol.js; modelo `Dungeon`, combate original tipo DUNGEON (LOCAL-028)
- [ ] `[C][D][T]` Easy
- [ ] `[C][D][T]` Normal
- [ ] `[C][D][T]` Hard
- [ ] `[C][D][T]` Expert — en el cliente se llama **Extreme**
- [ ] `[C][D][T]` Nightmare / later difficulty — 6 fases × 100 (Easy, Normal, Hard, Extreme, **Fantasy**, Nightmare), `dungeon_top` 600
- [ ] `[C][D][T]` Persistent HP between fights — ambos bandos (status hp/mp del ReportHero original)
- [ ] `[C][D][T]` Enemy generation — batalla aleatoria de la reserva `dungeon_battle.random_battle` de cada fase
- [ ] `[C][D][T]` Healing items — Rice Balls 1-3 (`healP`, `energy`)
- [ ] `[C][D][T]` Rice balls / relevant consumables
- [ ] `[C][D][T]` Stationery/buff items — Pencil/Eraser/Protractor, máx. 20, buff permanente por combate
- [ ] `[C][D][T][M]` Merchants — oferta tras victoria; Skip la guarda en la tienda; nivel de tienda por fase (M)
- [ ] `[C][D][T][M]` Rewards — 1 de 3 (cofre/objeto/mercader) con `award_weight` (orden de columnas M)
- [ ] `[C][D][T][M]` Reset schedule — 48 h abierta / 48 h cerrada, calendario local (M); Auto Smash

## Other PVE

- [ ] `[C][D][T][M]` House Exam — gxb2/house_exam.py + web/house-exam.js; modelo `AcademyAssessment`, 6 casas × 100 fases, solo la facción de la casa, temporadas de 14 días con 3 variantes de enemigos, Admission Ticket (64) / Certificate (63), Raid, Exam Score → item 173 (LOCAL-029)
- [ ] `[C][R]` Old Campus
- [ ] `[C][D][T][M]` Old Campus Exploration — gxb2/old_campus.py + web/old-campus.js (entrada desde Tests), LOCAL-035
- [ ] `[C][D][T][M]` Sanctuary — gxb2/sanctuary.py + web/sanctuary.js: mapa original del santuario, 9 fases, HP persistente, bendiciones, tienda, jefe con tramos de daño; rivales espejo (LOCAL-032)
- [ ] `[C][R]` Practical Work
- [ ] `[C][R]` Practical Experience
- [ ] `[C][R]` Entrance Exam
- [ ] `[C][R]` Admission Prep
- [x] `[C][D][T][P][M]` Echoes of Time — gxb2/echoes.py + web/echoes.js (Liga): observación, cartas, Planetarium, fases y logros (LOCAL-036)
- [ ] `[C][R]` Squad
- [ ] `[?][ ]` Top Floor / tower naming/version relationship
- [ ] `[?][ ]` Campus Guardian
- [ ] `[?][ ]` Challenge modes
- [ ] `[?][ ]` Other late-game PVE discovered in client/version logs

For every mode recover: unlock conditions, attempts, enemy generation, battle rules, rewards, reset schedule, UI, and progression state.

---

# 11. GALAXY / LATE-GAME SYSTEMS

- [ ] `[C][R]` Galaxy Voyage
  - [ ] Unlock conditions
  - [ ] Map/node generation
  - [ ] Combat
  - [ ] Resources
  - [ ] Progression
  - [ ] Rewards
  - [ ] Reset behavior
- [ ] `[C][R]` Stellar Altar
  - [ ] Unlock
  - [ ] Upgrade tree
  - [ ] Currencies
  - [ ] Stat effects
  - [ ] Persistence
- [ ] `[C][R]` Astral Core
  - [ ] Core types
  - [ ] Acquisition
  - [ ] Upgrade
  - [ ] Effects
  - [ ] Equip/use rules
- [ ] `[C][R]` Cosmos-specific progression
- [ ] `[?][ ]` Other connected cosmic/endgame systems

---

# 12. SERVANTS

- [ ] `[C][R]` Servant collection
- [ ] Servant database
- [ ] Unlock/acquisition
- [ ] Level
- [ ] Stats
- [ ] Skills
- [ ] Battle integration
- [ ] `[C][R]` Aura
- [ ] `[C][R]` Ulticore
- [ ] Evolution/promotion
- [ ] Upgrade resources
- [ ] UI
- [ ] Reset/rebuild behavior if any

---

# 13. PVP / LEAGUES

- [ ] `[C][D][M]` Junior Varsity — gxb2/arena.py + web/arena.js; robots originales, combate real, rivales NPC (LOCAL-027)
- [ ] `[C][D]` Varsity
  - [ ] Three-team behavior
- [ ] `[C][D]` Elite League
- [ ] `[C][R]` Ultimate League
- [ ] `[C][R]` House Battle
- [ ] Tickets/attempts
- [ ] Matchmaking
- [ ] Opponent refresh
- [ ] Points
- [ ] Ranking
- [ ] Seasons
- [ ] Defense lineup
- [ ] Battle history
- [ ] Replay if applicable
- [ ] Daily rewards
- [ ] Seasonal rewards
- [ ] Shop/currency links

## Offline replacement

- [ ] NPC player generator
- [ ] Persistent simulated roster pool
- [ ] Difficulty scaling
- [ ] Ranking simulation
- [ ] Season simulation
- [ ] Preserve PvP rewards without network dependency

---

# 14. GUILD

- [ ] `[C][D]` Guild creation/join
- [P][M] Guild name/info (Gremio v1, LOCAL-060)
- [ ] Member roles
- [ ] Office
- [P][M] Daily sign-in (Office, LOCAL-060)
- [P][M] Guild EXP
- [P][M] Guild level
- [ ] Guild Coins
- [ ] Merchant / Guild Store
- [ ] Lab
- [ ] Class technologies
- [ ] Technology upgrade costs
- [P][M] Gym (Guild Boss 1-60; final boss pendiente)
- [ ] Guild Boss
- [P][M] Cafeteria (Molino y pedidos)
- [ ] Orders/tasks
- [ ] Playground
- [ ] Guild War
- [ ] Guild ranking
- [ ] Guild rewards
- [ ] Guild chat

## Offline replacement

- [P][M] NPC guild members (miembros que se unen y firman)
- [ ] Simulated contributions
- [ ] Simulated guild progression
- [ ] Simulated guild war/opponents
- [ ] No online-member requirement

---

# 15. SUMMONING / GIRL ACQUISITION

## Capsule / recruit

- [ ] `[C][ ]` Capsule system
- [ ] Normal/basic capsule
- [ ] Advanced capsule
- [ ] Summon costs
- [ ] Drop pools
- [ ] Rates
- [ ] Pity/guarantee behavior
- [ ] Multi-summon
- [ ] Summon animation
- [ ] Duplicate handling
- [ ] Event banners
- [ ] Historical banner data if recoverable

## Enroll / Exchange

- [ ] `[C][D]` Enroll
- [ ] Seals
- [ ] House/faction selection
- [ ] Drop pools
- [ ] Rewards
- [ ] `[C][D]` Exchange
- [ ] Portfolios
- [ ] Exchange rules
- [ ] Preserve level after replacement where original did
- [ ] Preserve gear where original did
- [ ] Preserve crystal where original did
- [ ] Preserve antique where original did

## Other acquisition

- [ ] `[C][R]` Elite Assembly
- [ ] `[?][ ]` Cafe acquisition functionality
- [ ] Girl Store
- [ ] Shard synthesis
- [ ] Event acquisition
- [ ] Campaign/idle acquisition

---

# 16. SLOT MACHINE / LUCKY SYSTEM

- [ ] `[C][R]` Slot Machine
- [ ] Normal mode
- [ ] High Stakes
- [ ] Slot Tickets
- [ ] Single spin
- [ ] Multi-spin behavior
- [ ] Prize pool
- [ ] Player-level scaling if applicable
- [ ] Refresh
- [ ] Coupons
- [ ] Lucky Store
- [ ] Lucky Store inventory
- [ ] Lucky Store refresh
- [ ] Event integration

---

# 17. ECONOMY / ITEMS

Create authoritative item/currency registry.

- [ ] Coins
- [ ] Gems
- [ ] EXP Juice
- [ ] Lunch Boxes / relevant stamina-like materials
- [ ] Girl shards
- [ ] Gear materials
- [ ] Crystal materials
- [ ] Antique materials
- [ ] Capsule/recruit tickets
- [ ] League tickets
- [ ] Slot tickets
- [ ] Coupons
- [ ] Seals
- [ ] Portfolios
- [ ] Guild Coins
- [ ] Event currencies
- [ ] `[C][R]` Elementium / late-game currencies
- [ ] `[C][R]` Lucky Crystal / related currencies
- [ ] Cosmos/Galaxy currencies
- [ ] Servant currencies
- [ ] Skin/Fashion currencies
- [ ] Collection currencies
- [ ] Unknown client item IDs

For every currency/item record: ID, name, icon, cap, sources, sinks, shop value, event association, original paid/free status.

---

# 18. STORES / MARKET

- [ ] `[C][D][T]` Market — shop_black_new, 1 compra por hueco, reinicio diario (LOCAL-026)
- [ ] `[C][D][T]` Girl Store — shop_hero_new, grupos/rank
- [ ] `[C][D][M]` Guild Store/Merchant — límites por hueco, refresh 4#20000, reinicio diario (LOCAL-026)
- [ ] `[C][D][M]` Lucky Store — ver LOCAL-018 (acquisition.py)
- [ ] Skin Store — pendiente (skins)
- [ ] `[C][R]` Collection Store
- [ ] Event Stores
- [ ] `[C][D][T]` League/PvP stores if applicable — shop_arena (League), shop_new_trial (Sanctuary), shop_school_practise (House Exams), shop_artifact (Antique)
- [ ] Late-game stores
- [ ] Inventory generation
- [ ] `[T]` Refresh timer — Market medianoche local
- [ ] `[T]` Manual refresh — refresh_cost donde is_refresh=1
- [ ] Refresh cost scaling
- [ ] `[T]` Purchase limits — slot_buy_time
- [ ] `[M]` Daily/weekly limits
- [ ] `[T]` Unlock conditions — limit_level

---

# 19. QUESTS / TASKS / ACHIEVEMENTS

- [ ] `[C][D][M]` Daily missions — daily_mission, contadores locales, medianoche local (LOCAL-025)
- [ ] Weekly missions
- [ ] Monthly missions if present
- [ ] `[C][D][T]` Achievement categories — achievement_type (métricas locales para 1,3-6,19,22,24,25,27,36,39-43)
- [ ] `[C][D][T]` Achievement rewards — cadena next_achieve_id
- [ ] `[T]` Progress counters
- [ ] Bulk claim
- [ ] `[C][D][T][M]` Internship — gxb2/internship.py + web/internship.js (Campus → Intern), LOCAL-033
- [ ] Internship rarity/tier
- [ ] Internship requirements
- [ ] Internship duration
- [ ] Internship rewards
- [ ] Refresh
- [ ] `[C][R]` Exclusive Task
- [ ] Event tasks
- [ ] Beginner/new-player missions
- [ ] Return-player missions if present

---

# 20. EVENTS — FRAMEWORK

## Core event engine

- [P][M] Event definition format (activity_kit / activity_draw JSON, LOCAL-059/061)
- [ ] Start/end dates
- [ ] Automatic rotation
- [ ] Event state persistence
- [ ] Event-specific currencies
- [ ] Event missions
- [ ] Event battles
- [ ] Event bosses
- [ ] Event shops
- [ ] Event story
- [ ] Event CG/assets
- [ ] Event minigames
- [ ] Event ranking replacement where needed
- [ ] Event reward mail
- [ ] Event cleanup/archival

## Confirmed/documented event families and named events to recover

- [ ] Capsule/recruit events
- [ ] Enroll events
- [ ] Exclusive Task
- [ ] Mysterious Chest
- [ ] Jigsaw — `[T][P][M]` jugable en tanda052; calendario/presentación completa pendientes.
- [ ] Winning Heart
- [ ] Practical Work-related events
- [ ] Yume Sports Festival
- [ ] Miss Yume Pageant
- [ ] Seaside Fishing
- [ ] Gift Exchange
- [ ] Righteous Liberation
- [ ] My Room
- [ ] Orientation Gift
- [ ] Capsule Prize
- [ ] Anniversary events
- [ ] Christmas
- [ ] New Year
- [ ] Valentine
- [ ] Summer/beach events
- [ ] Halloween if present
- [ ] Collaboration/special events if present
- [ ] Other events recovered from version history/client assets

## Reborn event philosophy

- [ ] Events can cycle forever offline
- [ ] No real-money requirement
- [ ] Reasonable F2P completion
- [ ] Old events replayable
- [ ] Preserve original reward tables as optional/reference data

---

# 21. DORM / MY ROOM / LEISURE

- [ ] Dorm/My Room entry
- [ ] Rooms
- [ ] Room unlocks
- [ ] Furniture database
- [ ] Furniture rarity
- [ ] Furniture placement
- [ ] Furniture rotation/movement
- [ ] Furniture collection
- [ ] Comfort/value score
- [ ] Comfort rewards
- [ ] Girl placement
- [ ] Girl movement/animations
- [ ] Girl interactions
- [ ] Backgrounds/themes
- [ ] Room save/load
- [ ] `[?][ ]` Visits/social dorm functionality

---

# 22. COLLECTION / ARCHIVE

- [ ] Girl collection
- [ ] Skin collection
- [ ] Furniture collection
- [ ] Antique collection
- [ ] Gear collection if exposed
- [ ] Collection completion/progress
- [ ] Acquisition hints
- [ ] Collection Store
- [ ] Reward thresholds
- [ ] Unknown collection categories

---

# 23. STORY / MEMORIES / MANGA

- [ ] `[C][D]` Memories system
- [ ] Main Story archive
- [ ] Event Story archive
- [ ] Character Story archive
- [ ] Dating/Oath replay where available
- [ ] CG gallery
- [ ] `[C][R]` Manga
- [ ] Manga pages/assets
- [ ] Unlock conditions
- [ ] Localization/text extraction
- [ ] Replay without server

---

# 24. SOCIAL

- [ ] Friends list
- [ ] Friend requests
- [ ] Add/remove friend
- [ ] Friend recommendations
- [ ] Friend rewards/points
- [ ] Friend Boss
- [ ] `[C][R]` Security Squad
- [ ] Chat
- [ ] World/global chat if present
- [ ] Guild chat
- [ ] Private chat if present
- [ ] Mail
- [ ] System mail
- [ ] Reward mail
- [ ] Announcements

## Offline replacement

- [ ] NPC friends
- [ ] Simulated friend interactions
- [ ] Local/system mail generator
- [ ] Preserve friend-boss mechanics without network
- [ ] Replace social requirements in quests/events

---

# 25. UI / UX

## Main navigation

- [ ] Home/front page
- [ ] Main menu
- [ ] Girl screens
- [ ] Bag
- [ ] Campaign
- [ ] Battle modes
- [ ] Guild
- [ ] Friends
- [ ] Events
- [ ] Shops
- [ ] Profile
- [ ] Settings

## Micro-interactions — IMPORTANT FOR FIDELITY

- [ ] Pop-up open animation
- [ ] Pop-up close animation
- [ ] Pop-up scaling/easing
- [ ] Shadows behind panels/PNGs
- [ ] Button hover/press feedback where relevant
- [ ] Red notification dots
- [ ] Reward fly-in/claim animation
- [ ] `[C][D][T]` New Girl obtained presentation — web/summon-anim.js: máquina fx_ui_gacha_revision (putong/gaoji/friend 04→01→02→03, deslizar hacia abajo), intro 5★ "222", revelación dorada gaino (≥5★, espera toque) o morada gainp (<5★, izquierda/derecha), sonidos originales
- [ ] Level-up presentation
- [ ] Star-up/promotion presentation
- [ ] Currency count animation
- [ ] Loading transitions
- [ ] Screen transitions
- [ ] Tooltips
- [ ] Confirmation dialogs
- [ ] Error dialogs
- [ ] Announcement banner
- [ ] Scroll behavior
- [ ] Tabs
- [ ] Pagination
- [ ] Badge/count indicators
- [ ] Back-button behavior
- [ ] Aspect-ratio/resolution behavior

---

# 26. SETTINGS

- [ ] Music volume
- [ ] SFX volume
- [ ] Voice volume
- [ ] FPS options (30/60 where present)
- [ ] Announcement toggle
- [ ] Language
- [ ] Notification settings
- [ ] Account/data options
- [ ] Support/info/legal screens as archival stubs if desired
- [ ] Graphics/performance settings if present

---

# 27. AUDIO

- [ ] BGM inventory
- [ ] Home BGM
- [ ] Campaign BGM
- [ ] Battle BGM
- [ ] Event BGM
- [ ] Menu/UI SFX
- [ ] Battle SFX
- [ ] Girl voices
- [ ] Skill voices
- [ ] Home interactions
- [ ] Date/Oath voices
- [ ] Audio IDs/path mapping
- [ ] Loop points
- [ ] Volume categories
- [ ] Missing audio report

---

# 28. VISUAL ASSET INVENTORY

- [ ] Girl portraits
- [ ] Full-body Girl PNGs
- [ ] Animated Girl assets
- [ ] Battle sprites/assets
- [ ] Skins
- [ ] Skill FX
- [ ] Buff/debuff icons
- [ ] Backgrounds
- [ ] Campaign maps
- [ ] UI atlases
- [ ] Buttons
- [ ] Frames
- [ ] Currency icons
- [ ] Item icons
- [ ] Gear icons
- [ ] Antique icons
- [ ] Furniture
- [ ] Event art
- [ ] CGs
- [ ] Manga
- [ ] Fonts
- [ ] Localization images/text baked into images
- [ ] Loading screens
- [ ] Logos
- [ ] Unidentified assets bucket

For every extracted asset retain original path/name/hash when possible.

---

# 29. LOCALIZATION / TEXT

- [ ] Language list
- [ ] UI strings
- [ ] Girl names
- [ ] Girl biographies
- [ ] Skill descriptions
- [ ] Item descriptions
- [ ] Story dialog
- [ ] Event dialog
- [ ] Quest text
- [ ] Shop text
- [ ] Tutorial text
- [ ] System/error text
- [ ] Voice subtitles
- [ ] Original string IDs
- [ ] Placeholder/formatting syntax
- [ ] Missing-string fallback

---

# 30. TUTORIAL / NEW PLAYER FLOW

- [ ] First launch
- [ ] Intro/story
- [ ] Forced tutorial battles
- [ ] First Girl/recruit
- [ ] Menu unlock sequence
- [ ] Tutorial hand/finger indicators
- [ ] Tutorial highlights
- [ ] Forced clicks
- [ ] Tutorial rewards
- [ ] Early campaign progression
- [ ] Beginner missions
- [ ] Tutorial skip/replay (Reborn option)

---

# 31. DATA RECOVERY / REVERSE-ENGINEERING INDEX

Every discovery from APK/client/cache/server captures should be categorized here rather than left only in chat history.

## Client

- [ ] APK package inventory
- [ ] Native libraries
- [ ] Managed/code assemblies where applicable
- [ ] Scripts
- [ ] Asset bundles
- [ ] Resource tables
- [ ] Config files
- [ ] Databases
- [ ] Cached downloaded assets
- [ ] Obfuscated/encrypted resources
- [ ] Localization files
- [ ] Endpoint strings
- [ ] Version strings
- [ ] Feature flags
- [ ] Internal IDs

## Network/server reconstruction

- [ ] Endpoint catalog
- [ ] Request schemas
- [ ] Response schemas
- [ ] Authentication/session behavior
- [ ] Player-state endpoints
- [ ] Inventory endpoints
- [ ] Girl endpoints
- [ ] Battle endpoints
- [ ] Campaign endpoints
- [ ] Event endpoints
- [ ] Guild endpoints
- [ ] PvP endpoints
- [ ] Shop endpoints
- [ ] Mail endpoints
- [ ] Time/reset endpoints
- [ ] Static configuration delivery

## Unknown discoveries

Add every unknown with a stable ID:

```text
UNKNOWN-0001
Source: <file/endpoint/screen>
Observed: <what we know>
Hypothesis: <optional>
Status: [?]
Owner: NONE
```

---

# 32. ORIGINAL PLAYER SAVE RECOVERY ⭐⭐⭐

This is a separate milestone because success here would allow preservation of previously earned/purchased content.

- [ ] Locate remaining local account identifiers
- [ ] Locate local player/cache databases
- [ ] Locate auth/session remnants
- [ ] Locate cached player profile responses
- [ ] Locate inventory snapshots
- [ ] Locate Girl roster snapshots
- [ ] Locate skin ownership data
- [ ] Locate purchase/entitlement-related local records where present
- [ ] Locate progress/campaign state
- [ ] Locate guild/social state where useful
- [ ] Determine which state was server-authoritative
- [ ] Determine whether uploaded/archive data contains player state
- [ ] Build read-only parser first
- [ ] Produce human-readable recovery report
- [ ] Build conversion into Reborn save format
- [ ] Validate counts/IDs
- [ ] Never overwrite original evidence during import
- [ ] Manual correction layer for incomplete recovered state

---

# 33. REBORN DESIGN LAYER

All entries here are intentional modifications, not reconstruction claims.

- [ ] Fully offline operation
- [ ] Remove real-money requirement
- [ ] Convert paid currencies/content into gameplay rewards
- [T][M] VIP progression obtainable normally (LOCAL-050)
- [ ] Paid/exclusive antiques obtainable normally
- [ ] Event auto-rotation
- [ ] Permanent event archive/replay
- [ ] Simulated PvP
- [ ] Simulated guild
- [ ] Simulated friends
- [ ] Local mail
- [ ] Improved idle endgame
- [ ] Improved Tests/Quiz/PVE rewards where appropriate
- [ ] Better event-material economy
- [ ] Make obsolete Girls useful
- [ ] Explore full progression for low-star Girls
- [ ] Reduce dominant meta
- [ ] Counterplay-oriented balancing
- [ ] Preserve an Original/Classic balance mode if practical
- [ ] Optional sandbox/debug mode
- [ ] Optional event calendar controls
- [ ] Optional accelerated progression for testing

---

# 34. RESEARCH SOURCES / LEADS

Use sources as evidence, not as automatic truth. Reconcile community documentation with actual client data whenever possible.

- Girls X Battle 2 Fandom wiki — general mechanics, Battle Girls, skins, Patrol, Guild, Enroll, story, events.
- Japanese GxB2 Wiki / WikiRu — older system/menu documentation and character data.
- Community Google Sites guide/archive — leads to guides/spreadsheets for Tests, Galaxy Voyage, Stellar Altar, Astral Core, damage formula, antiques, etc.
- Version histories / app update notes — important for late-added modes and renamed systems.
- YouTube/gameplay recordings — UI, animations, exact flows, event behavior.
- Reddit/community posts — useful leads and historical screenshots; verify against stronger evidence.
- APK/client/cache files — primary technical evidence for shipped client content.
- User's own archived game files/data — highest-priority source for preservation and possible save recovery.

### Known web starting points

- https://girls-x-battle-2.fandom.com/wiki/Girls_X_Battle_2_Wiki
- https://girls-x-battle-2.fandom.com/wiki/Battle_Girls
- https://girls-x-battle-2.fandom.com/wiki/Patrol
- https://girls-x-battle-2.fandom.com/wiki/Guild
- https://girls-x-battle-2.fandom.com/wiki/Enroll
- https://girls-x-battle-2.fandom.com/wiki/Main_Story
- https://girls-x-battle-2.fandom.com/wiki/Skin
- https://girls-x-battle-2.fandom.com/wiki/Exclusives
- https://gxb2.wikiru.jp/
- https://sites.google.com/view/girlsxbattle2/home

---

# 35. AGENT WORKBOARD TEMPLATE

Copy active jobs into `AI_WORKBOARD.md`.

```markdown
# ACTIVE TASKS

## GXB2-XXXX
Status: [W:GPT]
Owner: ChatGPT
Started: YYYY-MM-DD
Goal: ...

Locked files:
- ...

Dependencies:
- ...

Findings:
- ...

Next step:
- ...

---

## GXB2-YYYY
Status: [W:CLAUDE]
Owner: Claude
Started: YYYY-MM-DD
Goal: ...

Locked files:
- ...
```

### Agent handoff format

```markdown
## HANDOFF — GXB2-XXXX
From: ChatGPT
To: Any available agent
Status: [P]

Completed:
- ...

Verified:
- ...

Not verified:
- ...

Files changed:
- ...

Do not change:
- ...

Recommended next action:
- ...
```

---

# 36. DISCOVERY INBOX

Put newly noticed things here immediately. They can be categorized later.

- [ ] DISCOVERY-0001 —
- [ ] DISCOVERY-0002 —
- [ ] DISCOVERY-0003 —

---

# 37. MAJOR MILESTONES

- [ ] **M0 — Inventory:** client/files/assets/endpoints catalogued
- [ ] **M1 — Boot:** game reaches reconstructed home screen reliably
- [ ] **M2 — Persistence:** local profile/save/reset cycle reliable
- [ ] **M3 — Girls:** roster/progression/equipment functional
- [ ] **M4 — Combat:** faithful deterministic combat engine functional
- [ ] **M5 — Campaign:** campaign + idle loop playable
- [ ] **M6 — Core PVE:** Tests/Patrol/etc. playable
- [ ] **M7 — Economy:** summon/shops/items/quests functional
- [ ] **M8 — Social replacements:** guild/friends/PvP work offline
- [ ] **M9 — Events:** event framework and rotation functional
- [ ] **M10 — Late game:** Galaxy/Servants/advanced systems functional
- [ ] **M11 — Preservation:** stories/skins/audio/collections substantially restored
- [ ] **M12 — Save recovery:** old player progress import attempted/validated
- [ ] **M13 — Reborn balance:** optional redesigned progression/balance implemented
- [ ] **M14 — Preservation release:** reproducible build + documentation

---

# 38. DEFINITION OF DONE

The reconstruction is considered preservation-complete only when we can answer these questions:

- Can a fresh player begin and progress without an external server?
- Can the game be closed and reopened without losing state?
- Do daily/weekly/event timers behave correctly?
- Are Girls, skills, equipment and combat data sufficiently faithful?
- Are Campaign and idle progression playable?
- Are the major PVE modes preserved?
- Are acquisition, inventory, currencies and stores functional?
- Can events rotate indefinitely without a live service?
- Have online-only systems received sensible offline replacements?
- Are story, character, skin and other collection assets accessible?
- Can previously archived player data be imported when technically recoverable?
- Are intentional Reborn changes clearly separated from original-game reconstruction?
- Can ChatGPT, Claude or another agent resume work from the repository documentation without relying on old chat context?

If the last answer is **no**, documentation is not finished.

---

## Final principle

**Preserve first. Modify second. Document both.**

The goal is not merely to make something that resembles GxB2. The project should retain enough structure, data, behavior, art, progression and historical context that the game remains understandable and playable after its original online infrastructure is gone, while allowing a separate Reborn ruleset to fix the problems of the original live-service economy and endgame.


---

# 39. AUDIT / HANDOFF — 2026-09-28

Task: **GXB2-DOC-AUDIT-001**, Owner: **ChatGPT**, documentation audit completed. Gameplay implementation was not changed.

- `[T]` Existing suite: 38 tests passed on temporary saves; [log](validation/audit-2026-09-28/unittest.txt). This validates those cases, not complete preservation.
- `[P]` Reconstruction: local profile/persistence, original combat adapter, campaign/idle, Girls/equipment/summons, Tests/Quiz and parts of Events/Home systems. See the [38-section evidence matrix](ESTADO_PROYECTO.md).
- `[BLOCKED]` Tests floors 1501–2000 lack battle data in the current runtime; full original save import lacks identified inventory/roster/progress snapshots.
- `[M]` Local substitutions and uncertain server rules are registered in [DESIGN_DECISIONS](DESIGN_DECISIONS.md).
- `[?]` Full browser QA, all abilities/recipes, complete campaign and economic progression, save migrations, restore and original/Classic fidelity remain unverified.
- Next unclaimed priorities: **GXB2-TIME-001**, **GXB2-EVENT-RESET-001**, **GXB2-IDLE-SETTLE-001**. Details and acceptance criteria in [ESTADO_PROYECTO](ESTADO_PROYECTO.md).
- Discoveries **UNKNOWN-0001–0003** and **DISCOVERY-0004–0006** are recorded in the [discovery inbox](ESTADO_PROYECTO.md#discovery-inbox--desconocidos); they must not remain only in chat.
- Continue from [AI_WORKBOARD](AI_WORKBOARD.md): no implementation task is claimed by this audit; read/claim/lock before editing. Preserve original files and player saves.


---

## LOCAL RECONSTRUCTION UPDATE — GXB2-RECON-WAVE-001

Started 2026-09-28; closed 2026-09-29 local time. Original checklist preserved. No whole-game/system [X] claims. Owner ChatGPT; file locks released in [AI_WORKBOARD](AI_WORKBOARD.md).

| Checklist areas | Current implementation | Research / missing |
|---|---|---|
|3/15 Girls & acquisition | [T][P][M] Exchange proposal/save/discard/restart; LOCK_PARTNER manual flags; protected materials | Client contracts identified; server probabilities and variant dropbox_id_2 unresolved. |
|16 Slots | [T][P][M] Normal/High Stakes, eight rewards, limits/costs/coupons/points, free/paid/system refresh, history/persistence | Local weighted server replacement; cool/pity/animation/Lucky Store pending. |
|1/9/20 Time, idle & events | [T][P][M] injected clock, historical idle rates, weekly point periods and rollback checks | Original settlement/calendar unresolved; not all timers migrated/verified. |
|17/18 Economy/store | [R] shop_luck 22 entries recovered, [T] new costs/rewards | Lucky purchase not implemented; sources/sinks and sustainable economy pending. |

Discovered currencies: Portfolios 19, Normal Slot Tickets 35, High Stakes Tickets 29, Coupons 6; costs from tables. New message coverage: PROPHET_REPLACE, PROPHET_REPLACE_SAVE, GAMBLE_GET_INFO, GAMBLE_REFRESH, GAMBLE_GET_AWARD, LOCK_PARTNER. `flags` is the original lock field; `lock_flags` aliases are only compatibility, not original schema.

Evidence: [research and source hashes](validation/reconstruction-2026-09-28/RESEARCH.md), [47 tests and UI scope](VALIDACION.md), [current priorities](ESTADO_PROYECTO.md). Preserve server unknowns as explicit Reborn decisions in [DESIGN_DECISIONS](DESIGN_DECISIONS.md). Next: save/restore QA, Lucky Store, manual material selection, global timers and fidelity corpus. Paid NewLevelUpGiftBag is not a verified free reward feature.


## VISUAL REFERENCES — GXB2-REF-UI-002 (2026-09-29)

Nine user-provided screenshots archived with hashes in [reference index](docs/references/2026-09-29/README.md). [T][P] Exchange vertical/chibis and Normal Slots bulk selector; [R] Slot Points variant5 rounds vs current recovered8. No full system [X]. Holiday Break Exchange is an event shop distinct from ProphetReplace.

Discovery inbox: Holiday Break currencies/composite costs/limit1 and Gem Store; Atelier Valeera shop; Entrance Exam Strength/Endurance/Wisdom, simulation vs ticket battle, exclusive roster; Limit-Break5-node Switch and Astral Core tabs; Nobunaga Gift/Voice/CV and voice button families. Screens confirm existence/layout, not full rules or operating code. Record/version/unlock/audio evidence still required.

User clarification and client source confirm side selector for bulk draws; source edition cycles10/20/50 and stores preference. Quantity selection itself has no cost. API indices/cost/gates preserved, High Stakes does not get this selector.


### GXB2-REF-003 — High Stakes reference (2026-09-29)

[C][R] Tenth screenshot confirms visible High Stakes layout with seasonal dealer, Skip/Record/search and1/10 buttons; small quantities unverified. Original client maps Normal→girls_model3→gamble_girl and High Stakes→girls_model4→gamble_up_girl. Source skeleton/atlas/RGB/Alpha located, hashes in [asset map](docs/references/2026-09-29/slots-original-assets.json). Web export/render/dealer remains pending; source discovery is not implementation. [Reference10 and analysis](docs/references/2026-09-29/README.md#décima-captura-high-stakes).


### GXB2-SLOTS-LUCKY-004 — Slots / Lucky Store (2026-09-29)

[C][D][T] dealers gamble_girl/gamble_up_girl exportados y visibles; idle recuperado, FX/diálogo/audio pendientes. [C][D][P][M] Lucky Store SHOP_LUCK3: ocho ofertas, Coupons, nivel14, compra1/casilla, refresh24h o50 Coupons; API original/persistencia/costes probados. Muestreo y calendario son sustitución local explícita. [C][D][T][M] Skip por modo, Records local50, probabilidades locales y reloj vivo; bulk50/40 y persistencia de preferencias verificados tras recarga. [P] Slots global, no [X].

[Fuentes/49 tests/QA](validation/slots-lucky-2026-09-29/RESEARCH.md), [LOCAL-018/019](DESIGN_DECISIONS.md), [relevo](AI_WORKBOARD.md). Actualiza los pendientes REF-003 de dealer web y REF-UI-002 de compra50/preferencia. UNKNOWN: Lucky limit_num/muestreo original, calendario del servidor, cooldown de Slots, FX/voz, touch y resoluciones. Siguiente: save backup/restore/migración y contratos de tiendas/eventos aportados en imágenes.


## LOCAL RECONSTRUCTION UPDATE — GXB2-CLAUDE-WAVE-005 (Claude, 2026-09-29)

- `[T]` **12 Servants:** UI de lista, detalle (Attribute / Servant Aura) y detalles; nivel, evolución, auras y selección; **integración en combate con los ReportPet/ReportPetAttr originales**. `[ ]` Ulticore/ex-level, Reborn, Training.
- `[T]` **Excursion:** mapa original animado (travel_main), edificios Store / Wishing Tree / Food Truck (producción, recogida, mejora), Main Center (entrenamiento), compra de Tasty Bread con límite diario.
- `[T][M]` **Explore:** eventos ponderados, combates reales, cofres con temporizador, apertura con gemas, ranuras y bloqueo, subida de nivel, Auto Explore (LOCAL-020…023).
- `[T]` **25 UI:** marco fijo 480×853 para todas las pantallas (LOCAL-024).
- `[T]` **Dates/relaciones:** hecho en WAVE-006 (ver abajo).


## LOCAL RECONSTRUCTION UPDATE — GXB2-CLAUDE-WAVE-006 (Claude, 2026-09-29)

- `[T]` **6 Dates:** lista por intimidad, ventana de cita (escena, arte, corazones, barra), regalos con favoritos/×10/Compose, voces por intimidad, Data (bonus), Oath. `[ ]` bonus en combate, escenas de cita/Oath, marcos.
- `[T][M]` **19 Tasks/Trophies:** Daily Tasks con Go/Claim y tarea 11, Trophies en cadena medidos desde la partida. Botón Tasks en Inicio. `[ ]` semanales, Alchemy/Internship/Hearts (sin sistema).
- `[T][M]` **18 Stores:** Shopping Street (mapa original), Market, Girls Store, Antique Store y la ventana con pestañas (Sanctuary, League, Guild, House Exams; Lucky abre Slots). Tenderas Spine originales. `[BLOCKED]` Transfer (inventario generado por servidor), Skin Store.
- `[T][M]` **13 Junior Varsity:** 15 robots originales + rivales NPC persistentes, combate con el motor original, puntuación por banda, tickets, cartas de premio, premio diario y de temporada. `[ ]` Varsity 3v3, Elite League, defensa distinta de la formación.


## LOCAL RECONSTRUCTION UPDATE — GXB2-CLAUDE-WAVE-007 (Claude, 2026-09-29)

- `[T]` **31 Inventario del cliente:** `tools/build_client_inventory.py` genera [INVENTARIO_CLIENTE](INVENTARIO_CLIENTE.md) desde la descompilación: 71 modelos de juego → ventanas, tablas y mensajes, con su estado local. Volver a ejecutarlo en cada tanda y mantener el mapa `LOCAL` del script.
- `[T][M]` **10 Patrol:** completo en backend, UI y QA (ver sección 10). Batallas 300001–301644 presentes en el motor recuperado. `[ ]` Auto Smash en la UI solo muestra el resumen; faltan el mercader Spine `dungeon_web`, el Game Assistant y la tarjeta de privilegio (pago).
- `[?]` **Discovery inbox (desde el cliente):** sistemas no listados antes en este master: **Soul Equip 1/2 + Soul Land**, **Govern Team** (clima/despliegue), **Show Window**, **Chime**, **GrowthDiary**, **NewbieCamp**, **PartnerDataStation/PartnerComment**, **FairArena**, **Shrine / Shrine Hurdle**, **Game Assistant** (sweep automático), fondos personalizados (`custom_background`) y minijuego del perro (`dog_mini_game`). Character Challenge del historial de versiones = modelo `HeroChallenge`. Estado y tablas en INVENTARIO_CLIENTE.


### GXB2-PORTRAITS-008 — iconos de chicas (2026-09-29)

[C][D][T] avatar indicado por partner.avatar integrado en portrait común:439 originales,637 IDs/359 visibles resueltos. Legado81 mantenido como fallback; Selene y variantes resueltas sin inferir ID de archivo. Recursos/HTTP/JS y UI invocación/formación comprobados; no es [X] de Girls global ni validación de todas las caras/vistas.10 filas auxiliares/no visibles sin fuente en el catálogo actual registradas como desconocidas. [Manifest, referencia y handoff](validation/portraits-2026-09-29/README.md).

### GXB2-REF-UI-004 — segunda tanda de capturas (Claude, 2026-09-29)

[Diez capturas con hashes](docs/references/2026-09-29-b/README.md). `[T]` La vista de **Patrol** se rehízo según la captura 10: mapa de la fase (`map_source`/`map_scale`/`map_position`), chibi de la chica y del primer enemigo, efectos Spine originales (`difangchuchang`, `chuchangtongyong`, `chuansongmen`) y mercaderes por nivel (`zhanghongpifu`, `shengdanxueqiao`, `mizhubaozang`), título con cuenta atrás en horas, columna de Rice Balls, casilla Skip, botón de espadas y 5 tarjetas. `[?]` Discovery: el juego **cerró el 30/06/2025** (correo de sistema); Correo con 3 pestañas, capacidad 40 y "reclamar todo"; Menú con Get Stronger, Community, GM y Urgent news; Ajustes con Diagnose, Red dot y Notification; Chicas con capacidad 167/285 ampliable y filtro "Favoritas"; **Demon Exam = `AcademyAssessment`** (House Exam por facción, Raid/Battle, dos tickets); pantalla de derrota con Rematch. Todavía `[ ]`: tarjeta de privilegio de Patrol (pago; se muestra "Unactivated").


### Descubrimiento29/09 — Capsules y huevo (GXB2-CAPSULE-EGG-009)
- [C][D][P][M] BAODI/huevo: item12, SUMMON9, coste1.000, pool10003 de5★; puntos por advanced `summon.award`. Claim/overflow/reinicio/BFF separados comprobados. Cliente original exigeVIP3, Reborn permite umbral por petición; FX/espacio siguen pendientes.
- [C][D][P] BFF: item11, SUMMON15/16, coste10/100, pool10005. Corrige ruta anterior9 (huevo) y corazones12; no altera saldos ni historial.
- [C][R] Alfheim/Restore Engine Season2/DailyQuiz nuevas referencias: [archivo](docs/references/2026-09-29-c/README.md). No declarar sistemas completos por captura.
- Evidencia/handoff: [validación](validation/capsule-egg-2026-09-29/README.md).

### GXB2-CLAUDE-WAVE-009 — animación de invocación e investigación de Sanctuary y Character Challenge (Claude, 2026-09-29)

- `[C][D][T]` **Animación de invocación** según `SummonResWindow`, `SummonEffectResWindow` y `PartnerSummonEffect`, con Spines, fondo y sonidos originales. **Variante de 5★:** antes de su revelación se reproduce el "222" de la máquina (`vd_egg_5star`) y la revelación usa `fx_ui_newgirl_gaino` (dorada; `texiao01` y después `texiao04` en bucle), esperando un toque. Las chicas de menos de 5★ usan `gainp` (morada), alternando izquierda y derecha sin pausa.
- `[R][BLOCKED:diseño]` **Sanctuary** (`Trial`, `new_trial_*`): 9 fases (Normal, Elite con buff, Blessing, Tienda y Jefe que revive con premios por daño), Chaos Crystals, rueda, reset diario y pase de 30 días. Las fases 1-7 no tienen `battle_id`: el servidor generaba los enemigos a partir del poder del jugador (`power` 0,2–0,35, `new_trial_match_chance/partner`), y los buffs son habilidades que se inyectan en el combate. Hacen falta decisiones de diseño antes de implementarlo.
- `[R]` **Character Challenge** (`HeroChallenge`, `partner_challenge*`): 12 fuertes × 10 fases, con las 120 batallas presentes en el motor. Las chicas prestadas son monstruos de atributos fijos (`partner_challenge_box`), y tras cada victoria se elige entre chicas, buffs o servants (`reward2 "tipo#n"`; los candidatos los generaba el servidor). Los tickets se regeneran cada 30 min hasta 10; al perder, esas chicas quedan fuera; el reset cuesta 1 ticket. Los modos Puzzle, Speed y Chess van aparte.


## Actualización 29/09/2026 — Guild Lab (ChatGPT, GXB2-GUILD-LAB-010)

Estado global Guild `[P][M]`; laboratorio con80 mejoras originales/5clases/2páginas, costes/prerrequisitos/máximos, guardado y reset gratuito primero/pagado después. Acceso Inicio→Gremio→Territorio→Laboratorio. Bonos conectados a atributos y combate Lua original según clase. Pantalla cotejada con la captura original Lab y prefab.99/99 pruebas (9 nuevas), QA temporal separada, sprites requeridos recuperados. APIs originales `GUILD_GET_SKILLS`, `GUILD_UPGRADE_SKILL`, `GUILD_RESET_SKILL` en `/api/action`.

[Evidencia, diferencias y handoff](validation/guild-lab-2026-09-29/README.md) · [6 capturas originales](docs/references/2026-09-29-d/README.md). Pendientes: economía/membresía/actividades Guild, cascada de reset original, FX/audio; regalos/Oath/dificultades capturados archivados, sin declarar completos por imagen. Sin moneda gratis en normal; DEV permite explorar Lab con moneda4. Fuentes y saves habituales preservados. Reiniciar servidor habitual y recargar para nuevo backend.

### GXB2-CLAUDE-WAVE-010 — Character Challenge, Sanctuary y barra del Servant (Claude, 2026-09-29)

- `[T][P][M]` **Character Challenge** (Normal + Puzzle): 12 desafíos × 10 fases, las 120 batallas originales, chicas-monstruo, elecciones de chica, bendición o Servant, Coupons con regeneración, muertes al perder y reset. Speed y Chess quedan `[ ]`.
- `[T][P][M]` **Sanctuary:** mapa original (volcán y mar), postes, banderas y puntos según `new_trial_offset`, medallón del jefe, barra de daño del jefe con cofre y número de tramos. Siguen `[ ]` la rueda de Chaos Crystals y el pase de Sanctuary.
- `[T]` **Combate:** la barra inferior es la energía del Servant (capturas del usuario, docs/references/2026-09-29-c).

### GXB2-CLAUDE-WAVE-011 — Internship y Alchemy (Claude, 2026-09-29)
- `[T][M]` **Internship** jugable desde Campus → Intern: encargos diarios, condiciones, selector con Auto, temporizador, aceleración, reclamo, bloqueo, refresco y pergaminos.
- `[T][M]` **Alchemy (Midas)**: reclamo gratis y compras con gemas, desde el oro de Inicio. Las tareas diarias de Alchemy e Internship ya avanzan (solo Hearts sigue sin sistema).

### GXB2-CLAUDE-WAVE-012 — Old Campus Exploration (Claude, 2026-09-29)
- `[T][P][M]` Old Campus jugable según las capturas 04-05 de docs/references/2026-09-29-e. Sus capturas de **Echoes of Time** (incluida la pantalla principal con la esfera, "Skyless Shrine") y de **Galaxy Voyage** quedan archivadas para las próximas tandas.

### GXB2-CLAUDE-WAVE-013 — Echoes of Time (Claude, 2026-09-29)
- `[T][P][M]` **Echoes of Time** jugable desde Liga, según las capturas del usuario (2026-09-29-e 01-03 y 2026-09-29-f 01-07):
  - esfera de mundos (I–VI);
  - tablero con la barra I–XII y 12 cartas;
  - mazos Supply/Challenge/Encounter y Record;
  - Planetarium I/II con las posiciones originales;
  - fases con Temporal Chips y Time Vortex;
  - logros con progreso y desbloqueo al 85 %.
- `[T]` Ventana de logros de Echoes ajustada a la captura 2026-09-29-g/03: Total Progress con pasos **reclamados** (igual que el cliente), Go / Claim / sello Collected y botón «!». Capturas de Skins, Yume Collection y el Santuario Tsuruga (Realm of Trials) archivadas.

### GXB2-CLAUDE-WAVE-014 — Santuario Tsuruga (Claude, 2026-09-29)
- `[T][P][M]` **Santuario Tsuruga (Realm of Trials)** jugable desde Liga, según las capturas 2026-09-29-g/04-07:
  - entrada con 4 zonas y el prólogo;
  - 3 pruebas por temporada, dificultad 1-300 y 15 fases;
  - vida persistente y buffs;
  - Message Board (tareas y logros) y Pond of Prayers.
- Tree of Chimes queda pendiente.

### GXB2-HOUSE-DRESS-014 — House / Outfit (ChatGPT, 29/09/2026)
- `[C][R]` Recuperados House/Dress,297 muebles,269 ofertas,13 series,425 estilos/1410 piezas,276 modelos Spine, accesorios y fondos originales. Monedas69 (Furniture Store) y258 (Outfit Store), pisos y dotación inicial están documentados.
- `[T][P][M]` Editor/tienda/guardado House, confort de inventario, selección propia y segundo piso; Locker Room/Closet base con equipamiento/preview/persistencia.9 tests específicos OK. Global secciones21/Outfit siguen parciales.
- `[R][ ]` Outfit gacha: datos/dropboxes/costes recuperados; probabilidad/soft pity sin acreditar y tiradas desactivadas. Visitas/ingreso/FX/interacciones House pendientes.
[Evidencia, límites y handoff](validation/house-dress-2026-09-29/README.md).

### GXB2-CLAUDE-WAVE-015 — Galaxy Voyage (Claude, 2026-09-29)
- `[T][P][M]` **Galaxy Voyage** jugable desde Cosmos Portal, según las capturas 2026-09-29-e/06-08:
  - 8 sistemas más System of Eternity;
  - mapas de cuadrícula generados, exploración con tiempo y rutas, enemigos con vida persistente, Ruler debilitable;
  - Galaxy Tyrant 1-20 y piratas espaciales;
  - Voyage Teams, Voyager Passport, tareas y tienda.
- Falta una captura del mapa de un sistema por dentro para ajustar el generador (LOCAL-038).
- `[P]` Galaxy Voyage ajustado con las capturas 2026-09-29-h (mapa por dentro, rutas, exploración, Details). Pendiente: igualar la ventana Battle (poder, fila de buffs, filtro de facciones).

### GXB2-CLAUDE-WAVE-016 — Historia principal (Claude, 2026-09-29)
- `[T][P]` **Historia principal:**
  - las escenas de la campaña salen antes del combate y tras la primera victoria (por ejemplo la ceremonia de apertura en 1-3);
  - reproductor con fondos, personajes, nombres, voces, música, Auto, Recall y Skip;
  - **Memories** (Menú → Recuerdos) con episodios, capítulos y desbloqueo por fase o Key of Memory.
- `[P]` Ventana Battle de Galaxy igualada a la captura: poder real, auras de facción y filtro.
- Capturas de Outfits (Locker Room / Closet / tienda), Wallpaper y Gallery archivadas en 2026-09-29-i para la próxima tanda.


### GXB2-CARDS-CAMPUS-015 — ChatGPT,29/09/2026
Campus elevado60px de lienzo; tarjetas compactas con marco original, nombre sobre retrato, emblemas según estrellas/facción y hover sin desplazamiento. QA visual9232 sobre partida temporal, filtros/detalle/galería e imágenes revisados, sintaxis JS válida. [Evidencia y límites](validation/cards-campus-2026-09-29/README.md). Incremento visual entregado; sistemas globales siguen parciales. Claims015 liberados. No cambios de backend ni guardados habituales.

### GXB2-CLAUDE-WAVE-017 — Outfits (Claude, 2026-09-29)
- `[T][P][M]` **Outfits** jugables desde Campus (Outfit / Outfit Store), según las capturas 2026-09-29-i y 2026-09-29-j:
  - **Locker Room:** chibi vestido con los Spines originales, 5 posiciones, estilos, Set, triángulo de atributos y Special Bonus;
  - **Closet:** con Gallery y Outfit Upgrade (seda y fragmentos);
  - **Outfit Store / Sale:** con garantía de naranja a 100.
- Los atributos de los Outfits ya alimentan Echoes of Time.

### GXB2-CLAUDE-WAVE-018 — Skins (Claude, 2026-09-29)
- `[T][P][M]` **Skins de chicas** (pestaña Skins de la ficha, como la captura 2026-09-29-g/01):
  - 336 skins con su retrato, su chibi de combate y sus atributos;
  - se ponen y se quitan desde la bolsa y se pueden ocultar en combate;
  - cuentan para la colección.

---

# 40. ACTUALIZACIÓN DE COBERTURA — 2026-09-30

Esta matriz actualiza las secciones 1–38 sin reescribir sus casillas históricas. Base: código y relevos [WAVE-019–048](AI_WORKBOARD.md); la última suite comunicada fue **271 pruebas**, pero el número de pruebas no equivale a porcentaje de reconstrucción ni a fidelidad total. `[T]` significa probado en el alcance indicado; `[P]` significa que el sistema global sigue incompleto; `[M]` señala sustituciones locales documentadas en [DESIGN_DECISIONS](DESIGN_DECISIONS.md). Ningún sistema global se declara `[X]` aquí.

| Secciones | Estado actual comprobable | Falta para cerrar el sistema |
|---|---|---|
| 1–2 Infraestructura, perfil y partida | `[T][P][M]` Servidor y guardado local, partida normal/DEV, reloj monótono y día/semana según hora de la máquina (W35–36). `tools/save_archive.py` hace copia SQLite en caliente y restaura en una ruta nueva, con integridad y sin sobrescribir (tanda049). | **P0** Migraciones antiguas y restauración integral en el flujo de la app; importación fiable de partida original e instalación portátil. |
| 3–4 Chicas y progresión | `[T][P][M]` Ficha de pantalla completa, Gear, Limit-Break, Astral Core, Potential, Anima, Souls, Switch/Reverse/Exchange, formación y variantes de 5★ (W19–24,43,45,47–48). | Contrastar todas las habilidades, combinaciones, costes, progresión y casos extremos con el cliente original. |
| 5–6 Skins, Outfits y relaciones | `[T][P][M]` Skins, Locker Room/Closet/Outfit Store, Showcase, Gift/Voice/Oath; cartas de reediciones y Wallpaper con skins (W17–19,29,47–48). | Escenas y efectos completos de relaciones, probabilidades y arte faltante; pruebas visuales/táctiles de todas las variantes. |
| 7–9 Combate, historia e idle | `[T][P][M]` Motor Lua original, escenas/Memories, formación y transición Battle de campaña, tarifa idle histórica (W16,34,42,44); bonos de Tree of Chimes aislados por partida (tanda049). | **P0** Corpus amplio de habilidades y reproducción de reportes originales; contrastar la liquidación idle al cambiar fase con el servidor original. |
| 10–11 PVE y Cosmos | `[T][P][M]` House Exam, Patrol, Character Challenge Normal/Puzzle, Sanctuary, Old Campus, Echoes, Tsuruga/Tree of Chimes, Galaxy Voyage y Lost Space (W08–16,21,33,44). | Speed/Chess, rueda/pase de Sanctuary, reglas server y temporadas, mapas/recompensas/eventos completos. |
| 12–14 Servants, PvP y Gremio | `[T][P][M]` Servants, Junior Varsity, Lab de 80 nodos y Gremio v1 con Office/Gym/Cafeteria (W05–07,37,42). | Servant Training/Reborn/Ulticore; Varsity 3v3/Elite; Guild War/Playground, economía y sociabilidad de gremio. |
| 15–18 Invocación, Slots, economía y tiendas | `[T][P][M]` Cápsulas/huevo 1000 puntos, Wish Capsule, Slots Normal/High Stakes con x10→50/40, Lucky Store, Transfer/Altar y tiendas principales (W09,30,45–46). | Distribuciones originales y calendario de tienda, límites server, todos los productos y economía sostenible sin DEV. |
| 19–20 Tareas y eventos | `[T][P][M]` Tareas, VIP por logros, kit genérico de 28 actividades y 8 sorteos, Jackpot, Wish Upon a Chime, Blind Box, Deep Sea/Palace, Pumpkin Patch, Jigsaw, Puppet Parade y Firework Project (W31–41, tandas052–053). | **P0** Calendario real de inicio/fin; minijuegos propios restantes (Winning Pair, Tea Party, etc.), resets y arte fiel. |
| 21–24 Dorm, colección, manga y social | `[T][P][M]` Dorm/editor, Collection/Wallpaper, Manga con páginas recuperadas, Memories y partes del perfil (W25,28,45–48). | Visitas e interacciones sociales, pisos/temas/muebles y reglas no documentadas; correo/amigos/chat/club completos. |
| 25–30 Interfaz, ajustes, audio y tutorial | `[T][P][M]` UI de tamaño fijo, pantalla Girls/filtros, navegación Campus/Gremio/Slots, menú de ajustes, animación de cápsulas y recursos originales (W09,34,45–48). | Auditoría visual sistemática en tamaños y tacto, audio/voces/FX de todos los flujos, idiomas, accesibilidad y tutorial. |
| 31–33 Recuperación y diseño Reborn | `[R][P][M]` Inventario generado del cliente, referencias archivadas, sustituciones locales registradas. | **P0** Save original verificable; completar índice de protocolos/tablas/assets y separar reglas originales de adaptaciones antes de ajustar balance. |

Prioridades de trabajo, en orden: **1)** migraciones de formatos antiguos y restauración desde la interfaz; **2)** corpus de regresión de combate; **3)** calendario y liquidación temporal de eventos/idle; **4)** mecánicas exclusivas de eventos y modos pendientes; **5)** pulido visual/audio con comparación de capturas. Las tareas concretas y bloqueos vigentes se reclaman en [AI_WORKBOARD](AI_WORKBOARD.md); la matriz de [ESTADO_PROYECTO](ESTADO_PROYECTO.md) conserva hallazgos anteriores y esta actualización prevalece cuando hay contradicción. La tanda049 cerró el aislamiento de Chimes y la herramienta básica de backup/restore en ruta nueva con **274 pruebas aprobadas**; no acredita importación del guardado original ni migraciones antiguas.


## Recuperación original — tanda050, 2026-09-30

[R][P] Android auditado: 31 formaciones anónimas, 62 chicas sin identificar y preferencias; no contiene roster/inventario completo y no permite migración jugable. Herramientas de auditoría y lector de índice de respaldo iPad implementados, con 5 pruebas específicas aprobadas. El usuario conserva la app en iPad, pero falla por conexión. Próximo paso: obtener respaldo Finder y comprobar archivos de la app. Importación completa sigue pendiente; no se tocó la partida habitual. [Evidencia](validation/original-save-2026-09-30/README.md).


## Recuperación iOS — tanda051, 2026-09-30

[T][R][P] Exportación iMazing de iPhone japonés analizada sin modificar: 71 filas de formación, cuatro cuentas separadas, 45 selecciones de estilo y caché histórica de 24 conjuntos en la cuenta principal de la caché. Sin roster completo ni inventario actual; personaje especial de Guild Competition excluido de importación por ser modificable. Auditor de exportación implementado y 3 pruebas específicas OK. La migración completa continúa pendiente. Próxima fuente posible: exportación del iPad, sin asumir que contiene la cuenta completa. [Informe](validation/ios-save-2026-09-30/README.md).

## Eventos — tanda052, 2026-09-30

[T][P][M] Jigsaw (37) y Puppet Parade (189) jugables en Inicio → Eventos → Exclusives. Jigsaw conserva 24 ilustraciones, las 216 piezas originales, intercambio de dos posiciones por 1 energía, 50 compras progresivas y seis hitos. Puppet conserva 17 hitos y sus premios; las marionetas no se consumen al cobrar. Progreso persistente y premios protegidos contra doble cobro. LOCAL-070 sustituye el calendario/suministro del servidor: eventos permanentes, 3 energías y 40 marionetas diarias, premios directamente a la bolsa. Falta la presentación/animación completa y el calendario original. Suite completa: 303/303 OK; siete pruebas propias y QA visual con partida temporal. [Evidencia](validation/events-2026-09-30/README.md). Próximo foco: Firework Project, Winning Pair y calendario de eventos.

## Firework Project — tanda053, 2026-09-30

[T][P][M] Firework Project 196 jugable en Inicio → Eventos → Exclusives: fabricar ×1/×10, cuatro resultados ponderados (15/50/20/15), coste de 25 polvos, nivel por 100 polvos gastados, 21 canjes con niveles y límites originales. No confundir con Firework Display 274. Estado persistente; operaciones inválidas no gastan recursos. LOCAL-071: archivo permanente y 250 polvos por día local para sustituir fuentes del servidor. Faltan calendario, fuentes originales de polvo y animación Spine de fabricación. Siete pruebas específicas; suite completa 311/311 OK. [Evidencia](validation/firework-2026-09-30/README.md). Siguiente foco: Winning Pair y calendario de eventos.

## GXB2-PORTRAITS-059 — 30/09/2026

[x] Cayla11002 y Kitty31004: ilustraciones originales recuperadas de local_tex; Graduate deja de ampliar sus tarjetas como si fueran dibujos completos. Índice535→537, sin perder skins. Carga del índice antes del primer render y reconocimiento full-art en Graduate. QA navegador de ambas; sintaxis JS y prueba de orden/filtros OK. No altera progresión ni saves. [Evidencia](validation/portraits-2026-09-30/README.md).

[~] Nuevas referencias: inventariadas4311 imágenes de Downloads/Reference, subcarpeta Graduate confirmada. [Inventario](docs/references/2026-09-30-graduate/README.md). Pendiente revisión visual y aplicación al resto de pantallas; no dar esos sistemas por reconstruidos.


## Pulido visual y tarjetas de skins — GXB2-POLISH-060, 2026-09-30

- [x] Graduate: encuadre por límites visibles de la ilustración (537 imágenes), estrellas originales, retratos disponibles sin apagado artificial y diálogo original.
- [x] Colección: equipar una skin cambia la tarjeta de esa copia; quitarla devuelve la tarjeta base. No altera otras copias de la misma chica. Galería prioriza 323 tarjetas originales de skins y señala ilustraciones pendientes.
- [x] Barras, pestañas y marcos: refinamiento de bordes, navegación inferior y paneles del gremio; entrada directa al territorio cuando ya existe gremio desbloqueado.
- [x] Menú: saldos sin solapamiento con Volver, navegación inferior dentro del lienzo y botones clonados de navegación operativos.
- [x] QA en partida de desarrollador separada: Alice 10★ equipar → recargar → quitar; otras copias conservan su tarjeta base. 6 pruebas de skins y 7 de promoción local, comprobación de orden/filtros Graduate y sintaxis correctas.
- [ ] Continuar revisión visual de Dorm, vestuario, eventos y demás pantallas usando referencias. El inventario de 4.311 referencias no equivale a revisión completa.

Evidencia y alcance: [validation/polish-2026-09-30/README.md](validation/polish-2026-09-30/README.md).


## Graduate — referencia de filtros y atributos, 2026-09-30

- [x] Filtros verticales con un emblema y número: amarillo 2–5, rojo 6–9 y naranja/dorado 10. Se conserva multiselección on/off y orden existente sin filtros.
- [x] Tres líneas: comparación real de atributos actual/después y límite de nivel, sin escribir en la partida. Ya no abre materiales ni lleva marcador de recetas listas.
- [x] Casilla Auto-seleccionar materiales de 5★ operativa, inicialmente apagada; revisión manual independiente debajo de la receta. Copias específicas y materiales de otras estrellas mantienen selección previa.
- [x] QA desarrollador separado: Sakura 6→7, off/on, preview Vida 43819→74865 y Ataque 5826→6836; diez pruebas de promoción/preview y pruebas JS correctas.
- Evidencia: validation/polish-2026-09-30/graduate-filters-reference.png y graduate-attributes.png.


## Graduate — ayuda visual y selección manual, 2026-09-30

- [x] «?» abre la guía original aportada por el usuario, con notas en español sobre filtros, atributos y materiales. Ventana cerrable con × o Escape y retorno de foco. Cabecera visible al desplazar la guía.
- [x] Las tarjetas de base/materiales abren el selector correspondiente. El selector excluye copias elegidas en otros huecos, bloqueadas como material e intercambio pendiente.
- [x] QA en partida desarrollador separada: Sakura 6→7; materiales 89,90,91,92 distintos, el 89 deja de aparecer en Material 2. Receta completa y botón habilitado, sin ejecutar Graduate.
- Evidencia: validation/polish-2026-09-30/graduate-help.png. Fuentes y guardados habituales intactos.


## Ajuste de referencia — ALL y filtro exclusivo, 2026-09-30

La instrucción nueva del usuario sustituye la multiselección anterior: ALL seleccionado por defecto, sólo un filtro de destino activo (2–10), elegir otro apaga el anterior. ALL recupera el orden general existente. La fila Revisar base y materiales 5/5 queda oculta: tocar una tarjeta abre su selector y Listo lo oculta de nuevo. QA navegador: 5→6 deja sólo 6 activo; ALL; selector false→true→false; consola sin errores. Evidencia graduate-all-clean.png. No se ejecutó Graduate. Servidor de prueba 9242 conservado porque el usuario lo está usando en modo desarrollador.


### Pulido Inicio y perfil — 2026-09-30 (GXB2-ASSISTANT-064)
- [x] Iconos laterales compactos y Assistant separado en la parte superior según Reference/Game Assistant y captura nueva.
- [x] Puntos rosados calculados desde el estado: tareas locales pendientes, correo, misiones del Libro reclamables, mejoras asequibles de Servant, cofres/recursos de Excursión y acciones gratuitas del Assistant. Se apagan al desaparecer la condición; no son marcadores decorativos permanentes.
- [x] Perfil en ventana flotante sobre Inicio, pestañas Perfil/Ajustes, avatar, nombre, firma, nivel/EXP, chibi equipada y radar real juntos. Detalles VIP desplegables y Wallpaper accesible en Ajustes. Altura ajustada bajo avatar y encima de navegación.
- [T] QA en partida de desarrollador 9242: distribución visual, apertura de edición de nombre sin guardar, chibi cargada sin errores; señales pendientes/recogidas/costes comprobadas y 2 pruebas Assistant OK.
- [ ] Recogida de recursos de Servant original pendiente: el indicador actual avisa de mejoras disponibles. El resto de operaciones y fidelidad completa de Game Assistant requieren revisión por sistema; esta tanda conserva su ventana ga2 ya existente.
- Evidencia: validation/assistant-2026-09-30/home-compact.png y profile-floating.png.

- [x] GXB2-PROFILE-065: corona, texto VIP y números del cliente original; VIP y avatar centrados en el mismo eje, ID/gremio separados, edición y EXP alineadas. Beneficios VIP desplegables sin alterar distribución. QA visual y carga de sprites OK: validation/assistant-2026-09-30/profile-vip-aligned.png.

- [x] GXB2-PROFILE-066: dígitos VIP de altura uniforme, marco del avatar contenido; filas VIP/nombre y avatar/firma alineadas y ID separado. Verificación geométrica y visual en navegador: validation/assistant-2026-09-30/profile-rows-aligned.png.

- [x] GXB2-PROFILE-067: selector Avatares con cinco columnas y tiles redondeados sin rótulos ni números añadidos. Vista previa/Cambiar arriba y scroll independiente. QA Chicas409 opciones/0 captions; avatar-picker-clean.png.


### GXB2-GITHUB-068 — Copia privada reproducible (30/09/2026)

- [X] Repositorio privado Armenidez/gxb2-local con código, datos, runtime y todos los assets exportados necesarios.
- [X] Voces empaquetadas: 6.108/6.108, sin depender del dump original para jugar.
- [X] Partidas y recuperación personal excluidas; capturas de referencia y tests conservados localmente y fuera del árbol final.
- [X] README de instalación; inicio Windows x64 con motor compatible incluido y selección automática.
- [X] Copia Git limpia verificada en Mac; arranque/combate/atributos/voces verificados en Windows Server 2022 mediante Actions.

Alcance: distribución de la reconstrucción actual; no cierra funciones pendientes del juego ni prueba visualmente todas las pantallas de Windows. Evidencia y límites en VALIDACION.md y AI_WORKBOARD.md.

## 41. Recuperación integral de tablas — 2026-10-01

GXB2-TABLES-069 `[D]` para exportación de tablas/textos de las fuentes disponibles; integración global `[P]`. 904 tablas, incluidas 17 compuestas con prioridad/IDs originales, 202.878 filas en segmentos y 252 tablas inglesas/73.656 filas. 586 tablas sin referencias locales previas. [TABLAS_RECUPERADAS](TABLAS_RECUPERADAS.md) y `data/recovered/manifest.json` permiten localizar campos y consumidores; ocho dossiers cubren ArenaTeam, FairArena, GuildWar, GrowthDiary, NewbieCamp, ArenaAllServerNew, ArenaAllServerScore y PetTraining. No se declara jugable ninguno por esta recuperación. Calendario/rankings/rivales y reglas de servidor pendientes. 5 tests del lector y comparación independiente de seis tablas aprobados; hashes de las 904 fuentes/exportaciones verificados.

## 42. Growth Diary — 2026-10-01

GXB2-GROWTH-070 `[T][P][M]`: 40 capítulos / 160 misiones; 121 con seguimiento, 39 pendientes. Reglas cliente originales de desbloqueo/premios/estrellas, métricas de servidor sustituidas explícitamente por LOCAL-078. Botón en Inicio, páginas, Claim/Go y guardado; 343 tests OK, QA temporal del capítulo 1/recompensa/avance/reapertura sin errores de consola. [GROWTH_DIARY](GROWTH_DIARY.md). No certificar sistema global terminado.

## 43. Ampliación de contenido — 2026-10-01

GXB2-CONTENT-071 `[T][P][M]`: Growth Diary 154/160 (33 métricas adicionales; seis pendientes); Newbie Camp 3 etapas, 30 tareas visibles +3 premios ocultos, 28/30 con seguimiento. Contratos originales Growth/Rookie y API HTTP, rollback/lotes/reinicio/concurrencia; suite general 352 OK y 11 casos de ampliación OK (dos añadidos después). QA y HTTP sobre DB temporal. [NEWBIE_CAMP](NEWBIE_CAMP.md), [GROWTH_DIARY](GROWTH_DIARY.md), LOCAL-079. Pendientes Friend Boss, Servant Training/Ulticore, Practical Work, Chat, Elite League; no certificar sistemas globales completos.

## 44. Sistemas pendientes reconstruidos — 2026-10-01

CONTENT-072 `[T][P][M]`: Friend Boss actual doce dificultades, Training diez salas/diez muñecos/15cursos, Ulticore nueve Servants/900filas, Practical Work tres proyectos/ochojefes. Diary157/160. HTTP/protocolo Friend y Pet, informes nativos y premios únicos; 364tests OK. Fuentes/partidas habituales intactas. Límites sociales/calendario y Diary116/130/160 por discrepancia ocho vs10 etapas; Chat/EliteLeague continúan pendientes. [Alcance](SISTEMAS_PENDIENTES_RECONSTRUIDOS.md), LOCAL-080.
