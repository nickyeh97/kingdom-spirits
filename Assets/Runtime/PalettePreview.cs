using System.Collections.Generic;
using System.Linq;
using SpiritBeast.Core;
using Unity.Collections;
using UnityEngine;
using UnityEngine.Rendering;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// 美術檢查工具：在 Play 模式把一個靈獸模型以 8 組配色並排顯示，並量測規格（GDD §7.2–7.3）。
    /// 由 Editor 選單「Spirit Beast/配色預覽（選取的模型）」建立；場景裡有它時，GameApp 不會啟動。
    /// </summary>
    public sealed class PalettePreview : MonoBehaviour
    {
        public GameObject Model;

        readonly List<GameObject> _clones = new List<GameObject>();
        IReadOnlyList<SpecFinding> _findings = new SpecFinding[0];
        ModelMeasure _measure;
        Camera _camera;
        int _focus = -1;   // -1＝八隻全部；0–7＝單看一組
        bool _turn = true;
        float _facing = 180f;
        float _spacing = 1f;
        GUIStyle _style, _label;
        Font _font;

        void Start()
        {
            _camera = Camera.main;
            if (_camera == null) _camera = new GameObject("Main Camera").AddComponent<Camera>();
            _camera.clearFlags = CameraClearFlags.SolidColor;
            _camera.backgroundColor = new Color(0.99f, 0.96f, 0.89f);

            if (Model == null)
            {
                _findings = new[] { new SpecFinding(SpecLevel.Error, "沒有指定模型：請在 Project 視窗選取 FBX 後，從選單「Spirit Beast/配色預覽」開啟") };
                return;
            }

            var shader = Shader.Find("SpiritBeast/PaletteMask");
            _measure = Measure(Model);
            _findings = ModelSpecRules.Check(_measure);
            Debug.Log($"[配色預覽] {Model.name}\n" + string.Join("\n", _findings));

            _spacing = Mathf.Max(_measure.Width, _measure.Depth, 0.3f) * 1.5f;
            for (int i = 0; i < Catalog.Palettes.Count; i++)
            {
                var clone = Instantiate(Model, transform);
                clone.name = Model.name + "_" + Catalog.Palettes[i].Id;
                if (shader != null) ApplyPalette(clone, shader, Catalog.Palettes[i]);
                _clones.Add(clone);
            }
            Layout();
        }

        static void ApplyPalette(GameObject go, Shader shader, Palette p)
        {
            var mat = new Material(shader) { name = "Palette_" + p.Id };
            mat.SetColor("_Primary", Hex(p.Main));
            mat.SetColor("_Secondary", Hex(p.Secondary));
            mat.SetColor("_Accent", Hex(p.Accent));
            foreach (var r in go.GetComponentsInChildren<Renderer>())
                r.sharedMaterials = Enumerable.Repeat(mat, Mathf.Max(1, r.sharedMaterials.Length)).ToArray();
        }

        /// <summary>單看時只顯示一隻並拉近；全部時排成 4×2</summary>
        void Layout()
        {
            for (int i = 0; i < _clones.Count; i++)
            {
                bool show = _focus < 0 || _focus == i;
                _clones[i].SetActive(show);
                var pos = _focus < 0 ? new Vector3((i % 4 - 1.5f) * _spacing, 0f, (i / 4) * _spacing) : Vector3.zero;
                _clones[i].transform.localPosition = pos;
            }
            float h = Mathf.Max(_measure != null ? _measure.Height : 1f, 0.3f);
            float span = _focus < 0 ? _spacing * 4.2f : Mathf.Max(h, _spacing) * 1.6f;
            float dist = span * 0.5f / Mathf.Tan(_camera.fieldOfView * 0.5f * Mathf.Deg2Rad) / Mathf.Max(_camera.aspect, 0.6f);
            var center = new Vector3(0f, h * 0.5f, _focus < 0 ? _spacing * 0.5f : 0f);
            _camera.transform.position = center + new Vector3(0f, h * 0.6f, -dist);
            _camera.transform.LookAt(center);
        }

        void Update()
        {
            float y = _turn ? Time.time * 30f : 0f;
            foreach (var c in _clones) c.transform.localRotation = Quaternion.Euler(0f, _facing + y, 0f);
        }

        // ---- 量測 ----

        static ModelMeasure Measure(GameObject model)
        {
            var go = Instantiate(model);
            go.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
            go.transform.localScale = Vector3.one;
            var m = new ModelMeasure { Name = model.name };
            var materials = new HashSet<Material>();
            Bounds? bounds = null;

            foreach (var r in go.GetComponentsInChildren<Renderer>())
            {
                foreach (var mat in r.sharedMaterials) if (mat != null) materials.Add(mat);
                bounds = bounds.HasValue ? Encapsulate(bounds.Value, r.bounds) : r.bounds;

                // 不用 GetComponent<…>()?.：編輯器裡缺元件時回傳的是「假 null」，?. 擋不住
                Mesh mesh = null;
                if (r is SkinnedMeshRenderer skinned) mesh = skinned.sharedMesh;
                else if (r.TryGetComponent(out MeshFilter filter)) mesh = filter.sharedMesh;
                if (mesh == null) continue;
                m.MeshCount++;
                for (int sub = 0; sub < mesh.subMeshCount; sub++) m.Triangles += (int)(mesh.GetIndexCount(sub) / 3);

                if (!mesh.HasVertexAttribute(VertexAttribute.Color)) { m.MeshesWithoutVertexColor++; continue; }
                if (!mesh.isReadable && !Application.isEditor) { m.MaskReadable = false; continue; }
                // AcquireReadOnlyMeshData 在編輯器裡讀得到沒開 Read/Write 的 FBX 網格
                using (var data = Mesh.AcquireReadOnlyMeshData(mesh))
                {
                    var colors = new NativeArray<Color>(data[0].vertexCount, Allocator.Temp);
                    data[0].GetColors(colors);
                    foreach (var c in colors) CountMask(m, c);
                    colors.Dispose();
                }
            }

            m.MaterialCount = materials.Count;
            if (bounds.HasValue)
            {
                var b = bounds.Value;
                m.Width = b.size.x; m.Height = b.size.y; m.Depth = b.size.z; m.MinY = b.min.y;
            }
            Destroy(go);
            return m;
        }

        static Bounds Encapsulate(Bounds a, Bounds b) { a.Encapsulate(b); return a; }

        static void CountMask(ModelMeasure m, Color c)
        {
            if (c.a > 0.95f)
            {
                if (c.r >= c.g && c.r >= c.b) m.PrimaryVertices++;
                else if (c.g >= c.b) m.SecondaryVertices++;
                else m.AccentVertices++;
            }
            else if (c.a < 0.05f) m.FixedVertices++;
            else m.AmbiguousVertices++;
        }

        static Color Hex(string hex) => ColorUtility.TryParseHtmlString(hex, out var c) ? c : Color.white;

        // ---- 介面 ----

        void OnGUI()
        {
            float s = Mathf.Max(1f, Screen.height / 720f);
            if (_style == null)
            {
                _font = Resources.Load<Font>("Fonts/NotoSansTC-Subset");
                _style = new GUIStyle(GUI.skin.label) { fontSize = Mathf.RoundToInt(15 * s), wordWrap = true };
                _label = new GUIStyle(_style) { alignment = TextAnchor.UpperCenter };
                if (_font != null) { _style.font = _font; _label.font = _font; }
                _style.normal.textColor = _label.normal.textColor = new Color(0.29f, 0.23f, 0.16f);
            }

            float x = 12 * s, y = 10 * s, sw = 44 * s;
            if (GUI.Button(new Rect(x, y, 70 * s, sw), "全部")) { _focus = -1; Layout(); }
            for (int i = 0; i < Catalog.Palettes.Count; i++)
            {
                var r = new Rect(x + (78 + i * 50) * s, y, sw, sw);
                if (_focus == i) Fill(new Rect(r.x - 3, r.y - 3, r.width + 6, r.height + 6), Color.black);
                Fill(r, Hex(Catalog.Palettes[i].Main));
                Fill(new Rect(r.x, r.yMax - r.height * 0.3f, r.width * 0.5f, r.height * 0.3f), Hex(Catalog.Palettes[i].Secondary));
                Fill(new Rect(r.center.x, r.yMax - r.height * 0.3f, r.width * 0.5f, r.height * 0.3f), Hex(Catalog.Palettes[i].Accent));
                if (GUI.Button(r, GUIContent.none, GUIStyle.none)) { _focus = i; Layout(); }
            }
            float bx = x + (78 + Catalog.Palettes.Count * 50) * s;
            if (GUI.Button(new Rect(bx, y, 80 * s, sw), _turn ? "停止轉動" : "轉動")) _turn = !_turn;
            if (GUI.Button(new Rect(bx + 86 * s, y, 80 * s, sw), "轉向 180°")) _facing = (_facing + 180f) % 360f;

            // 規格檢查結果
            float ty = y + sw + 12 * s;
            GUI.Label(new Rect(x, ty, 600 * s, 24 * s), "規格檢查：" + (Model != null ? Model.name : "（未指定）"), _style);
            foreach (var f in _findings)
            {
                ty += 24 * s;
                var old = GUI.contentColor;
                GUI.contentColor = f.Level == SpecLevel.Error ? new Color(0.8f, 0.1f, 0.1f) : f.Level == SpecLevel.Warning ? new Color(0.75f, 0.45f, 0f) : new Color(0.2f, 0.5f, 0.2f);
                GUI.Label(new Rect(x, ty, 760 * s, 24 * s), f.ToString(), _style);
                GUI.contentColor = old;
            }

            // 每隻下方標配色名稱
            for (int i = 0; i < _clones.Count; i++)
            {
                if (!_clones[i].activeSelf) continue;
                var sp = _camera.WorldToScreenPoint(_clones[i].transform.position);
                if (sp.z <= 0) continue;
                var p = Catalog.Palettes[i];
                GUI.Label(new Rect(sp.x - 70 * s, Screen.height - sp.y + 6 * s, 140 * s, 24 * s), p.Id + " " + p.Name, _label);
            }
        }

        static void Fill(Rect rect, Color color)
        {
            var old = GUI.color;
            GUI.color = color;
            GUI.DrawTexture(rect, Texture2D.whiteTexture);
            GUI.color = old;
        }
    }
}
