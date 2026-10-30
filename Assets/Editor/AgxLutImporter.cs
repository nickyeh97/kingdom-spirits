using UnityEditor;

namespace SpiritBeast.Editor
{
    /// <summary>
    /// AgX 查找表（Assets/Resources/Shaders/AgX_Lut.png）的匯入設定：它存的是數值不是顏色，
    /// 所以關 sRGB、不壓縮、不產生 mipmap、邊緣夾住、雙線性內插——任何一項錯了，Blender 預覽模式的顏色就會偏。
    /// 用 Tools/bake_agx_lut.py 從 Blender 重新烘焙。
    /// </summary>
    public sealed class AgxLutImporter : AssetPostprocessor
    {
        void OnPreprocessTexture()
        {
            if (!assetPath.EndsWith("Shaders/AgX_Lut.png")) return;
            var importer = (TextureImporter)assetImporter;
            importer.sRGBTexture = false;
            importer.mipmapEnabled = false;
            importer.wrapMode = UnityEngine.TextureWrapMode.Clamp;
            importer.filterMode = UnityEngine.FilterMode.Bilinear;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.maxTextureSize = 2048;
        }
    }
}
