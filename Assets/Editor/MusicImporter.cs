using UnityEditor;
using UnityEngine;

namespace SpiritBeast.Editor
{
    /// <summary>
    /// 背景音樂（Assets/Resources/Audio/**，Tools/make_bgm.py 產生）的匯入設定：
    /// 壓縮留在記憶體、品質 50%（背景音樂小聲播放，聽不出差別；建置檔小很多），背景載入不卡畫面。
    /// </summary>
    public sealed class MusicImporter : AssetPostprocessor
    {
        void OnPreprocessAudio()
        {
            if (!assetPath.StartsWith("Assets/Resources/Audio/")) return;
            var importer = (AudioImporter)assetImporter;
            importer.loadInBackground = true;
            var s = importer.defaultSampleSettings;
            s.loadType = AudioClipLoadType.CompressedInMemory;
            s.compressionFormat = AudioCompressionFormat.Vorbis;
            s.quality = 0.5f;
            importer.defaultSampleSettings = s;
        }
    }
}
