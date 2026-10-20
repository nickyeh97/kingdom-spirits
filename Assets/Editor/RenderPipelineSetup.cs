using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace SpiritBeast.Editor
{
    /// <summary>
    /// 確保專案使用 URP（卡通著色器 SpiritBeast/PaletteMask 只在 URP 下運作）。
    /// 還沒設定時自動建立 Assets/Settings/SpiritBeast_URP.asset（含 Renderer）並設為預設管線；
    /// 已經有管線就不動。開專案時自動執行一次，命令列建置（Build.Web）也會先呼叫。
    /// 手機取向：關 HDR、關陰影（卡通明暗不需要投影，省效能）。產生的 .asset 要進版控。
    /// </summary>
    [InitializeOnLoad]
    public static class RenderPipelineSetup
    {
        const string Folder = "Assets/Settings";
        const string AssetPath = Folder + "/SpiritBeast_URP.asset";
        const string RendererPath = Folder + "/SpiritBeast_URP_Renderer.asset";
        const string PostProcessDataPath = "Packages/com.unity.render-pipelines.universal/Runtime/Data/PostProcessData.asset";

        static RenderPipelineSetup() => EditorApplication.delayCall += () => Ensure();

        [MenuItem("Spirit Beast/設定 URP（卡通著色器）")]
        static void Menu() => Ensure(true);

        public static void Ensure(bool log = false)
        {
            if (GraphicsSettings.defaultRenderPipeline != null)
            {
                if (log) Debug.Log($"[URP] 已在使用：{AssetDatabase.GetAssetPath(GraphicsSettings.defaultRenderPipeline)}");
                return;
            }

            var asset = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(AssetPath);
            if (asset == null)
            {
                if (!AssetDatabase.IsValidFolder(Folder)) AssetDatabase.CreateFolder("Assets", "Settings");
                var renderer = ScriptableObject.CreateInstance<UniversalRendererData>();
                renderer.postProcessData = AssetDatabase.LoadAssetAtPath<PostProcessData>(PostProcessDataPath);
                AssetDatabase.CreateAsset(renderer, RendererPath);

                asset = UniversalRenderPipelineAsset.Create(renderer);
                asset.supportsHDR = false;
                asset.shadowDistance = 0f;
                AssetDatabase.CreateAsset(asset, AssetPath);
                var so = new SerializedObject(asset);
                SetBool(so, "m_MainLightShadowsSupported", false);
                SetBool(so, "m_AdditionalLightShadowsSupported", false);
                so.ApplyModifiedPropertiesWithoutUndo();
                AssetDatabase.SaveAssets();
            }

            // 各品質等級沒指定管線時會用這個預設值，所以只設預設管線即可
            GraphicsSettings.defaultRenderPipeline = asset;
            AssetDatabase.SaveAssets();
            Debug.Log($"[URP] 已設定預設管線：{AssetPath}（請把 Assets/Settings 與 ProjectSettings 的變更進版控）");
        }

        static void SetBool(SerializedObject so, string name, bool value)
        {
            var p = so.FindProperty(name);
            if (p != null) p.boolValue = value;
        }
    }
}
