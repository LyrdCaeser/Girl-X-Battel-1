# GXB 3 — Khôi phục Thức Tỉnh 4★/5★, Nâng cấp nhanh và SUPER GM Gift Nữ Thần

## Bảng gốc, không mock/fake

- Quét đủ 647 partner rows trong `data/partner.json`, bao gồm tất cả hình thái 4★/5★/6★/10★; khôi phục 38/38 phép 4★→5★ từ `data/graduate.json`.
- Bổ sung 39 công thức 5★→6★ đã bị bỏ sót khỏi `data/ascension.json` bằng **nguyên văn** `partner.material` của bản 6★ tương ứng. Không tự đặt vật phẩm, chi phí, nhân vật hoặc phép nâng sao.
- Các bản 5★ tái phát hành từ 4★ mà không có hình thái 6★ trong bảng gốc vẫn được báo không có công thức, không làm phép chuyển đổi giả.
- `COMPOSE_PARTNER` thật xử lý 4★→5★ và 5★→6★; `AWAKE_PARTNER` thật xử lý từ 6★ trở lên. Snapshot trả đúng recipe theo từng form; giao diện Thức Tỉnh hiện đủ nguyên liệu, cho phép xem và thao tác mà không chồng lấp nút X/CTA.

## Nâng cấp nhanh (mọi Nữ Thần)

- Ở chi tiết và roster có nút **Nâng cấp nhanh**.
- Một giao dịch server trừ đúng giá gốc theo từng bước EXP/level; nếu đủ nguyên liệu tự tiến các bậc grade bình thường, dừng khi hết tài nguyên hoặc đạt cấp giới hạn của **sao hiện có**. Không tiêu bản sao nâng sao, không cấp miễn phí, không thay tài khoản hoặc UID.
- Đọc cấu hình bảng theo `table_id` trong mỗi lần xử lý, không cần danh sách ID đóng cứng nên hỗ trợ tướng hiện tại và những tướng sẽ được bổ sung đúng bảng gốc.

## SUPER GM → Gift Nữ Thần

- Chỉ chủ sở hữu đã xác thực SUPER GM và **khóa hành động QTV riêng** mới được tạo mã, không dựa vào email/khóa do client tự khai. Giao diện có tìm kiếm, 7 bộ lọc hệ, phân trang 24, ảnh từ 446 hình thái gốc có fallback host, chọn sao từ chuỗi tiến hóa có thật.
- Cho phép chọn cấp hợp lệ với sao, số HP/ATK/DEF/SPD **cộng thêm** (có giới hạn), tối đa 10 nút Lõi Tinh Tú theo `star_origin` ở từ 15★, và đủ bốn trang bị gốc bậc đỏ 6★ (IDs 1999/2999/3999/4999). Các chỉ số cộng thêm tham gia `HeroAttr` LuaJIT gốc, không phải ảnh/nhãn UI giả.
- Mã SUPER GM: **30 ngày từ thời điểm tạo**, `max_uses=0` đại diện *không giới hạn tổng lượt*, nhưng **một UID chỉ nhập một lần cho mỗi mã**. Giữ nguyên giới hạn của giftcode vật phẩm thông thường.
- Khi nhập mã, người chơi được gửi thư có thông tin Nữ Thần. Khi nhận thư, máy chủ tạo một Nữ Thần mới trong hồ sơ đúng UID và world cùng giao dịch xác nhận thư và lưu player Neon; chặn nhận lại và rollback khi lỗi.

## Chính sách dữ liệu và phát hành

Không reset Neon; không gửi quà cho người chơi thật trong kiểm thử; không dùng dữ liệu demo hoặc NPC; không thay bản APK/EXE/IPA/MobileConfig v2.5.2 chỉ vì có mã nguồn mới. Test nguồn bằng SQLite tạm và cửa sổ Chromium trong QA. Mỗi commit chỉ stage file đúng phạm vi, CI GitHub PASS và có backup Neon PG18/source trước Production fast-forward; chờ `/readyz` true sau restart.
