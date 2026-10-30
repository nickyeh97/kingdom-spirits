using UnityEngine;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// 背景音樂（組長 2026-10-30：「舒服很 chill」）：Resources/Audio/bgm_home.ogg，Tools/make_bgm.py 程式合成的原創曲，
    /// 53 秒無縫循環、小聲播放。可以關掉（例如在聚會現場），選擇記在 PlayerPrefs，下次開啟維持。
    /// 瀏覽器規定使用者點過畫面才能出聲：網頁版會在第一次點擊之後才開始播（Unity 自動處理）。
    /// </summary>
    public static class BackgroundMusic
    {
        const string Clip = "Audio/bgm_home";
        const float Volume = 0.35f;            // 背景音樂要小聲，不搶孩子跟家長說話
        const string PrefKey = "SpiritBeast.Music";

        static AudioSource _source;

        public static bool On { get; private set; } = true;
        public static string Label => On ? "音樂：開" : "音樂：關";

        /// <summary>場景開始時呼叫一次：建立播放器，照上次的選擇播或不播</summary>
        public static void Init()
        {
            var clip = Resources.Load<AudioClip>(Clip);
            if (clip == null) { Debug.LogWarning("[音樂] 找不到 Resources/" + Clip); return; }
            var go = new GameObject("BackgroundMusic");
            // 場景的相機上有 AudioListener；Demo 自己建相機時沒有，就掛在這裡（沒有它就聽不到聲音）
            if (Object.FindAnyObjectByType<AudioListener>() == null) go.AddComponent<AudioListener>();
            _source = go.AddComponent<AudioSource>();
            _source.clip = clip;
            _source.loop = true;
            _source.volume = Volume;
            _source.playOnAwake = false;
            _source.spatialBlend = 0f;
            Apply(Load());
        }

        public static void Toggle() => Apply(!On);

        static void Apply(bool on)
        {
            On = on;
            if (_source != null)
            {
                if (on && !_source.isPlaying) _source.Play();
                else if (!on) _source.Stop();
            }
            Save(on);
        }

        // PlayerPrefs 在某些瀏覽器環境（隱私模式等）可能失敗：失敗就預設開著
        static bool Load()
        {
            try { return PlayerPrefs.GetInt(PrefKey, 1) == 1; }
            catch { return true; }
        }

        static void Save(bool on)
        {
            try { PlayerPrefs.SetInt(PrefKey, on ? 1 : 0); }
            catch { }
        }
    }
}
