using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace SpiritBeast.Editor
{
    public static class Build
    {
        const string ScenePath = "Assets/Scenes/Main.unity";
        const string OutputDir = "Builds/Web";
        const string SizeReportPath = "Builds/Web-size-report.txt";   // 放在 Web 資料夾外面，不會被部署
        // 下載大小上限：Web 建置壓縮後 30 MB（組長裁決 2026-10-29，GDD §10；原訂 15 MB）
        const long BudgetBytes = 30L * 1024 * 1024;

        [MenuItem("Spirit Beast/建置 Web（含大小報告）")]
        static void WebFromMenu() => Web();

        /// <summary>
        /// 命令列建置 Web：
        /// Unity -batchmode -nographics -quit -projectPath . -executeMethod SpiritBeast.Editor.Build.Web -logFile -
        /// 建完寫出大小報告（Builds/Web-size-report.txt）；超過預算時命令列以錯誤碼結束、編輯器跳出提示。
        /// </summary>
        public static void Web()
        {
            EnsureMainScene();
            RenderPipelineSetup.Ensure(true);
            PlayerSettings.companyName = "TBOJ";
            PlayerSettings.productName = "Kingdom Spirits";
            PlayerSettings.WebGL.template = "PROJECT:SpiritBeast";
            // 不顯示 Unity 啟動畫面：孩子點進來直接看到靈獸，也少打包 2.7 MB 的標誌貼圖（Unity 6 個人版可關）
            PlayerSettings.SplashScreen.show = false;
            // 「顯示 Unity 標誌」也要關：只關啟動畫面時，標誌貼圖（2.7 MB）還是會被打包（2026-10-30 大小報告發現）
            PlayerSettings.SplashScreen.showUnityLogo = false;
            PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Brotli;
            // 主機沒設好 Content-Encoding 時由載入器在瀏覽器解壓，仍可開啟（GDD §8.1）
            PlayerSettings.WebGL.decompressionFallback = true;

            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { ScenePath },
                locationPathName = OutputDir,
                target = BuildTarget.WebGL,
                options = BuildOptions.None,
            });

            if (report.summary.result != UnityEditor.Build.Reporting.BuildResult.Succeeded)
            {
                Debug.LogError($"[Build] Web failed: {report.summary.result}");
                Fail();
                return;
            }

            long download = WriteSizeReport(report);
            string summary = $"[Build] Web OK -> {OutputDir}：下載大小 {MB(download)}（預算 {MB(BudgetBytes)}），報告 {SizeReportPath}";
            if (download > BudgetBytes)
            {
                Debug.LogError(summary + " —— 超過預算");
                Fail();
                if (!Application.isBatchMode)
                    EditorUtility.DisplayDialog("建置超過大小預算", $"下載大小 {MB(download)}，預算 {MB(BudgetBytes)}。\n最大的素材列在 {SizeReportPath}。", "好");
                return;
            }
            Debug.Log(summary);
            if (!Application.isBatchMode) EditorUtility.RevealInFinder(SizeReportPath);
        }

        // 命令列才以錯誤碼結束；從選單建置時不能把編輯器關掉
        static void Fail()
        {
            if (Application.isBatchMode) EditorApplication.Exit(1);
        }

        static string MB(long bytes) => $"{bytes / (1024f * 1024f):F1} MB";

        /// <summary>
        /// 大小報告：①實際要下載的檔案（Brotli 壓縮後、在硬碟上的大小，和預算比的是這個）
        /// ②打包進去的素材依大小排序（壓縮前的大小，用來找「誰最大」）。回傳下載總大小。
        /// </summary>
        static long WriteSizeReport(UnityEditor.Build.Reporting.BuildReport report)
        {
            var files = Directory.GetFiles(OutputDir, "*", SearchOption.AllDirectories)
                .Select(f => new FileInfo(f)).OrderByDescending(f => f.Length).ToList();
            long download = files.Sum(f => f.Length);

            var sb = new StringBuilder();
            sb.AppendLine($"Web 建置大小報告　{System.DateTime.Now:yyyy-MM-dd HH:mm}　Unity {Application.unityVersion}");
            sb.AppendLine($"下載大小（壓縮後）：{MB(download)}　預算：{MB(BudgetBytes)}　{(download > BudgetBytes ? "超過預算" : "在預算內")}");
            sb.AppendLine();
            sb.AppendLine("① 下載的檔案（壓縮後）");
            foreach (var f in files)
                sb.AppendLine($"  {MB(f.Length),10}  {Path.GetRelativePath(OutputDir, f.FullName)}");
            sb.AppendLine();
            sb.AppendLine("② 打包的素材，前 40 大（壓縮前；程式碼與引擎本身在 .wasm，不在這裡）");
            var assets = report.packedAssets.SelectMany(p => p.contents)
                .GroupBy(c => string.IsNullOrEmpty(c.sourceAssetPath) ? "(內建／產生的資源)" : c.sourceAssetPath)
                .Select(g => (path: g.Key, size: g.Sum(c => (long)c.packedSize)))
                .OrderByDescending(a => a.size).ToList();
            foreach (var a in assets.Take(40))
                sb.AppendLine($"  {MB(a.size),10}  {a.path}");
            sb.AppendLine($"  （素材共 {assets.Count} 項，合計 {MB(assets.Sum(a => a.size))}）");

            File.WriteAllText(SizeReportPath, sb.ToString());
            return download;
        }

        // 場景只放預設相機與光源，畫面內容由 Bootstrap 在執行期建立
        static void EnsureMainScene()
        {
            if (File.Exists(ScenePath)) return;
            Directory.CreateDirectory(Path.GetDirectoryName(ScenePath));
            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            EditorSceneManager.SaveScene(scene, ScenePath);
        }
    }
}
