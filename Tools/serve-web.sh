#!/usr/bin/env bash
# 本機用固定的埠號開遊戲（預設 3000）。
# Unity 的「Build And Run」每次都換一個隨機埠號，平台 .env.staging.local 的 VITE_SPIRIT_GAME_URL 就對不上；
# 改成：Unity 只「建置」（選單 Spirit Beast/建置 Web），這個伺服器開著不用關，重新建置後重新整理網頁即可。
# 用法（repo 根目錄）：bash Tools/serve-web.sh        換埠號：PORT=3100 bash Tools/serve-web.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PORT="${PORT:-3000}"
if [ ! -f Builds/Web/index.html ]; then
  echo "還沒有建置：先在 Unity 選單「Spirit Beast/建置 Web（含大小報告）」" >&2
  exit 1
fi
IP="$(ipconfig getifaddr en0 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}' || true)"
echo "遊戲（這台電腦）：http://localhost:$PORT"
[ -n "$IP" ] && echo "遊戲（同 Wi-Fi 的手機）：http://$IP:$PORT   ← 平台的 VITE_SPIRIT_GAME_URL 填這個"
echo "停止：Ctrl+C"
# --no-port-switching：埠號被占用時直接報錯，不會偷偷換成別的埠（那樣平台的連結又會對不上）
exec npx --yes serve Builds/Web --listen "tcp://0.0.0.0:$PORT" --no-port-switching
