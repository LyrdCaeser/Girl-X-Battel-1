# Hướng dẫn GxB2 Local Việt Hóa

Nhánh phát triển: `snez-vietnamese`.

## Chạy trên Windows

1. Cài Python 3.10 trở lên và bật tùy chọn thêm Python vào PATH.
2. Clone repo bằng Git LFS:
   ```powershell
   git lfs install
   git clone -b snez-vietnamese https://github.com/LyrdCaeser/Girl-X-Battel-1.git
   cd Girl-X-Battel-1
   git lfs pull
   ```
3. Chạy `.\Iniciar-Windows.cmd`.
4. Game mở tại `http://localhost:9080/`.

## Bảng Quản Trị QTV

Nút **QTV** trên Trang Chủ mở màn hình đăng nhập. Khóa QTV được chủ dự án đặt cố định trong backend `server.py`.

Sau khi xác thực, game chuyển sang save QTV riêng:

- Save thường: `state/profile.sqlite3`
- Save QTV: `state/profile.developer.sqlite3`
- Khóa của phiên đăng nhập chỉ được giữ trong `sessionStorage` của tab trình duyệt.
- **Thoát QTV** sẽ quay về save thường.

Bảng QTV có hai nhóm chính:

- **Cấu hình Local:** tài nguyên khởi đầu, Starter Girls, trọng số Triệu Hồi theo sao, giá Shop, phần thưởng và chi phí tiến triển.
- **Công cụ QTV:** thêm Nữ Sinh, thêm toàn bộ collection, 15★, áp cấp, chỉnh tầng Tests và mở Campaign.

## Cấu hình Local

Mặc định nằm tại:

`data/local_config.json`

Khi thay đổi trong Bảng QTV, override được lưu tại:

`state/local_config.json`

Do đó không cần sửa `engine.py` để cân bằng game.

Các nhóm cấu hình:

- `starting_resources`: tài nguyên của save mới.
- `starter_girls`: 1–6 ID Nữ Sinh của save mới.
- `summon_rate.star_multiplier`: hệ số trọng số theo số sao; `1.0` là gốc, `2.0` là gấp đôi, `0` loại nhóm đó khỏi pool.
- `shop.price_multiplier`: hệ số giá Shop.
- `rewards.multiplier`: áp dụng cho Campaign clear/idle, Tests và Daily Quiz.
- `progression.cost_multiplier`: áp dụng cho chi phí tăng cấp, tăng Bậc và phần tài nguyên của Thức Tỉnh.

Tài nguyên khởi đầu và Starter Girls chỉ áp dụng khi tạo **save mới**. Các multiplier còn lại có hiệu lực ngay.

## Kiến trúc chính

- `server.py`: HTTP/TCP local, xác thực QTV và API cấu hình.
- `gxb2/local_config.py`: đọc/ghi/kiểm tra cấu hình Local.
- `gxb2/engine.py`: SQLite save, progression, summon và battle orchestration.
- `gxb2/shops.py`: Shop.
- `gxb2/campaign.py`: Campaign idle/reward.
- `web/admin.js` + `web/admin.css`: Bảng Quản Trị QTV.
- `web/i18n-vi.js`: Việt hóa UI và thông báo động.

Đây là project phục dựng Local. Một số hệ thống được tái dựng từ dữ liệu client và không phải backend chính thức của game.
