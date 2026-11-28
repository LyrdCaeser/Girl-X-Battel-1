# Lyr Sonia · QA Spine sáu hướng (chưa triển khai game)

Bộ mã và trang thử này **không được game Production nạp**. Không dùng GIF và không thêm hệ 8/nhân vật vào dữ liệu người chơi.

- Sân thử dùng Pixi + Spine 3.6.37, chọn đúng 6 hướng từ bộ ZIP **Lyr Sonia 6 hướng v1.4 đã duyệt** ngay trên trình duyệt của người dùng. ZIP không được tải lên máy chủ.
- Tại góc chính diện: giữ 5 clip idle / attack / skill / hurt / dead của bộ QA chưa hoàn thiện.
- Tại 5 góc còn lại: chỉ kiểm tra ảnh góc vẽ **thật** trong Spine; **khóa** Attack/Skill vì chưa rig bộ phận ở góc đó. Không lật ngang hoặc tự tạo chuyển động giả.
- Nhân vật không di chuyển vị trí đội hình. Dead ngã rồi biến mất sau 1,25 giây ở bản QA hiện tại.
- 4 ô kỹ năng: 1 chủ động có tham chiếu VFX Nymphaea/Izanami/Monica, 3 bị động chờ duyệt tác dụng. Không tự đặt chỉ số.
- Sử dụng bản QA trong môi trường riêng có các asset assets/sonia/model.json, model.atlas, texture và /vendor/pixi.min.js, /vendor/pixi-spine.js. index.html không phải file offline tự chạy.

## Kiểm thử
Chạy node docs/lyr-sonia/qa/test_direction_rules.cjs từ repo để kiểm tra luật hướng/trạng thái Dead. Smoke test WebGL đã chạy trên Chromium với **ZIP fixture riêng (ảnh màu giả để kiểm tra loader)**: 6/6 hướng và Dead đạt. Smoke test chưa xác minh ảnh gốc v1.4 trên điện thoại Android thực.

## Điều kiện còn thiếu
1. Tách layer và rig thực tế cho các hướng ¾/nghiêng/sau (không dùng full-body sprite làm thay thế).
2. Tạo Attack/Skill/Hurt/Dead riêng ở các hướng đó và kiểm tra không hở.
3. Tích hợp bộ VFX 3 Nữ Thần và 4 kỹ năng thực sự, duyệt cơ chế 3 bị động.
4. Đo trên Android thật, rồi mới xét tích hợp Production.
