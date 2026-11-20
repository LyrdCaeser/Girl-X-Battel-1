# Lyr Sonia — đặc tả kỹ thuật có kiểm thử (chưa phát hành)

**Trạng thái:** `QA_ONLY_NOT_IN_GAME`. Tệp này là hợp đồng phát triển, không tự đăng ký nhân vật vào engine, không thêm hệ mới vào lựa chọn người chơi và không phát hành nội dung trên Production.

## Các mục đã được duyệt
- **Hệ Hỗn Độn:** nhóm `8` mới; các nhóm `1–7` và dữ liệu Nữ Thần hiện hành giữ nguyên.
- **Nghề Pháp Sư:** `job=3`.
- **Bốn ô kỹ năng:** `act_skill_id` (một chủ động) và `pas_skill1_id`, `pas_skill2_id`, `pas_skill3_id` (ba bị động), theo cấu trúc bảng `data/partner.json`; chưa tự tạo tác dụng hoặc số liệu cho ba bị động.
- **Kỹ năng chủ động:** tên làm việc `Tinh Liên Hỏa Ấn`; chỉ dùng hiệu ứng hình ảnh gốc Nymphaea, Izanami, Monica; không sao chép công thức sát thương.
- **Spine chibi:** 6 hướng nhìn có hình vẽ thực, dùng `3.6.37`; trong chiến đấu chỉ có `idle`, `attack`, `skill`, `hurt`, `dead`.
- **Không chạy/di chuyển trong chiến đấu.** Giữ vị trí đội hình; không áp dụng cách lao tới mục tiêu trong bản QA thử cũ.
- **Dead:** khi HP bằng 0, ngã rồi **biến mất khỏi chiến trường** sau hoạt ảnh, không nằm lại trên sân.

## Cổng cần đạt trước khi nhập engine
1. Hoàn thiện tên, tác dụng, cấp độ và chỉ số của **ba bị động**, quy tắc độc lập với kỹ năng gốc.
2. Cấp ID nhân vật và bốn ID kỹ năng độc lập; tránh trùng toàn bộ bảng gốc.
3. Đăng ký và kiểm tra `group=8` xuyên suốt: engine combat, cộng hưởng đội hình, điều kiện, lọc hệ, UI, icon và các thao tác có giới hạn hệ.
4. Hoàn thành Spine 6 hướng *trong chiến đấu*; vẽ khớp đầy đủ và kiểm tra đặc biệt `dead → remove`.
5. Kiểm tra WebGL PC + **thiết bị Android thật**, với hiệu ứng, tải texture, FPS và dọn tài nguyên.
6. Chỉ sau khi tất cả đạt mới quyết định triển khai; **không thay đổi Neon người chơi**.

## Tệp liên quan
- `character-v1.json`: đặc tả máy đọc được.
- `tests/test_lyr_sonia_character_contract.py`: test dựa trên bảng `data/partner.json` và FX gốc.
