# 開發指南

> 開發、測試、建置、CI 與部署的完整說明。專案概觀請見根目錄 [`README.md`](../README.md)。

## 版本

- **Unity 6000.3.25f1（Unity 6.3 LTS）**，以 `ProjectSettings/ProjectVersion.txt` 為準。
- 不用 Beta 版（例如 6.7 Beta）：CI 的 GameCI 映像只提供正式版，且 Beta 不適合給孩子用的產品。
- 升級版本時：本機先升級並跑過測試與建置 → 改 `ProjectVersion.txt` → 確認 [GameCI 映像](https://hub.docker.com/r/unityci/editor/tags) 有該版本的 `webgl` 標籤。

## 本機環境（macOS）

1. 以 Unity CLI 安裝編輯器，**需含 WebGL Build Support 模組**（模組參數請看 `unity install --help`）：

   ```bash
   unity install 6000.3.25f1
   ```

2. 用 Unity Hub 或 Unity CLI 開啟本專案資料夾。第一次開啟會產生 `Library/`（不進版控）、
   各檔案的 `.meta` 與 `ProjectSettings/*.asset`——**這些要 commit**（`.meta` 記錄資產 GUID，漏了會讓引用斷掉）。
3. 純 C# 核心測試需要 [.NET 8 SDK](https://dotnet.microsoft.com/download)（`brew install dotnet@8` 亦可）。

## 測試

```bash
# 純 C# 核心（Assets/Core）：不需要開 Unity，幾秒跑完
dotnet test Tools/CoreTests

# 同一批測試在 Unity 裡跑（EditMode）
"$UNITY" -batchmode -nographics -projectPath . \
  -runTests -testPlatform EditMode -testResults results.xml -logFile -
```

- `$UNITY` 是編輯器執行檔路徑。Unity Hub 預設在
  `/Applications/Unity/Hub/Editor/6000.3.25f1/Unity.app/Contents/MacOS/Unity`；用 Unity CLI 安裝的，以 CLI 顯示的安裝位置為準。
- 核心邏輯一律放 `Assets/Core`（`noEngineReferences`，不能引用 UnityEngine），測試放 `Assets/Tests/EditMode`，只用 NUnit。
  `Tools/CoreTests` 直接編譯這兩個資料夾的原始檔，所以**同一份測試在 dotnet 與 Unity 都會跑**。
- C# 語法以 C# 9 為上限（Unity 6 的版本）；`Tools/CoreTests` 已設 `LangVersion 9.0` 把關。
  但 .NET 8 的 API 比 Unity 多，用到較新的 API 時要靠 Unity 端的 CI 抓。

## 建置 Web

```bash
"$UNITY" -batchmode -nographics -quit -projectPath . \
  -executeMethod SpiritBeast.Editor.Build.Web -logFile -
```

- 輸出在 `Builds/Web/`（不進版控）。建置腳本：`Assets/Editor/Build.cs`。
- 網頁模板：`Assets/WebGLTemplates/SpiritBeast/index.html`。它負責讀取平台帶來的授權片段（`#at=…&child=…`）、
  立刻清掉網址列，再交給 C#（`Assets/Plugins/WebGL/AuthFragment.jslib`）。
- 壓縮用 Brotli ＋「解壓縮後備」：主機沒設好 `Content-Encoding` 也能開，只是比較慢。

### 本機預覽

```bash
npx --yes serve Builds/Web
```

直接開 `http://localhost:3000` 會顯示「Fragment: Empty」（正常，沒帶片段）。
測授權交接可開 `http://localhost:3000/#at=test&child=3f2504e0-4f89-11d3-9a0c-0305e82c3301`，
畫面左上應顯示 `Fragment OK child=3f2504e0...`，且網址列的 `#…` 會立刻消失。

## CI（GitHub Actions）

`.github/workflows/ci.yml` 有三個 job：

| Job | 內容 | 需要的 Secrets |
| --- | --- | --- |
| `core-tests` | `dotnet test`，每次必跑 | 無 |
| `unity` | Unity EditMode 測試＋Web 建置，產物上傳為 artifact `web` | `UNITY_LICENSE`、`UNITY_EMAIL`、`UNITY_PASSWORD` |
| `deploy` | 僅 push 到 `main`：把建置結果部署到 Vercel | `VERCEL_TOKEN`、`VERCEL_ORG_ID`、`VERCEL_PROJECT_ID`（＋上面的 Unity 授權） |

Secrets 未設定時，`unity` 與 `deploy` 會在 Actions 頁面留下黃色警告並略過，不會假裝通過了建置。

### 設定 Unity 授權（一次性）

依 [GameCI 啟用說明](https://game.ci/docs/github/activation)（Personal 授權）：

1. 在 Mac 上用 Unity Hub 登入並啟用 Personal 授權。
2. 授權檔在 `/Library/Application Support/Unity/Unity_lic.ulf`，把**整個檔案內容**貼到 repo 的
   Settings → Secrets and variables → Actions → New repository secret，名稱 `UNITY_LICENSE`。
3. 再新增 `UNITY_EMAIL`、`UNITY_PASSWORD`（Unity 帳號）。
4. `.ulf` 是機密，已列入 `.gitignore`，**不要 commit**。

## 部署（Vercel，一次性）

1. 在本 repo 資料夾執行 `npx vercel link`，選擇建立新專案（名稱如 `kingdom-spirits`）。
   **不要**在 Vercel 網站用「Import Git Repository」——Vercel 無法建置 Unity，建置交給 CI。
2. 產生的 `.vercel/project.json` 裡有 `orgId` 與 `projectId`，分別存成 Secrets `VERCEL_ORG_ID`、`VERCEL_PROJECT_ID`。
3. 到 [vercel.com/account/tokens](https://vercel.com/account/tokens) 建立 token，存成 `VERCEL_TOKEN`。
4. 之後每次 merge 進 `main`，CI 建置完成就會自動部署。`vercel.json`（壓縮檔的標頭設定）會一起帶上去。

部署後的網址要填回牧區平台，作為家長服事卡頁「去看靈獸」連結的目標（平台端 P1）。
