using UnityEditor;
using UnityEngine;

namespace SpiritBeast.Editor
{
    /// <summary>
    /// 輸入系統一定要是舊版 Input Manager（Project Settings → Player → Active Input Handling＝Input Manager (Old)）：
    /// 介面的 EventSystem 用 StandaloneInputModule，新版 Input System 套件沒裝；設錯時 PC 與手機的按鈕都點不動。
    /// 這個設定改了要「重開 Unity」才生效——開專案時自動檢查，不對就改回來並詢問是否馬上重開。
    /// </summary>
    [InitializeOnLoad]
    public static class InputHandlerCheck
    {
        const int OldInputManager = 0;   // 0 舊版、1 新版 Input System、2 兩者

        static InputHandlerCheck() => EditorApplication.delayCall += Check;

        [MenuItem("Spirit Beast/檢查輸入設定")]
        static void Menu()
        {
            if (!Check()) EditorUtility.DisplayDialog("輸入設定", "輸入設定正確：Input Manager (Old)。", "好");
        }

        /// <summary>回傳是否有修正</summary>
        static bool Check()
        {
            var settings = Unsupported.GetSerializedAssetInterfaceSingleton("PlayerSettings");
            if (settings == null) return false;
            var so = new SerializedObject(settings);
            var prop = so.FindProperty("activeInputHandler");
            if (prop == null || prop.intValue == OldInputManager) return false;

            prop.intValue = OldInputManager;
            so.ApplyModifiedProperties();
            AssetDatabase.SaveAssets();
            Debug.LogWarning("[輸入設定] Active Input Handling 已改回 Input Manager (Old)；重開 Unity 後按鈕才點得動。");
            if (!Application.isBatchMode &&
                EditorUtility.DisplayDialog("輸入設定已修正",
                    "Active Input Handling 原本不是 Input Manager (Old)，介面按鈕會點不動。\n已經改回來，要重開 Unity 才會生效。",
                    "現在重開", "稍後"))
                EditorApplication.OpenProject(System.IO.Directory.GetCurrentDirectory());
            return true;
        }
    }
}
