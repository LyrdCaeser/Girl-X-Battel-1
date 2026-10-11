# Hướng dẫn GxB2 Local Việt Hóa

Nhánh phát triển: `snez-vietnamese`.

## Chạy trên Windows

1. Cài Python 3.10 trở lên và bật tùy chọn thêm Python vào PATH.
2. Clone repo có Git LFS:
   ```powershell
   git lfs install
   git clone -b snez-vietnamese https://github.com/LyrdCaeser/Girl-X-Battel-1.git
   cd Girl-X-Battel-1
   git lfs pull
   ```
3. Chạy:
   ```powershell
   .\Iniciar-Windows.cmd
   ```
4. Trình duyệt mở tại `http://localhost:9080/`.

## Chế độ QTV

Mỗi lần server khởi động, Terminal sẽ in:

```text
Khóa QTV phiên này: <khóa>
```

Trong game bấm **QTV**, nhập khóa đó rồi bật **Chế độ Quản Trị**.

- QTV dùng file save riêng `state/profile.developer.sqlite3`.
- Save thường `state/profile.sqlite3` không bị sửa bởi các thao tác QTV.
- Khóa QTV chỉ giữ trong `sessionStorage` của tab trình duyệt.
- Có thể đặt khóa cố định trước khi chạy:
  ```powershell
  $env:GXB2_ADMIN_KEY="khoa-cua-ban"
  .\Iniciar-Windows.cmd
  ```
  hoặc:
  ```powershell
  .\.venv\Scripts\python.exe server.py --open --admin-key "khoa-cua-ban"
  ```

## Cấu trúc chính

- `server.py`: HTTP/TCP local, kiểm tra khóa QTV, API.
- `gxb2/engine.py`: save SQLite, progression, tài nguyên, summon, battle orchestration và save QTV.
- `gxb2/shops.py`: cửa hàng.
- `gxb2/events.py`: sự kiện.
- `gxb2/arena.py`: đấu trường Local.
- `web/index.html` + `web/*.js`: giao diện.
- `web/i18n-vi.js`: lớp Việt hóa UI và text động.

## Lưu ý

Đây là project phục dựng Local. Một số hệ thống là bản tái dựng dựa trên dữ liệu client, không phải backend chính thức của game.
