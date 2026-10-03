using System.Collections.Generic;
using SpiritBeast.Core;
using UnityEngine;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// G1 占位靈獸：用內建幾何體拼出三種造型，依階段放大並加上特徵。
    /// G2 會換成正式模型（docs/ART_PIPELINE.md），對外介面維持 Show／Hop／Celebrate。
    /// </summary>
    public sealed class BeastView : MonoBehaviour
    {
        static readonly float[] StageScale = { 0.75f, 0.9f, 1.05f, 1.2f };

        Transform _body;
        Shader _shader;
        float _hopTime = -1f;
        float _spinTime = -1f;
        float _evolveTime = -1f;
        string _pendingVariant, _pendingPalette;
        int _pendingStage;

        public bool Evolving => _evolveTime >= 0f;

        void Awake()
        {
            _shader = Shader.Find("Legacy Shaders/Diffuse");
            if (_shader == null) _shader = Shader.Find("Sprites/Default");
        }

        public void Show(string variant, string palette, int stage)
        {
            if (_body != null) Destroy(_body.gameObject);
            _body = new GameObject("Body").transform;
            _body.SetParent(transform, false);
            Build(variant, Catalog.FindPalette(palette), stage);
            _body.localScale = Vector3.one * StageScale[Mathf.Clamp(stage, 1, 4) - 1];
        }

        public void Hop() => _hopTime = 0f;

        public void Celebrate() { _hopTime = 0f; _spinTime = 0f; }

        /// <summary>進化過場：先放大發光，再換成新階段的樣子（約 3 秒）</summary>
        public void Evolve(string variant, string palette, int newStage)
        {
            _pendingVariant = variant; _pendingPalette = palette; _pendingStage = newStage;
            _evolveTime = 0f;
        }

        void Update()
        {
            if (_body == null) return;
            float t = Time.time;
            float y = Mathf.Sin(t * 2f) * 0.05f;
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
            _body.localRotation = Quaternion.Euler(0f, 200f + spin, 0f);
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
            if (!_materials.TryGetValue(color, out var mat) && _shader != null)
            {
                mat = new Material(_shader) { color = color };
                _materials[color] = mat;
            }
            go.AddComponent<MeshRenderer>().sharedMaterial = mat;
        }

        static Color Hex(string hex) => ColorUtility.TryParseHtmlString(hex, out var c) ? c : Color.white;
    }
}
