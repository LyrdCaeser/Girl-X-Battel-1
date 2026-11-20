# GXB 3 — Kiểm chứng lỗi hệ thống từ 8 ảnh Android (14/11/2026)

## Căn nguyên và thay đổi có bằng chứng

1. **Tất cả Nữ Thần ≥9★ hiển thị thành 9★ trong xếp đội:** `CampaignFlow.heroIcon` dùng `Math.min(4,star-5)`, luôn dừng ở 4 sao đỏ. Đổi sang `GirlUI.stars(star,'card')` — chung bộ biểu tượng nguyên gốc với Hồ sơ, hỗ trợ 4★–25★ và số sao thực (25★ hiển thị emblemm 15). Không sửa dữ liệu sao hay UID của người chơi.
2. **Thanh HP hai phe dồn nửa trái:** `mobile-native.css` đặt `html.gxb-mobile #app-frame .units{max-width:46%!important}`, ép cả các lớp HP tuyệt đối của 12 vị trí Spine vào nửa sân. Chỉ override `#app-frame .battlefield>.units` thành `width:100%!important;max-width:none!important` để giữ tọa độ chiến trường 1080 × 1920. Thử phát lại 57 frame LuaJIT thật trên Neon QA: trước khi sửa, x HP trái/phải ~29/99 (đều ở trái); sau sửa, x 94/245 và 47/292, đúng hai phe. 6/6 nhân vật có đúng một HP, 4/4 tử trận không còn HP nổi.
3. **Lỗi `Value out of range: 3192954487`:** báo cáo LuaJIT tổng sát thương > giới hạn signed int32 của protobuf `battle_data.total_harm`. Chỉ giới hạn dữ liệu **wire client tương thích int32** tại 2.147.483.647; giữ nguyên giá trị sát thương gốc int64 trong LuaJIT report JSON để không mất thống kê. Test giá trị chính xác trong ảnh, giá trị bình thường và giá trị âm/lỗi.
4. **BXH Junior Varsity/3v3/Liên server tự xếp theo lực chiến:** backend dùng `LEFT JOIN` toàn bộ người chơi đã đăng ký với `COALESCE(r.rating,1000)` rồi xếp hạng ngay cả khi chưa có trận. Đổi sang chỉ `JOIN pvp_ratings r` của **mùa/mode đang xem với `r.matches>0`**, kết quả trận được backend xác nhận. Người chơi chưa đấu sẽ thấy `Chưa đấu`, không phải vị trí #1 giả. Modes không nhập nhằng.
5. **Avatar người chơi trong Arena:** thay chân dung Nữ Thần đầu tiên bằng `state.profile.avatar`, hỗ trợ ảnh custom WebP từ Neon cùng avatar gốc và fallback. Chỉ public key, không lộ dữ liệu tài khoản riêng.
6. **Thức Tỉnh 4–9★:** màn tab hiển thị nguyên liệu thực `next_awake.material`/công thức nguồn trong chính tab, trạng thái đủ/thừa và chi phí thực, còn nút mở `COMPOSE_PARTNER`/`AWAKE_PARTNER` server. Kiểm tra 38 công thức gốc 4→5 và 115 công thức gốc 5→6. Không sinh công thức cho Nữ Thần không có nâng sao ở dữ liệu nguồn.
7. **3v3 bố cục tự chế:** thay popup chứa 3 badge trống/gợi ý tự xếp bằng 3 hàng native `arena_3v3_t1..t3`, mỗi hàng 6 slot, chọn nhân vật thật từ kho người chơi, không tự điền đội, không tạo đối thủ hay kết quả NPC. Sau khi lưu, dùng các API PvP online thật đang có. Điều này cải thiện fidelity với `Arena3v3BattleFormationWindow` gốc; **không phải chứng minh toàn bộ cơ chế client gốc đã được phục hồi pixel-perfect**.

## QA và giới hạn

- 7 bài `tests/test_systemic_visual_data_regressions_20261114.py`: test 647 bảng nhân vật, 153 native recipes, hình sao, phép truyền protobuf, rank thực, avatar và full-width CSS. Đã chạy PASS.
- 3 bài HTTP/tương tác PvP có thật bằng tài khoản QA, test JS original Arena/Guild, 3 đội 18 slot, replay LuaJIT/HP; các screenshot Chromium nằm trên VPS QA (không đưa ảnh tài khoản người chơi Production lên GitHub).
- QA trên **nhánh Neon độc lập** `br-broad-wind-b3i1ogbq` fork từ Production. Tuyệt đối không viết hồ sơ người chơi Production; server QA chỉ bind 127.0.0.1:19090.
- Đã tái hiện và sửa tọa độ HP với Chromium mobile. **Vẫn cần kiểm thử bản APK, iOS, Windows thực tế trên thiết bị, so sánh từng prefab/skin/skill của toàn bộ client gốc, cũng như chứng minh 3v3 online hoàn toàn khớp cơ chế gốc** trước khi có thể tuyên bố phục hồi hoàn chỉnh mọi cơ chế. Không tuyên bố đã kiểm chứng điều chưa kiểm chứng.
- Không tăng VersionName/VersionCode, không xuất bản GitHub Release mới trong nhánh sửa lỗi. Chỉ làm release sau khi quality gate đạt và xác nhận Production an toàn.
