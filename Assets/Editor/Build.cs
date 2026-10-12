using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace SpiritBeast.Editor
{
    public static class Build
    {
        const string ScenePath = "Assets/Scenes/Main.unity";
        const string OutputDir = "Builds/Web";

        /// <summary>
        /// 命令列建置 Web：
        /// Unity -batchmode -nographics -quit -projectPath . -executeMethod SpiritBeast.Editor.Build.Web -logFile -
        /// </summary>
        public static void Web()
        {
            EnsureMainScene();
            PlayerSettings.companyName = "TBOJ";
            PlayerSettings.productName = "Kingdom Spirits";
            PlayerSettings.WebGL.template = "PROJECT:SpiritBeast";
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
                EditorApplication.Exit(1);
                return;
            }
            Debug.Log($"[Build] Web OK: {report.summary.totalSize / (1024f * 1024f):F1} MB -> {OutputDir}");
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
