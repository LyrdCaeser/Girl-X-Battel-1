# Lyr Sonia — Skill QA v2.1 (KHÔNG PHÁT HÀNH)

## Phần đã thực hiện
- Ảnh ¾ phải đã duyệt được tách thành 8 attachment từ pixel gốc, cộng với trượng từ atlas Lyr Sonia có sẵn.
- 10 xương điều khiển thân trên/tay/trượng/tóc/váy/vòng đầu qua Pixi-Spine 3.6.37.
- Hoa sen Nymphaea tăng kích thước và độ tương phản; hiệu ứng Monica giữ nguyên.
- PC và Mobile đủ 7 bước VFX; tối đa 2 VFX đồng thời; không dây hồng.
- Skill hit tại 1,12 giây. Đây là QA xem hình, không chỉnh gameplay hoặc dữ liệu Neon.

## Giới hạn
- Tách lớp bằng mask ảnh giúp cử động thật nhưng CHƯA là art mesh hoàn chỉnh: cần bù vùng khuất, sửa khớp tay, tóc, váy.
- Chưa kiểm tra GPU Android thật, chưa tích hợp combat, chưa phát hành.
- Ba kỹ năng bị động chưa được chốt nội dung.

## Khôi phục preview QA trên VPS
Chạy trong thư mục này:
    python3 check_contract.py
    python3 restore_qa.py /tmp/lyr_sonia_skill_v20_rebuilt_qa
    python3 -m http.server 18889 --bind 127.0.0.1 --directory /tmp/lyr_sonia_skill_v20_rebuilt_qa

WebP được lưu dạng Base64 text trong images.b64.json, tránh upload Git LFS thêm khi quota giới hạn.
model.atlas.txt được khôi phục thành model.atlas.
FX dùng đường dẫn chỉ đọc trong /opt/gxb3/web/assets/battle-fx, không thay đổi FX gốc.

## Sửa lỗi v2.1
- Khôi phục nét kim loại liên tục của cán trượng, giữ đầu trượng và vị trí tay cầm từ atlas gốc.
- Xóa hai vòng elip hồng do mã QA tự vẽ; KHÔNG xóa hiệu ứng Monica gốc.
- PC và Mobile vẫn giữ đủ 7 nhịp VFX; mọi chỉnh sửa chỉ thuộc QA.
