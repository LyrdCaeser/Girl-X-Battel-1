# GXB 3 — Ảnh đại diện từ thư viện máy

## Hành vi người chơi

Trong Hồ sơ → Ảnh đại diện → Avatar, người chơi có thể tải ảnh JPEG/PNG/WebP từ thư viện máy, dùng ảnh đó hoặc chuyển về avatar gốc. Có nút **Xóa ảnh của tôi**. Ảnh cá nhân là ảnh công khai, xuất hiện ở hồ sơ/sảnh, danh sách Bang Hội và xếp hạng Đấu Trường. Bộ khung và kho avatar/Nữ Thần gốc vẫn giữ nguyên.

## Lưu trữ và an toàn

- Máy khách cắt vuông và nén WebP 320×320. Máy chủ **luôn** giải mã và nén lại bằng Pillow; không tin định dạng/tên do máy khách khai báo; không nhận SVG/GIF động.
- Giới hạn yêu cầu ảnh 3 MiB; giới hạn số pixel và dung lượng sau nén. Xóa EXIF/GPS và metadata nhúng trong output WebP.
- Bắt buộc phiên đăng nhập hợp lệ, kiểm tra Origin. **Tối đa một lần tải hoặc thay ảnh cá nhân mỗi 24 giờ tính từ lần tải thành công**, theo UID tài khoản trên mọi world. Thời điểm được lưu lâu dài tại Neon `profile_avatar_upload_cooldowns`; không reset khi xóa ảnh, đổi máy, đổi server/world hay restart VPS. API `/api/profile/photo/status` giúp giao diện báo giờ/phút còn lại; POST mới trong thời gian chờ trả HTTP 429 + `Retry-After` trước khi đọc/giải mã ảnh. Vẫn giới hạn thêm 3 yêu cầu tải/giờ theo UID để chống CPU spam (người dùng cùng Wi-Fi không ảnh hưởng nhau). Không nhận UID/server từ JSON để xác định chủ ảnh.
- Ảnh lưu trong bảng PostgreSQL Neon `profile_avatar_photos` (`avatar_key` ngẫu nhiên, UID, server_id, picture BYTEA, updated_at). Cửa sổ hồ sơ lưu `profile.avatar` và `profile.uploaded_avatar` theo **đúng UID + world**; game không lấy ảnh của tài khoản khác dù đoán được tên token.
- Mỗi avatar có URL bất biến `/api/profile/photo/custom_<128-bit-random>.webp`, công khai để người chơi khác nhìn thấy. Khi **upload ảnh mới và lưu profile thành công**, máy chủ xóa **tất cả ảnh cũ cùng UID+world khỏi Neon BYTEA**, kể cả ảnh tồn lưu từ lỗi cũ, để không phình dung lượng. Xóa ảnh cá nhân cũng dọn tất cả ảnh của UID+world nhưng vẫn giữ cooldown. Không xóa ảnh của cùng UID trên world khác khi hồ sơ đó còn sử dụng. Nếu lưu hồ sơ thất bại thì ảnh mới và thời gian chờ mới được hoàn tác, ảnh cũ vẫn nguyên. Neon backup bao gồm cả ảnh, không phụ thuộc ổ đĩa VPS.
- Thao tác ảnh không trừ tiền tệ/vật phẩm, không thay save tiến trình, không sửa bảng skin.

## Trước phát hành client

- Android: bản ứng dụng cũ không hỗ trợ `onShowFileChooser`. Mã native mới sử dụng `ACTION_OPEN_DOCUMENT` + quyền đọc URI **chỉ ảnh được chọn**, không đòi quyền truy cập toàn thư viện. Vì thế phải có **bản APK mới** khi chủ game quyết định phát hành, dù API/web đã chạy trên Production.
- iOS: WebKit dùng picker mặc định và có `NSPhotoLibraryUsageDescription` cho bản IPA mới. Windows WebView2 dùng picker của hệ thống. Cả ba cần được QA trên thiết bị thật ở đợt release.
- GitHub Actions chỉ **đăng công khai GitHub Release** nếu chủ game mở workflow thủ công và bật checkbox `publish`; một lần push nhánh không thể ghi đè Release hiện hành. Các bản build CI chưa phải bản phát hành.
- Chạy `python -m unittest discover -s tests -p 'test_profile_photo_upload.py'` cùng full regression. Kiểm tra POST ẩn danh = 401, không đúng Origin = 403, ảnh giả = 400, quá lớn = 413, UID khác không thể chọn ảnh, và đồng bộ qua đăng nhập lại.
