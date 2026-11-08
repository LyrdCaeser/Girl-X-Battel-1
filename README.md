Cảnh báo nghiêm trọng (KHÔNG ĐƯỢC TÁI CHẾ, VIỆC TÁI CHẾ & FORK SẼ DẪN ĐẾN VIỆC BỊ CHẶT TAY):

© 2026 LyrdCaeser. Bảo lưu mọi quyền.

Kho lưu trữ này và mã nguồn của nó được công khai chỉ nhằm mục đích trình bày portfolio và xem xét mã.

VIỆC SỬ DỤNG TRÁI PHÉP BỊ NGHIÊM CẤM. Bạn KHÔNG được phép sao chép, phân phối, sửa đổi hoặc sử dụng mã nguồn này cho bất kỳ dự án cá nhân hoặc thương mại nào mà không có sự cho phép bằng văn bản rõ ràng. 

> **02/10/2026 — cập nhật 088:** bổ sung bảng và hệ thống cục bộ, điều chỉnh Campaign và Tests, hướng dẫn theo ngữ cảnh, biểu tượng và hiệu ứng phát sáng, văn bản giao diện tiếng Anh, trạng thái chiến đấu, đội hình căn giữa và nhãn VICTORY/DEFEAT. [Ghi chú phân phối](DISTRIBUCION_2026-10-02.md).

> **01/10/2026 — CONTENT-072:** Friend Boss, Servant Training, Ulticore và Practical Work hiện có tại Trang chủ → Training & Bosses (Huấn luyện & Trùm). Growth Diary **157/160**. **364 bài kiểm thử đạt**; các trận chiến dùng bộ máy gốc đã được xác minh trên cơ sở dữ liệu tạm. [Phạm vi và giới hạn](SISTEMAS_PENDIENTES_RECONSTRUIDOS.md). Khởi động lại máy chủ để nạp mã.

> **01/10/2026 — GXB2-CONTENT-071:** Growth Diary được cập nhật lên **154/160** nhiệm vụ; Newbie Camp có **ba giai đoạn, 30 nhiệm vụ và ba phần thưởng**, trong đó **28/30** nhiệm vụ đã được tích hợp. API và thông điệp gốc, phần thưởng được lưu bền vững và kiểm thử trên bản lưu tạm. Khởi động lại máy chủ; các nút nằm ở Trang chủ. [Newbie Camp](NEWBIE_CAMP.md) · [Growth Diary đã cập nhật](GROWTH_DIARY.md).

# Girls X Battle 2 — phiên bản chạy cục bộ

Dự án lưu giữ và tái dựng game để chơi trên máy chủ cục bộ, bao gồm mã nguồn, dữ liệu, tranh minh họa, hoạt ảnh, biểu tượng và giọng nói. Một số hệ thống đã hoàn chỉnh, một số mới hoàn thiện một phần; xem [ESTADO_PROYECTO.md](ESTADO_PROYECTO.md) và [GXB2_MASTER_CHECKLIST.md](GXB2_MASTER_CHECKLIST.md) để biết phạm vi thực tế.

## Khởi chạy trên macOS

Cần Python 3.10 trở lên. Bộ máy chiến đấu có kèm LuaJIT cho máy Mac dùng Intel. Trên Apple Silicon, tệp thực thi này cần Rosetta; bạn cũng có thể dùng bản LuaJIT được biên dịch cho Apple Silicon như hướng dẫn bên dưới.

```sh
git clone https://github.com/Armenidez/gxb2-local.git
cd gxb2-local
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 server.py --open
```

Mở `http://localhost:9080/`. Để dừng máy chủ, nhấn Ctrl+C. Kho lưu trữ này ở chế độ riêng tư: bạn cần có quyền truy cập bằng tài khoản GitHub của mình để tải xuống. Gói tải xuống có dung lượng lớn vì bao gồm tài nguyên hình ảnh và âm thanh.

Nếu các cổng đó đang được sử dụng:

```sh
python3 server.py --open --http-port 9242 --tcp-port 9243
```

## Khởi chạy trên Windows 10/11 (64 bit)

1. Cài Python 3.10 trở lên từ https://www.python.org/downloads/windows/ và bật tùy chọn thêm Python vào PATH.
2. Tải kho lưu trữ riêng tư này bằng **Code → Download ZIP** (hoặc dùng Git), sau đó giải nén toàn bộ thư mục.
3. Nhấp đúp vào **Iniciar-Windows.cmd**. Lần đầu chạy, chương trình tạo môi trường Python và cài thư viện phụ thuộc; sau đó game sẽ mở trong trình duyệt.

Bộ máy LuaJIT cho Windows x64 đã được bao gồm và tự động chọn. Bạn không cần cài LuaJIT hoặc ffmpeg. Lần đầu cài thư viện phụ thuộc Python cần có kết nối Internet; tài nguyên game đã được đóng gói sẵn.

Nếu cần đổi cổng, mở cửa sổ dòng lệnh trong thư mục và chạy:

```bat
Iniciar-Windows.cmd --http-port 9242 --tcp-port 9243
```

Cửa sổ dòng lệnh phải mở trong khi chơi. Nhấn Ctrl+C để dừng máy chủ. Windows ARM và các phiên bản trước Windows 10 chưa được kiểm chứng.

## LuaJIT trên các máy khác

Bộ máy chiến đấu cần LuaJIT 2.x. Để dùng bản LuaJIT tương thích do bạn tự cài (ví dụ: bản được biên dịch trực tiếp cho macOS hoặc Linux), hãy cấu hình đường dẫn tới tệp thực thi trước khi khởi động:

```sh
export GXB2_LUAJIT="$(command -v luajit)"
python3 server.py --open
```

Các tệp thực thi riêng cho macOS x64 và Windows x64 đã được đóng gói kèm. Trên Linux, hãy cài LuaJIT; máy chủ sẽ tìm trong PATH hoặc nhận đường dẫn qua `GXB2_LUAJIT`. Các thông báo giấy phép của thư viện trong `runtime/` và `web/vendor/` được giữ nguyên.

## Bản lưu và chế độ nhà phát triển

Lần khởi chạy đầu tiên tạo một bản lưu mới tại `state/profile.sqlite3` và một bản lưu nhà phát triển riêng tại `state/profile.developer.sqlite3`. Cơ sở dữ liệu và các bản xuất dữ liệu cá nhân được loại khỏi Git. Có thể chuyển chế độ chơi trong giao diện để thử nghiệm bằng bản lưu nhà phát triển.

Để mở một bản lưu khác:

```sh
python3 server.py --db state/mi-partida.sqlite3 --open
```

Để tạo bản sao nhất quán, kể cả khi máy chủ đang chạy:

```sh
python3 tools/save_archive.py backup state/profile.sqlite3 backups/mi-partida.sqlite3
```

Bản tái dựng không thể tự khôi phục tài khoản từng được lưu trên các máy chủ cũ.

## Các tệp được bao gồm

- `server.py`, `gxb2/`: máy chủ và luật chơi cục bộ.
- `web/`: giao diện, thư viện trình duyệt và toàn bộ tài nguyên đã xuất.
- `data/`: các bảng và dữ liệu cần thiết để chơi.
- `runtime/`: bộ máy Lua và LuaJIT cho macOS x64 và Windows x64.
- `tools/` và tài liệu trạng thái: công cụ cùng lịch sử dự án.

Các bài kiểm thử phát triển và ảnh chụp màn hình tham chiếu được lưu trên máy Mac làm việc và bị loại khỏi phiên bản cuối của kho lưu trữ.

Không cần các thư mục gốc trong `Downloads` để khởi chạy game. Các công cụ trích xuất trong `tools/` dùng để tái tạo tài nguyên từ nguồn gốc; một số công cụ cần các nguồn đó. Bạn không cần chạy chúng sau khi tải kho lưu trữ này. Giọng nói đã được chuyển đổi sang MP3. Nếu muốn tạo lại, bạn cần ffmpeg và thư mục âm thanh gốc.

## Kiểm tra

```sh
python3 tools/bundle_voices.py --check
```

Các báo cáo lịch sử không xác nhận game đã hoàn toàn trung thực với bản gốc; chúng có thể dẫn tới kiểm thử hoặc ảnh chụp trong `tests/`, `docs/references/` và `validation/`. Những nội dung này được lưu cục bộ và loại khỏi phiên bản cuối của kho lưu trữ, cùng với các bản lưu dùng để kiểm thử. Xem [LEEME.md](LEEME.md) để biết lịch sử và kiến trúc.


Kiểm tra phân phối: bản sao sạch trên macOS và [khởi chạy/chiến đấu trên Windows x64](https://github.com/Armenidez/gxb2-local/actions/runs/36729034925) đều đạt. Kiểm tra Windows chạy trên Windows Server 2022; đây không phải là đợt rà soát trực quan đầy đủ mọi màn hình trên Windows 10/11.

## Khôi phục đầy đủ các bảng — 01/10/2026

[Các bảng đã khôi phục](TABLAS_RECUPERADAS.md): đủ 904/904 bảng gốc, 202.878 hàng dữ liệu trong các phân đoạn, 252 bảng tiếng Anh và tám hồ sơ hệ thống. Dữ liệu và manifest nằm trong `data/recovered/`; công cụ trích xuất có thể tái chạy là `tools/recover_client_tables.py`. Việc khôi phục tài liệu từ các nguồn này đã hoàn tất; tích hợp để chơi vẫn còn một phần. Không thay đổi luật chơi hay bản lưu.

## Growth Diary — 01/10/2026

Nút mới nằm ở Trang chủ sau giai đoạn 5: 40 chương / 160 nhiệm vụ, theo dõi cục bộ 121 nhiệm vụ, nhận thưởng một lần và lưu tiến trình. [Phạm vi và 39 mục tiêu còn lại](GROWTH_DIARY.md). Khởi động lại máy chủ để nạp thay đổi.
