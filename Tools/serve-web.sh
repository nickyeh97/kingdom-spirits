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
# 埠號被占用就停下來，並說是誰占的（serve 的 --no-port-switching 實測沒擋住，會自己換到隨機埠）
if command -v lsof >/dev/null && lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "$PORT 埠已經有程式在用：" >&2
  lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >&2
  echo "" >&2
  echo "多半是之前開的 npx serve 還在跑（VS Code 另一個終端機分頁）。關掉它，或執行：kill <上面的 PID>" >&2
  echo "要改用別的埠：PORT=3100 bash Tools/serve-web.sh（平台的 VITE_SPIRIT_GAME_URL 也要跟著改）" >&2
  exit 1
fi
IP="$(ipconfig getifaddr en0 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}' || true)"
echo "遊戲（這台電腦）：http://localhost:$PORT"
[ -n "$IP" ] && echo "遊戲（同 Wi-Fi 的手機）：http://$IP:$PORT   ← 平台的 VITE_SPIRIT_GAME_URL 填這個"
echo "停止：Ctrl+C"
# 上面已經確認埠號是空的；--no-port-switching 留著當第二道保險
exec npx --yes serve Builds/Web --listen "tcp://0.0.0.0:$PORT" --no-port-switching
