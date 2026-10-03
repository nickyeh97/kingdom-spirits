using SpiritBeast.Runtime;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace SpiritBeast.Editor
{
    /// <summary>美術檢查：在 Project 視窗選取靈獸模型（FBX）→ 選單開啟配色預覽並自動進入 Play</summary>
    public static class PalettePreviewMenu
    {
        const string MenuPath = "Spirit Beast/配色預覽（選取的模型）";

        [MenuItem(MenuPath)]
        static void Open()
        {
            var model = Selection.activeObject as GameObject;
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            // 開一個不存檔的暫存場景，不會動到 Main.unity
            EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            new GameObject(nameof(PalettePreview)).AddComponent<PalettePreview>().Model = model;
            EditorApplication.EnterPlaymode();
        }

        [MenuItem(MenuPath, true)]
        static bool CanOpen() =>
            Selection.activeObject is GameObject go && EditorUtility.IsPersistent(go) && !EditorApplication.isPlaying;
    }
}
