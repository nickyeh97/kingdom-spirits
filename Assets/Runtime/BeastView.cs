using System.Collections.Generic;
using SpiritBeast.Core;
using UnityEngine;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// 靈獸的 3D 呈現。有正式模型時載入 Resources/Beasts/英文名_形態（BeastForms），以換色材質上色；
    /// 還沒有模型的變體用內建幾何體拼出占位造型。對外介面一致：Show／Hop／Celebrate／Evolve。
    /// </summary>
    public sealed class BeastView : MonoBehaviour
    {
        static readonly float[] StageScale = { 0.75f, 0.9f, 1.05f, 1.2f };

        Transform _body;
        float _hopTime = -1f;
        float _spinTime = -1f;
        float _evolveTime = -1f;
        string _pendingVariant, _pendingPalette;
        int _pendingStage;

        public bool Evolving => _evolveTime >= 0f;

        /// <summary>使用者轉動的角度（度，水平方向）：Demo 左右滑動時改它，換靈獸、換配色都保留</summary>
        public float Yaw;

        Material _modelMaterial;
        // 有骨架動作的模型（FBX 以 Legacy 動畫匯入）：用名稱播放；沒有動作的模型用下面的程式動作（跳、轉圈）
        Animation _anim;
        readonly Dictionary<string, string> _clips = new Dictionary<string, string>();   // 動作名（Idle…）→ Unity 裡的名稱（Rig|Idle）
        static readonly HashSet<string> Looping = new HashSet<string> { "Idle", "Sleep" };
        string _current;

        /// <summary>動作名稱（Blender 的 Action 名）：待機、開心、揮手、吃果子、睡覺、玩玩具</summary>
        public const string Idle = "Idle", Happy = "Happy", Wave = "Wave", Eat = "Eat", Sleep = "Sleep", PlayToy = "Play";

        public bool Has(string clip) => _anim != null && _clips.ContainsKey(clip);
        public bool Sleeping => _anim != null && _current == Sleep;

        public void Show(string variant, string palette, int stage)
        {
            if (_body != null) Destroy(_body.gameObject);
            if (_modelMaterial != null) Destroy(_modelMaterial);
            _body = new GameObject("Body").transform;
            _body.SetParent(transform, false);
            stage = Mathf.Clamp(stage, 1, 4);

            var v = Catalog.FindVariant(variant);
            var model = v != null ? Resources.Load<GameObject>(BeastForms.ResourcePath(v.DisplayName, stage)) : null;
            if (model != null)
            {
                var go = Instantiate(model, _body);
                go.transform.localPosition = Vector3.zero;
                go.transform.localRotation = Quaternion.identity;
                _modelMaterial = PaletteMaterial.Apply(go, Catalog.FindPalette(palette), PaletteMaterial.FindPattern(model.name));
                if (_modelMaterial != null) _modelMaterial.SetFloat("_PatternStrength", BeastForms.PatternStrength(variant, stage));
                _body.localScale = Vector3.one * BeastForms.Scale(stage);
                SetupAnimation(go);
            }
            else
            {
                _anim = null;
                Build(variant, Catalog.FindPalette(palette), stage);
                _body.localScale = Vector3.one * StageScale[stage - 1];
            }
        }

        public void Hop()
        {
            if (!Play(Happy)) _hopTime = 0f;   // 睡著時點一下也是播 Happy＝醒過來
        }

        public void Celebrate()
        {
            if (!Play(Happy)) _hopTime = 0f;
            _spinTime = 0f;
        }

        /// <summary>
        /// 播一個動作：循環的（待機、睡覺）一直播到下一個動作；其他的播完自動回到待機。
        /// 模型沒有這個動作時回傳 false（呼叫端可以改用程式動作或什麼都不做）。
        /// </summary>
        public bool Play(string clip)
        {
            if (!Has(clip) || Evolving) return false;
            _anim.CrossFade(_clips[clip], 0.15f);
            if (!Looping.Contains(clip)) _anim.CrossFadeQueued(_clips[Idle], 0.2f);
            _current = clip;
            return true;
        }

        /// <summary>
        /// 找出模型裡的動作（Blender 的 Action 匯出成 FBX 後叫「Rig|Idle」這種名字，所以比對「|」後面）並開始待機循環
        /// </summary>
        void SetupAnimation(GameObject go)
        {
            _anim = go.GetComponentInChildren<Animation>();
            _clips.Clear();
            _current = null;
            if (_anim == null) return;
            foreach (AnimationState st in _anim)
            {
                var n = st.name.Substring(st.name.LastIndexOf('|') + 1);
                _clips[n] = st.name;
                st.wrapMode = Looping.Contains(n) ? WrapMode.Loop : WrapMode.Once;
            }
            if (!_clips.ContainsKey(Idle)) { _anim = null; _clips.Clear(); return; }
            _anim.Play(_clips[Idle]);
            _current = Idle;
        }

        /// <summary>進化過場：先放大發光，再換成新階段的樣子（約 3 秒）</summary>
        public void Evolve(string variant, string palette, int newStage)
        {
            _pendingVariant = variant; _pendingPalette = palette; _pendingStage = newStage;
            _evolveTime = 0f;
        }

        void Update()
        {
            if (_body == null) return;
            if (_anim != null && _current != null && !Looping.Contains(_current) && !_anim.IsPlaying(_clips[_current]))
                _current = Idle;                       // 揮手、開心…播完已經自動接回待機
            float t = Time.time;
            // 有骨架動作時呼吸由 Idle 動作負責，不再整隻上下飄
            float y = _anim != null ? 0f : Mathf.Sin(t * 2f) * 0.05f;
            if (_hopTime >= 0f)
            {
                _hopTime += Time.deltaTime;
                y += Mathf.Max(0f, Mathf.Sin(_hopTime * Mathf.PI * 2.5f)) * 0.5f;
                if (_hopTime > 0.8f) _hopTime = -1f;
            }
            float spin = 0f;
            if (_spinTime >= 0f)
            {
                _spinTime += Time.deltaTime;
                spin = Mathf.SmoothStep(0f, 360f, _spinTime / 1.2f);
                if (_spinTime > 1.2f) _spinTime = -1f;
            }
            if (_evolveTime >= 0f)
            {
                _evolveTime += Time.deltaTime;
                float pulse = 1f + Mathf.Sin(Mathf.Clamp01(_evolveTime / 3f) * Mathf.PI) * 0.6f;
                transform.localScale = Vector3.one * pulse;
                spin = _evolveTime * 240f;
                if (_evolveTime > 1.5f && _pendingVariant != null)
                {
                    Show(_pendingVariant, _pendingPalette, _pendingStage);
                    _pendingVariant = null;
                }
                if (_evolveTime > 3f) { _evolveTime = -1f; transform.localScale = Vector3.one; }
            }
            _body.localPosition = new Vector3(0f, y, 0f);
            _body.localRotation = Quaternion.Euler(0f, 200f + Yaw + spin, 0f);
        }

        // ---- 造型 ----

        void Build(string variant, Palette p, int stage)
        {
            Color main = Hex(p.Main), second = Hex(p.Secondary), accent = Hex(p.Accent);
            switch (variant)
            {
                case "dove":
                    Part("Sphere", main, new Vector3(0f, 0.55f, 0f), new Vector3(0.9f, 0.8f, 1f));
                    Part("Sphere", main, new Vector3(0f, 1.15f, 0.2f), Vector3.one * 0.6f);
                    Part("Sphere", second, new Vector3(-0.5f, 0.6f, -0.05f), new Vector3(0.18f, 0.5f, 0.6f));
                    Part("Sphere", second, new Vector3(0.5f, 0.6f, -0.05f), new Vector3(0.18f, 0.5f, 0.6f));
                    Part("Cube", accent, new Vector3(0f, 1.1f, 0.52f), new Vector3(0.12f, 0.1f, 0.18f));
                    if (stage >= 3) Part("Sphere", second, new Vector3(0f, 0.45f, -0.6f), new Vector3(0.45f, 0.12f, 0.6f));
                    break;
                case "lion":
                    if (stage >= 2) Part("Cylinder", second, new Vector3(0f, 1.15f, -0.05f), new Vector3(stage >= 3 ? 1.15f : 0.95f, 0.06f, stage >= 3 ? 1.15f : 0.95f), Quaternion.Euler(90f, 0f, 0f));
                    Part("Sphere", main, new Vector3(0f, 0.5f, 0f), new Vector3(0.85f, 0.75f, 1.05f));
                    Part("Sphere", main, new Vector3(0f, 1.15f, 0.15f), Vector3.one * 0.7f);
                    Part("Sphere", accent, new Vector3(-0.25f, 1.45f, 0.1f), Vector3.one * 0.18f);
                    Part("Sphere", accent, new Vector3(0.25f, 1.45f, 0.1f), Vector3.one * 0.18f);
                    Legs(main);
                    break;
                default: // lamb
                    Part("Sphere", main, new Vector3(0f, 0.55f, 0f), new Vector3(1f, 0.85f, 1.15f));
                    Part("Sphere", main, new Vector3(-0.3f, 0.8f, 0.2f), Vector3.one * 0.45f);
                    Part("Sphere", main, new Vector3(0.3f, 0.8f, 0.2f), Vector3.one * 0.45f);
                    Part("Sphere", second, new Vector3(0f, 1.1f, 0.35f), new Vector3(0.55f, 0.6f, 0.55f));
                    Part("Sphere", accent, new Vector3(-0.32f, 1.15f, 0.3f), new Vector3(0.25f, 0.1f, 0.15f));
                    Part("Sphere", accent, new Vector3(0.32f, 1.15f, 0.3f), new Vector3(0.25f, 0.1f, 0.15f));
                    if (stage >= 3)
                    {
                        Part("Sphere", accent, new Vector3(-0.2f, 1.42f, 0.3f), Vector3.one * 0.16f);
                        Part("Sphere", accent, new Vector3(0.2f, 1.42f, 0.3f), Vector3.one * 0.16f);
                    }
                    Legs(second);
                    break;
            }
            // 大眼睛：每一階段都完整可愛（一等不是「弱」）
            float headZ = variant == "lamb" ? 0.6f : 0.5f;
            Part("Sphere", Color.black, new Vector3(-0.13f, 1.2f, headZ), Vector3.one * 0.11f);
            Part("Sphere", Color.black, new Vector3(0.13f, 1.2f, headZ), Vector3.one * 0.11f);
            // 小領袖：光環
            if (stage >= 4) Part("Cylinder", Hex("#FFD54A"), new Vector3(0f, 1.75f, 0f), new Vector3(0.6f, 0.02f, 0.6f));
        }

        void Legs(Color c)
        {
            foreach (var x in new[] { -0.3f, 0.3f })
                foreach (var z in new[] { -0.3f, 0.3f })
                    Part("Cylinder", c, new Vector3(x, 0.12f, z), new Vector3(0.18f, 0.14f, 0.18f));
        }

        readonly Dictionary<Color, Material> _materials = new Dictionary<Color, Material>();

        void Part(string mesh, Color color, Vector3 pos, Vector3 scale, Quaternion? rot = null)
        {
            var go = new GameObject(mesh);
            go.transform.SetParent(_body, false);
            go.transform.localPosition = pos;
            go.transform.localScale = scale;
            go.transform.localRotation = rot ?? Quaternion.identity;
            go.AddComponent<MeshFilter>().sharedMesh = Resources.GetBuiltinResource<Mesh>(mesh + ".fbx");
            if (!_materials.TryGetValue(color, out var mat))
            {
                mat = PaletteMaterial.Flat(color);
                _materials[color] = mat;
            }
            go.AddComponent<MeshRenderer>().sharedMaterial = mat;
        }

        static Color Hex(string hex) => ColorUtility.TryParseHtmlString(hex, out var c) ? c : Color.white;
    }
}
