# Lyr Sonia — Battle pose góc ¾ phải · Tác vụ 1 (v1.8 QA)

**Trạng thái:** KHÓA TƯ THẾ ĐÃ DUYỆT — CHƯA PHẢI MODEL CHIẾN ĐẤU HOÀN CHỈNH.

- Nguồn: tranh `three_quarter_right.png` (234×398) từ bộ hình sáu hướng Lyr Sonia v1.4 đã duyệt.
- SHA-256 ảnh PNG nguồn không chỉnh sửa: `b4324f9ab942c91017b3862a87dd16630d7ccc959a1bed4e776393891aba9df7`.
- Texture WebP QA chất lượng 85: SHA-256 `7a1a336b75238d0116fe3410d285fb7c2d5f4d526c8caed1a33f08529da01a8e`.
- Spine **3.6.37**: attachment `three_quarter_right` cho slot `combat_stance`, animation `battle_idle` khóa đúng tư thế. Không dùng ảnh chính diện, không lật ảnh để giả góc.
- **Không làm giả hoạt ảnh**: nguồn một lớp nguyên người chưa có rig phân tách tay/chân/tóc/váy/trượng.
- Cần tiếp tục vẽ tách lớp và rig đúng góc ¾ phải cho `Idle`, `Attack`, `Skill`, `Hurt`, và `Dead`; Dead ngã theo mẫu đã duyệt rồi biến mất, không nằm mãi trên sân.
- Trong trận chiến GXB 3 **không chạy/di chuyển**. Không tự ý thêm hoạt ảnh lao tới mục tiêu.
- Các tệp này chỉ là QA reference, **không được nạp vào roster, combat gameplay hoặc player Neon**.
- Mẫu PNG nguyên gốc (không nén) có trong `Lyr_Sonia_Battle_ThreeQuarterRight_v18_QA.zip` được bàn giao riêng.

Trình kiểm tra WebGL riêng trên VPS: trang `/tmp/lyr_sonia_chaos_v16_qa/index.html` thông qua Termalin.
