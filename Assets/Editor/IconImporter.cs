using UnityEditor;

namespace SpiritBeast.Editor
{
    /// <summary>
    /// 介面圖示（Assets/Resources/Icons/**，Tools/make_icons.py 產生）的匯入設定：
    /// 透明邊緣不出現黑邊、縮小顯示時用 mipmap 才不會鋸齒、不壓縮（圖小、壓縮會糊掉描邊）。
    /// </summary>
    public sealed class IconImporter : AssetPostprocessor
    {
        void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith("Assets/Resources/Icons/")) return;
            var importer = (TextureImporter)assetImporter;
            importer.alphaIsTransparency = true;
            importer.mipmapEnabled = true;
            importer.wrapMode = UnityEngine.TextureWrapMode.Clamp;
            importer.filterMode = UnityEngine.FilterMode.Trilinear;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.maxTextureSize = 128;
        }
    }
}
