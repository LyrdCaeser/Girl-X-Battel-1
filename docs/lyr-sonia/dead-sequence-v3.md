# Lyr Sonia — Tác vụ 3: Hurt → Dead → biến mất (QA)

**Trạng thái:** Đạt kiểm thử điều khiển, **CHƯA ĐẠT** nghiệm thu hoạt ảnh. Không tích hợp Production.

## Hợp đồng
- Idle: đứng tại chỗ ở góc **¾ phải**. Không có Move/Run trên chiến trường.
- Hurt (không chí mạng): phản ứng trúng đòn, trở về Idle khi HP còn trên 0.
- HP về 0: phát Dead một lần; khóa nhận đòn, Idle/Attack/Skill/Hurt, bỏ khả năng chọn làm mục tiêu.
- Dùng nguyên vẹn tư thế Dead nằm nghiêng đã duyệt. Event `dead_final_reached` tại **1,155 giây**.
- Hoàn thành Dead tại **1,55 giây**: `figure.visible = false`, không để xác, giữ registry để hồi sinh hợp lệ.
- Dự phòng **2,5 giây** nếu event completion không đến; token hóa callback để hồi sinh không bị ẩn bởi tác vụ cũ.
- Không làm ảnh hưởng nhân vật khác trong đội hình.
- Việc ẩn thuộc vòng đời hình ảnh; logic gameplay về quyền hồi sinh tuân theo cơ chế game hiện hành.

## Tình trạng kiểm thử
- Bộ QA cục bộ v3.0: **13/13** bài kiểm tra hợp đồng và điều khiển đạt.
- Đối chiếu mã `web/battle-animation.js`: hệ thống hiện tại phát Dead một lần, ẩn sau completion và có fallback (không sửa file này).
- **Không** có bằng chứng nghiệm thu WebGL Android thật cho model tích hợp v3.0.
- **Lỗi hình ảnh còn lại từ 2.4.1:** bóng kép và đổi pose giật ở khoảng 0,17 / 0,49 / 0,82 / 1,13 giây. Cần vẽ/tách bổ sung các phần khuất và chỉnh rig trước khi phát hành.

## Cổng nghiệm thu
1. Sửa hoàn toàn bóng kép, không lộ khớp hoặc văng khỏi khung.
2. Kiểm thử trực quan trên Pixi-Spine 3.6.37 ở PC và Mobile.
3. Test FPS/độ ổn định trên Android thật.
4. Kiểm chứng Dead & hồi sinh trong trận chiến thật với nhân vật thực và bảo toàn Neon.

Mọi tệp này chỉ ghi lại hợp đồng và kiểm thử, **không thay đổi gameplay/Neon**.
