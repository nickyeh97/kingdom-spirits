using UnityEditor;

namespace SpiritBeast.Editor
{
    /// <summary>
    /// 靈獸模型（Assets/Art/Resources/Beasts/*.fbx）的匯入設定：
    /// 動作用 Legacy 動畫匯入——執行時用名稱播放（BeastView），不需要另外做 Animator Controller。
    /// 沒有骨架的模型不受影響（沒有動作可匯入）。
    /// </summary>
    public sealed class BeastModelImporter : AssetPostprocessor
    {
        void OnPreprocessModel()
        {
            if (!assetPath.StartsWith("Assets/Art/Resources/Beasts/") || !assetPath.EndsWith(".fbx")) return;
            var importer = (ModelImporter)assetImporter;
            importer.animationType = ModelImporterAnimationType.Legacy;
            importer.importAnimation = true;
            importer.generateAnimations = ModelImporterGenerateAnimations.GenerateAnimations;
        }
    }
}
