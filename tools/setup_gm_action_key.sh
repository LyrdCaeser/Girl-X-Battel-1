#!/usr/bin/env bash
# Run on the GXB3 VPS as root. Never commit or send this generated key in chat.
# Does not modify game saves, assets, Neon or player accounts.
set -euo pipefail

if (( EUID != 0 )); then
  echo "Chạy bằng: sudo bash tools/setup_gm_action_key.sh"
  exit 1
fi
systemctl cat gxb3.service >/dev/null

dir=/etc/gxb3
file="$dir/gm-action-key.env"
override_dir=/etc/systemd/system/gxb3.service.d
dropin="$override_dir/60-gm-action-key.conf"
install -d -m 0700 "$dir"
install -d -m 0755 "$override_dir"

if [[ -e "$file" ]]; then
  echo "Khóa GM hiện tại đã tồn tại tại $file, không ghi đè."
  echo "Nếu đã biết khóa, sử dụng lại trong GM Tools."
else
  # Random 48-byte base64url token; never take it from clipboard, chat or repository.
  key="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
  ( umask 077; printf 'GXB3_GM_ACTION_KEY=%s\n' "$key" > "$file" )
  chmod 0600 "$file"
  # Never print secrets to shared terminal output or copied diagnostic logs.
  # The owner can read the root-only file privately on the VPS when needed.
  echo "Đã tạo khóa GM an toàn tại $file (không hiển thị giá trị)."
  echo "Đọc khóa RIÊNG TƯ trên VPS khi cần; tuyệt đối không gửi nội dung file vào chat."
  unset key
fi

cat > "$dropin" <<'EOF'
[Service]
EnvironmentFile=/etc/gxb3/gm-action-key.env
EOF
chmod 0644 "$dropin"
systemctl daemon-reload
systemctl restart gxb3.service
echo "Đã cài GXB3_GM_ACTION_KEY vào systemd và restart gxb3."
echo "Kiểm tra bản phát hành: /opt/gxb3/.venv/bin/python /opt/gxb3/tools/verify_vps_release.py"
