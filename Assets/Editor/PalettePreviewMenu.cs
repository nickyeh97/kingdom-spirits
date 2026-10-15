using System.Collections.Generic;
using System.IO;
using System.Linq;
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
            var models = ModelsBesides(model);
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            // 開一個不存檔的暫存場景，不會動到 Main.unity
            EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            var preview = new GameObject(nameof(PalettePreview)).AddComponent<PalettePreview>();
            preview.Model = model;
            preview.Models = models;
            EditorApplication.EnterPlaymode();
        }

        /// <summary>同資料夾的所有模型（依名稱排序），讓 Play 中可以直接切換</summary>
        static List<GameObject> ModelsBesides(GameObject model)
        {
            var folder = Path.GetDirectoryName(AssetDatabase.GetAssetPath(model))?.Replace('\\', '/');
            if (string.IsNullOrEmpty(folder)) return new List<GameObject> { model };
            return AssetDatabase.FindAssets("t:Model", new[] { folder })
                .Select(guid => AssetDatabase.GUIDToAssetPath(guid))   // 方法群組會因 string／GUID 兩個多載而模稜兩可
                .Where(p => Path.GetDirectoryName(p)?.Replace('\\', '/') == folder)   // 不含子資料夾
                .Select(path => AssetDatabase.LoadAssetAtPath<GameObject>(path))
                .Where(go => go != null)
                .OrderBy(go => go.name)
                .DefaultIfEmpty(model)
                .ToList();
        }

        [MenuItem(MenuPath, true)]
        static bool CanOpen() =>
            Selection.activeObject is GameObject go && EditorUtility.IsPersistent(go) && !EditorApplication.isPlaying;
    }
}
