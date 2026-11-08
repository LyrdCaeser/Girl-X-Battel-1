# Audit tài nguyên offline: `origin/main` → `feature/offline-mode`

- Thời điểm chạy: 2026-11-08 (UTC+07:00)
- Commit `origin/main`: `7a49e5f873a41a9fa7fbe6a885cad775f95de83f`
- Commit `feature/offline-mode`: `01f0b5841db0c526a20a8d3f86fe9d0ed61d2f5d`
- Tổng file tài nguyên: main **36,354**, offline **36,363**
- Thiếu trên offline: **0**
- Khác blob ID giữa hai nhánh: **20** (khác biệt đã có giữa nhánh; audit không ghi đè/cherry-pick)
- Offline-only: **9**

## Âm thanh và Git LFS

- Audio được theo dõi trong Git LFS trên offline: **6,701**
- Payload đã hydrate và xác minh không phải pointer: **6,701/6,701**
- Còn pointer / file thiếu: **0 / 0**
- Kích thước audio đã hydrate trong working tree: **531,908,765 byte** (~531.9 MB)
- Audio trong `origin/main`: **6,701**; thiếu trên offline **0**; khác blob **0**

| Nhóm | File main | File offline | Thiếu | Khác blob | Audio LFS hydrate |
|---|---:|---:|---:|---:|---:|
| `data` | 1252 | 1258 | 0 | 14 | — |
| `runtime` | 3599 | 3599 | 0 | 1 | — |
| `web/assets/altar` | 27 | 27 | 0 | 0 | — |
| `web/assets/arena` | 43 | 43 | 0 | 0 | — |
| `web/assets/assistant` | 56 | 56 | 0 | 0 | — |
| `web/assets/avatars.json` | 1 | 1 | 0 | 0 | — |
| `web/assets/avatars.png` | 1 | 1 | 0 | 0 | — |
| `web/assets/battle-fx` | 2047 | 2047 | 0 | 0 | — |
| `web/assets/battle-loading` | 24 | 24 | 0 | 0 | — |
| `web/assets/battle-maps` | 68 | 68 | 0 | 0 | — |
| `web/assets/battle-maps.json` | 1 | 1 | 0 | 0 | — |
| `web/assets/bg` | 2 | 2 | 0 | 0 | — |
| `web/assets/blind-box` | 29 | 29 | 0 | 0 | — |
| `web/assets/campaign` | 178 | 178 | 0 | 0 | — |
| `web/assets/campus` | 16 | 16 | 0 | 0 | — |
| `web/assets/capsule` | 12 | 12 | 0 | 0 | — |
| `web/assets/cards` | 408 | 408 | 0 | 0 | — |
| `web/assets/cards.json` | 1 | 1 | 0 | 0 | — |
| `web/assets/characters` | 120 | 120 | 0 | 0 | — |
| `web/assets/characters.json` | 1 | 1 | 0 | 0 | — |
| `web/assets/chibis` | 3930 | 3930 | 0 | 1 | — |
| `web/assets/chimes` | 46 | 46 | 0 | 0 | — |
| `web/assets/currency` | 8 | 8 | 0 | 0 | — |
| `web/assets/daily-quiz` | 23 | 23 | 0 | 0 | — |
| `web/assets/dates` | 185 | 185 | 0 | 0 | — |
| `web/assets/detail` | 141 | 141 | 0 | 0 | — |
| `web/assets/dress` | 2036 | 2036 | 0 | 0 | — |
| `web/assets/dress-show` | 47 | 47 | 0 | 0 | — |
| `web/assets/echoes` | 160 | 160 | 0 | 0 | — |
| `web/assets/enroll` | 43 | 43 | 0 | 0 | — |
| `web/assets/equipment` | 142 | 142 | 0 | 0 | — |
| `web/assets/ev-sand` | 57 | 57 | 0 | 0 | — |
| `web/assets/events` | 397 | 397 | 0 | 0 | — |
| `web/assets/excursion` | 80 | 80 | 0 | 0 | — |
| `web/assets/factions` | 7 | 7 | 0 | 0 | — |
| `web/assets/fantasy-book` | 66 | 66 | 0 | 1 | — |
| `web/assets/firework-project` | 14 | 14 | 0 | 0 | — |
| `web/assets/galaxy` | 152 | 152 | 0 | 0 | — |
| `web/assets/girl-details.json` | 1 | 1 | 0 | 1 | — |
| `web/assets/girl-ui` | 30 | 30 | 0 | 0 | — |
| `web/assets/girls-catalog.json` | 1 | 1 | 0 | 0 | — |
| `web/assets/group-buff` | 53 | 53 | 0 | 0 | — |
| `web/assets/growth-diary` | 8 | 8 | 0 | 0 | — |
| `web/assets/guild` | 90 | 90 | 0 | 0 | — |
| `web/assets/hero-41001.png` | 1 | 1 | 0 | 0 | — |
| `web/assets/hero-42001.png` | 1 | 1 | 0 | 0 | — |
| `web/assets/hero-43001.png` | 1 | 1 | 0 | 0 | — |
| `web/assets/hero-challenge` | 95 | 95 | 0 | 0 | — |
| `web/assets/home-bg.png` | 1 | 1 | 0 | 0 | — |
| `web/assets/home-icons-alpha.png` | 1 | 1 | 0 | 0 | — |
| `web/assets/home-icons.json` | 1 | 1 | 0 | 0 | — |
| `web/assets/home-icons.png` | 1 | 1 | 0 | 0 | — |
| `web/assets/home-systems` | 502 | 502 | 0 | 0 | — |
| `web/assets/house-exam` | 58 | 58 | 0 | 0 | — |
| `web/assets/img-guides` | 66 | 66 | 0 | 0 | — |
| `web/assets/internship` | 79 | 79 | 0 | 0 | — |
| `web/assets/item-icons` | 2038 | 2038 | 0 | 0 | — |
| `web/assets/item-icons.json` | 1 | 1 | 0 | 0 | — |
| `web/assets/items-catalog.json` | 1 | 1 | 0 | 0 | — |
| `web/assets/jackpot` | 35 | 35 | 0 | 0 | — |
| `web/assets/league` | 15 | 15 | 0 | 0 | — |
| `web/assets/life` | 16 | 16 | 0 | 0 | — |
| `web/assets/lihui` | 2183 | 2183 | 0 | 0 | — |
| `web/assets/login` | 0 | 1 | 0 | 0 | — |
| `web/assets/lost-space` | 60 | 60 | 0 | 0 | — |
| `web/assets/magic-card` | 33 | 33 | 0 | 0 | — |
| `web/assets/menu` | 713 | 713 | 0 | 2 | — |
| `web/assets/menus` | 71 | 71 | 0 | 0 | — |
| `web/assets/midas` | 7 | 7 | 0 | 0 | — |
| `web/assets/missions` | 18 | 18 | 0 | 0 | — |
| `web/assets/nav` | 16 | 16 | 0 | 0 | — |
| `web/assets/nav-reference` | 6 | 6 | 0 | 0 | — |
| `web/assets/newbie-camp` | 4 | 4 | 0 | 0 | — |
| `web/assets/old-campus` | 61 | 61 | 0 | 0 | — |
| `web/assets/original-ui` | 2977 | 2977 | 0 | 0 | — |
| `web/assets/patrol` | 47 | 47 | 0 | 0 | — |
| `web/assets/picture-layouts.json` | 1 | 1 | 0 | 0 | — |
| `web/assets/pictures` | 537 | 537 | 0 | 0 | — |
| `web/assets/pirate` | 25 | 25 | 0 | 0 | — |
| `web/assets/profile` | 943 | 943 | 0 | 0 | — |
| `web/assets/pumpkin` | 18 | 18 | 0 | 0 | — |
| `web/assets/puzzle-events` | 270 | 270 | 0 | 0 | — |
| `web/assets/remaining-systems` | 9 | 9 | 0 | 0 | — |
| `web/assets/sanctuary` | 94 | 94 | 0 | 0 | — |
| `web/assets/scenes` | 7 | 7 | 0 | 0 | — |
| `web/assets/servant` | 115 | 115 | 0 | 0 | — |
| `web/assets/shops` | 213 | 213 | 0 | 0 | — |
| `web/assets/shrine` | 152 | 152 | 0 | 0 | — |
| `web/assets/skills` | 465 | 465 | 0 | 0 | — |
| `web/assets/skins` | 669 | 669 | 0 | 0 | — |
| `web/assets/slots` | 161 | 161 | 0 | 0 | — |
| `web/assets/souls` | 139 | 139 | 0 | 0 | — |
| `web/assets/sounds` | 381 | 381 | 0 | 0 | 379 |
| `web/assets/spine` | 538 | 538 | 0 | 0 | — |
| `web/assets/sprite` | 84 | 84 | 0 | 0 | — |
| `web/assets/stage-check.png` | 1 | 1 | 0 | 0 | — |
| `web/assets/stage-lock.png` | 1 | 1 | 0 | 0 | — |
| `web/assets/station` | 63 | 65 | 0 | 0 | — |
| `web/assets/stellar` | 14 | 14 | 0 | 0 | — |
| `web/assets/story` | 526 | 526 | 0 | 0 | 214 |
| `web/assets/story-items` | 10 | 10 | 0 | 0 | — |
| `web/assets/summon` | 1 | 1 | 0 | 0 | — |
| `web/assets/summon-result` | 15 | 15 | 0 | 0 | — |
| `web/assets/tower` | 15 | 15 | 0 | 0 | — |
| `web/assets/two-love` | 21 | 21 | 0 | 0 | — |
| `web/assets/ui` | 21 | 21 | 0 | 0 | — |
| `web/assets/voices` | 6108 | 6108 | 0 | 0 | 6108 |
| `web/assets/wish` | 25 | 25 | 0 | 0 | — |

## Kết luận

Không có file từ `main` bị thiếu trên `feature/offline-mode`; các audio có cùng đường dẫn và cùng blob pointer LFS giữa hai nhánh. Trong checkout hiện tại, toàn bộ 6.701 payload audio đã được tải thật vào working tree, không còn LFS pointer. `voices` có 6.108 file hydrate; `sounds` có 379; `story` có 214 file audio LFS (nhóm thư mục `story` có 526 tài nguyên tổng cộng).

Các thay đổi blob được báo cáo là khác biệt đã có sẵn giữa hai nhánh trong những đường dẫn chung; không tự ý thay bằng bản `main`. Nhánh offline giữ 9 file offline-only.

## File offline-only

- `data/brand.json`
- `data/guild_online_config.json`
- `data/local_config.json`
- `data/pvp_season_rewards.json`
- `data/topup_packages.json`
- `data/world_live_defaults.json`
- `web/assets/login/gxb3-wedding-promo.webp`
- `web/assets/station/station-vi-candidate.json`
- `web/assets/station/station-vi.json`

## Các đường dẫn chung khác blob

- `data/activity_draw.json`
- `data/activity_kit.json`
- `data/blind_box.json`
- `data/events.json`
- `data/growth_diary.json`
- `data/guild.json`
- `data/jackpot.json`
- `data/lost_space.json`
- `data/magic_card.json`
- `data/newbie_camp.json`
- `data/partner_plot.json`
- `data/pirate.json`
- `data/pumpkin.json`
- `data/story.json`
- `runtime/battle_host.lua`
- `web/assets/chibis/catalog.json`
- `web/assets/fantasy-book/book.json`
- `web/assets/girl-details.json`
- `web/assets/menu/help.json`
- `web/assets/menu/manga/manga.json`

## Chạy lại audit

Trong clone có cả hai ref Git:

```bash
python3 tools/audit_offline_resources.py
python3 tools/audit_offline_resources.py --json > docs/reports/OFFLINE_RESOURCE_AUDIT.json
```

Để tải payload LFS audio về working tree:

```bash
git lfs install --local
git lfs pull --include='web/assets/voices/**,web/assets/sounds/**,web/assets/story/**' --exclude=''
```

Audit so sánh Git tree/blob; việc xác minh hydration được thực hiện riêng bằng cách kiểm tra header payload của từng file audio trong working tree.
