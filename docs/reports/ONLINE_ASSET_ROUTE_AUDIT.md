# Online asset route audit

## Kết quả audit

Audit trên `web/` phân loại các URL tuyệt đối của frontend như sau:

- `/assets/*` và `/localization/*`: tài nguyên tĩnh có thể đưa lên CDN.
- File JS/CSS ở root như `/app.js`, `/style.css`: tài nguyên tĩnh có thể đưa lên CDN.
- `/api/*`, `/health` và `/local-log`: route gameplay/API, giữ nguyên trên VPS.

Runtime mới (`web/asset-runtime.js`) chỉ rewrite hai nhóm static đầu tiên và root JS/CSS. Nó không rewrite `/api/*`, auth, save, battle, payment hoặc các route trạng thái người chơi.

Chạy lại audit bằng:

```bash
python3 tools/audit_online_asset_routes.py web
```

## Cấu hình VPS

Sau khi workflow `GXB3 offline resource packs` publish thành công, log sẽ in ra URL dạng:

```text
https://<CLOUDFRONT_DOMAIN>/online-assets/web-<commit-sha>/
```

Đặt biến môi trường trên VPS:

```bash
export GXB_ASSET_BASE_URL="https://<CLOUDFRONT_DOMAIN>/online-assets/web-<commit-sha>/"
```

Sau đó restart Online server. Endpoint `/asset-config.js` sẽ trả cấu hình runtime; không cần ghi CDN domain vào mã nguồn frontend.

Nếu biến không được đặt hoặc rỗng, frontend tự động dùng VPS như fallback. Nếu biến không phải HTTPS URL không có query/fragment, server từ chối trả cấu hình để tránh định tuyến asset sai.

## Publish layout

Workflow publish cùng một commit theo hai dạng:

```text
/offline-resources/<version>/pack-<sha256>.zip
/online-assets/<version>/assets/...
/online-assets/<version>/localization/...
/online-assets/<version>/app.js
/online-assets/<version>/*.css
```

Các file Online được gắn `Cache-Control: public,max-age=31536000,immutable`; vì vậy mỗi version phải dùng prefix mới và có thể rollback bằng cách đổi `GXB_ASSET_BASE_URL` về version cũ.
