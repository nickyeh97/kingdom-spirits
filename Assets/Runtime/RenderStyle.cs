using UnityEngine;

namespace SpiritBeast.Runtime
{
    public enum RenderMode { Toon = 0, Blender = 1 }

    /// <summary>
    /// 渲染模式切換（所有靈獸材質一起換，著色器讀全域 _SpiritStyle）：
    ///   卡通：正式的遊戲畫面——兩段明暗＋描邊，用場景原本的燈光與背景。
    ///   Blender 預覽：跟美術檢查用的 Cycles 預覽圖一致（art-worklog 裡的算圖），方便對照模型——
    ///     太陽、環境光、背景、AgX 色調都換成算圖的設定，太陽會投影，不畫描邊。
    /// 選擇記在 PlayerPrefs，下次開啟維持同一個模式。
    /// </summary>
    public static class RenderStyle
    {
        // ---- Blender 預覽算圖的設定（Blender 4.2.23 Cycles 實測，2026-10-21）----
        // 太陽：強度 3、旋轉 (50°, 0, −30°)；Cycles 裡強度 S 照在白色漫射面上＝S/π
        const float SunStrength = 3f;
        // 光線前進的方向，換到 Unity 世界（相機在 −Z 看 +Z、模型轉向相機，跟 Blender 算圖的擺法相同）：
        // 從畫面左上、相機後方照過來
        static readonly Vector3 SunTravel = new Vector3(0.383f, -0.643f, 0.663f);
        // 世界：顏色 (0.55, 0.60, 0.65) × 強度 0.6（線性值；均勻世界光照在白色漫射面上＝原值）
        static readonly Vector4 Ambient = new Vector4(0.55f * 0.6f, 0.60f * 0.6f, 0.65f * 0.6f, 1f);
        // 背景：上面的世界顏色經過 AgX 後，算圖裡的像素值（sRGB）
        static readonly Color32 Background = new Color32(151, 155, 159, 255);
        const string PrefKey = "SpiritBeast.RenderMode";

        public static RenderMode Mode { get; private set; }

        static Camera _camera;
        static Light _sun;
        static bool _sunCreated;
        // 卡通模式要還原的原本設定
        static Quaternion _toonRotation;
        static float _toonIntensity;
        static Color _toonColor, _toonBackground;

        public static string Label => Mode == RenderMode.Toon ? "卡通" : "Blender 預覽";

        /// <summary>場景開始時呼叫：記下原本的燈光與背景，套用上次選的模式</summary>
        public static void Init(Camera camera)
        {
            _camera = camera;
            _sunCreated = false;
            _sun = FindSun();
            _toonRotation = _sun.transform.rotation;
            _toonIntensity = _sun.intensity;
            _toonColor = _sun.color;
            _toonBackground = camera.backgroundColor;
            Shader.SetGlobalTexture("_SpiritAgxLut", Resources.Load<Texture2D>("Shaders/AgX_Lut"));
            // 全域設定在編輯器裡結束 Play 後還會留著：結束時切回卡通，Scene 視窗與正式遊戲不受影響
            Application.quitting -= ResetGlobal;
            Application.quitting += ResetGlobal;
            Apply(Load());
        }

        static void ResetGlobal() => Shader.SetGlobalFloat("_SpiritStyle", 0f);

        public static void Toggle() => Apply(Mode == RenderMode.Toon ? RenderMode.Blender : RenderMode.Toon);

        public static void Apply(RenderMode mode)
        {
            Mode = mode;
            Shader.SetGlobalFloat("_SpiritStyle", (float)mode);
            Shader.SetGlobalVector("_SpiritAmbient", Ambient);
            if (_sun != null)
            {
                bool blender = mode == RenderMode.Blender;
                // 自己建的太陽在卡通模式關掉（場景原本沒有燈，卡通模式也就維持沒有）
                if (_sunCreated) _sun.enabled = blender;
                _sun.transform.rotation = blender ? Quaternion.LookRotation(SunTravel) : _toonRotation;
                _sun.intensity = blender ? SunStrength / Mathf.PI : _toonIntensity;
                _sun.color = blender ? Color.white : _toonColor;
                // 卡通模式不投影（卡通明暗本來就不用影子）：URP 不會畫陰影圖，手機上沒有額外負擔
                _sun.shadows = blender ? LightShadows.Soft : LightShadows.None;
            }
            if (_camera != null) _camera.backgroundColor = mode == RenderMode.Blender ? (Color)Background : _toonBackground;
            Save(mode);
        }

        static Light FindSun()
        {
            if (RenderSettings.sun != null) return RenderSettings.sun;
            foreach (var l in Object.FindObjectsByType<Light>(FindObjectsSortMode.None))
                if (l.type == LightType.Directional) return l;
            _sunCreated = true;
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            return sun;
        }

        // PlayerPrefs 在某些瀏覽器環境（隱私模式等）可能失敗：失敗就用預設的卡通模式，不影響畫面
        static RenderMode Load()
        {
            try { return PlayerPrefs.GetInt(PrefKey, 0) == 1 ? RenderMode.Blender : RenderMode.Toon; }
            catch { return RenderMode.Toon; }
        }

        static void Save(RenderMode mode)
        {
            try { PlayerPrefs.SetInt(PrefKey, (int)mode); }
            catch { }
        }
    }
}
