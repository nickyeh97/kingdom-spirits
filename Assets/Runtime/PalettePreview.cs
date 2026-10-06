using System.Collections.Generic;
using System.Linq;
using SpiritBeast.Core;
using UnityEngine;
using UnityEngine.Rendering;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// 美術檢查工具：在 Play 模式把一個靈獸模型以 8 組配色並排顯示，並量測規格（GDD §7.2–7.3）。
    /// 由 Editor 選單「Spirit Beast/配色預覽（選取的模型）」建立；場景裡有它時，GameApp 不會啟動。
    /// Play 中可切換模型：點畫面上的模型按鈕，或在 Project 視窗點選另一個模型（編輯器限定）；
    /// 從 Blender 重新匯出後按「重新載入」即可看到新版。
    /// </summary>
    public sealed class PalettePreview : MonoBehaviour
    {
        /// <summary>目前預覽的模型</summary>
        public GameObject Model;
        /// <summary>可切換的模型（Editor 選單放入同資料夾的模型）</summary>
        public List<GameObject> Models = new List<GameObject>();

        readonly List<GameObject> _clones = new List<GameObject>();
        IReadOnlyList<SpecFinding> _findings = new SpecFinding[0];
        ModelMeasure _measure;
        Camera _camera;
        int _focus = -1;   // -1＝八隻全部；0–7＝單看一組
        bool _turn = true;
        float _facing = 180f;
        float _spacing = 1f;
        int _view;   // 對應著色器 _View：0 正常、1 遮罩顏色、2 遮罩 A、3 不打光
        static readonly string[] ViewNames = { "正常", "遮罩顏色", "遮罩A", "不打光" };
        readonly List<Material> _materials = new List<Material>();
        GUIStyle _style, _label;
        Font _font;

        void Start()
        {
            _camera = Camera.main;
            if (_camera == null) _camera = new GameObject("Main Camera").AddComponent<Camera>();
            _camera.clearFlags = CameraClearFlags.SolidColor;
            _camera.backgroundColor = new Color(0.99f, 0.96f, 0.89f);

            Models.RemoveAll(m => m == null);
            if (Model == null && Models.Count > 0) Model = Models[0];
            if (Model == null)
            {
                _findings = new[] { new SpecFinding(SpecLevel.Error, "沒有指定模型：請在 Project 視窗選取 FBX 後，從選單「Spirit Beast/配色預覽」開啟") };
                return;
            }
            Show(Model);
        }

        /// <summary>換成另一個模型（或重新載入同一個）：清掉舊的 8 隻，重新量測、套色、排版</summary>
        public void Show(GameObject model)
        {
            foreach (var c in _clones) Destroy(c);
            foreach (var m in _materials) Destroy(m);
            _clones.Clear();
            _materials.Clear();
            Model = model;
            if (!Models.Contains(model)) Models.Add(model);

            var shader = Shader.Find("SpiritBeast/PaletteMask");
            // 量測失敗也照樣顯示 8 組配色：檢查是輔助，預覽才是主要用途
            try
            {
                _measure = Measure(Model);
                _findings = ModelSpecRules.Check(_measure);
            }
            catch (System.Exception e)
            {
                _measure = new ModelMeasure { Name = Model.name, Height = 1f, Width = 1f, Depth = 1f };
                _findings = new[] { new SpecFinding(SpecLevel.Error, "量測失敗：" + e.Message) };
            }
            Debug.Log($"[配色預覽] {Model.name}\n" + string.Join("\n", _findings));

            _spacing = Mathf.Max(_measure.Width, _measure.Depth, 0.3f) * 1.4f;
            for (int i = 0; i < Catalog.Palettes.Count; i++)
            {
                var clone = Instantiate(Model, transform);
                clone.name = Model.name + "_" + Catalog.Palettes[i].Id;
                if (shader != null)
                {
                    var mat = ApplyPalette(clone, shader, Catalog.Palettes[i]);
                    mat.SetFloat("_View", _view);   // 換模型時維持目前的診斷顯示模式
                    _materials.Add(mat);
                }
                _clones.Add(clone);
            }
            Layout();
        }

        static bool IsModel(GameObject go) => go != null && go.GetComponentsInChildren<Renderer>(true).Length > 0;

        static Material ApplyPalette(GameObject go, Shader shader, Palette p)
        {
            var mat = new Material(shader) { name = "Palette_" + p.Id };
            mat.SetColor("_Primary", Hex(p.Main));
            mat.SetColor("_Secondary", Hex(p.Secondary));
            mat.SetColor("_Accent", Hex(p.Accent));
            foreach (var r in go.GetComponentsInChildren<Renderer>())
                r.sharedMaterials = Enumerable.Repeat(mat, Mathf.Max(1, r.sharedMaterials.Length)).ToArray();
            return mat;
        }

        /// <summary>
        /// 全部：4 隻一排、上下兩排（第 1–4 組在上），全部面向鏡頭；單看：只留一隻。
        /// 鏡頭距離依寬、高兩個方向都放得下來算。
        /// </summary>
        void Layout()
        {
            if (_measure == null) return;   // 沒指定模型時沒有東西可排
            float h = Mathf.Max(_measure.Height, 0.3f);
            float rowGap = h * 1.35f;
            for (int i = 0; i < _clones.Count; i++)
            {
                _clones[i].SetActive(_focus < 0 || _focus == i);
                _clones[i].transform.localPosition = _focus < 0
                    ? new Vector3((i % 4 - 1.5f) * _spacing, i < 4 ? rowGap : 0f, 0f)
                    : Vector3.zero;
            }
            float width = _focus < 0 ? _spacing * 4f : _spacing;
            float height = _focus < 0 ? rowGap + h : h;
            float tanHalf = Mathf.Tan(_camera.fieldOfView * 0.5f * Mathf.Deg2Rad);
            float dist = Mathf.Max(height * 0.5f / tanHalf, width * 0.5f / (tanHalf * _camera.aspect)) * 1.25f;
            var center = new Vector3(0f, height * 0.5f, 0f);
            _camera.transform.position = center + new Vector3(0f, h * 0.15f, -dist);
            _camera.transform.LookAt(center);
        }

        void Update()
        {
#if UNITY_EDITOR
            // Play 中在 Project 視窗點選另一個模型 → 跟著切換
            var picked = UnityEditor.Selection.activeObject as GameObject;
            if (picked != null && picked != Model && UnityEditor.EditorUtility.IsPersistent(picked) && IsModel(picked))
                Show(picked);
#endif
            float y = _turn ? Time.time * 30f : 0f;
            foreach (var c in _clones) c.transform.localRotation = Quaternion.Euler(0f, _facing + y, 0f);
        }

        // ---- 量測 ----

        static ModelMeasure Measure(GameObject model)
        {
            var go = Instantiate(model);
            try { return MeasureInstance(go, model.name); }
            finally { go.SetActive(false); Destroy(go); }
        }

        static ModelMeasure MeasureInstance(GameObject go, string name)
        {
            go.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
            go.transform.localScale = Vector3.one;
            var m = new ModelMeasure { Name = name };
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
                // 頂點色數值要網格開 Read/Write 才讀得到（編輯器 Play 模式也一樣，會拋 InvalidOperationException）。
                // 沒開就只略過數值檢查；換色在 GPU 上做，不受影響
                if (!mesh.isReadable) { m.MaskReadable = false; continue; }
                foreach (var c in mesh.colors) CountMask(m, c);
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
            // 診斷：全黑時切到「遮罩顏色」——還是全黑＝FBX 頂點色是 0；切到「不打光」有顏色＝光照問題
            if (GUI.Button(new Rect(bx + 172 * s, y, 120 * s, sw), "顯示：" + ViewNames[_view]))
            {
                _view = (_view + 1) % ViewNames.Length;
                foreach (var m in _materials) m.SetFloat("_View", _view);
            }

            // 模型切換：同資料夾的模型各一顆按鈕，目前的加框；「重新載入」給 Blender 重新匯出後用
            float my = y + sw + 8 * s, mx = x;
            for (int i = 0; i < Models.Count; i++)
            {
                if (Models[i] == null) continue;
                var name = Models[i].name;
                var r = new Rect(mx, my, Mathf.Max(90f, name.Length * 9f + 24f) * s, 34 * s);
                if (Models[i] == Model) Fill(new Rect(r.x - 3, r.y - 3, r.width + 6, r.height + 6), Color.black);
                if (GUI.Button(r, name) && Models[i] != Model) Show(Models[i]);
                mx = r.xMax + 8 * s;
            }
            if (Model != null && GUI.Button(new Rect(mx, my, 90 * s, 34 * s), "重新載入")) Show(Model);

            // 規格檢查結果
            float ty = my + 34 * s + 10 * s;
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
