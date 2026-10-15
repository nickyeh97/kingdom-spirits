using System.Collections.Generic;
using System.Linq;
using SpiritBeast.Core;
using UnityEngine;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// 離線 Demo（展演用，不連平台）：選靈獸 → 選顏色 → 按服事項目 ＋1，看等級、階段與進化 → 一鍵還原到初始。
    /// 規則全部來自 Core（等級＝次數＋1、門檻 0/4/12/24、鼓勵話語），與正式遊戲相同。
    /// </summary>
    public sealed class DemoApp : MonoBehaviour
    {
        const float BeastShare = 0.55f;   // 上方 55% 給靈獸，下方放按鈕

        readonly System.Random _random = new System.Random();
        readonly List<ServiceEntry> _entries = new List<ServiceEntry>();
        ServiceCard _card;
        Encourager _encourager;
        BeastView _beast;
        Camera _camera;
        string _variant = "lamb", _palette = "p1";
        string _headline, _message;

        void Start()
        {
            _camera = Camera.main;
            if (_camera == null) _camera = new GameObject("Main Camera").AddComponent<Camera>();
            _camera.clearFlags = CameraClearFlags.SolidColor;
            _camera.backgroundColor = new Color(0.99f, 0.96f, 0.89f);
            _camera.rect = new Rect(0f, 1f - BeastShare, 1f, BeastShare);
            // 鏡頭固定、框得下最大的小領袖：進化時看得出「長大」
            // 小領袖約 1.63 公尺：頭頂不碰上方按鈕、腳不碰下方色票
            _camera.transform.position = new Vector3(0f, 1.0f, -3.2f);
            _camera.transform.LookAt(new Vector3(0f, 0.95f, 0f));

            _beast = new GameObject("Beast").AddComponent<BeastView>();
            _encourager = new Encourager(null, _random);
            ResetJourney();
        }

        void ResetJourney()
        {
            _entries.Clear();
            _card = new ServiceCard(Catalog.DemoServiceItems, _entries);
            _beast.Show(_variant, _palette, _card.Stage);
            _headline = "回到起點：每一隻靈獸都從這裡開始";
            _message = _encourager.OnOpen();
        }

        void Serve(string item)
        {
            var before = _card;
            _entries.Add(new ServiceEntry(item, null, System.DateTimeOffset.UtcNow));
            _card = new ServiceCard(Catalog.DemoServiceItems, _entries);
            var outcome = new LogOutcome(before, _card, item);
            var name = Catalog.FindVariant(_variant)?.DisplayName ?? _variant;
            _headline = outcome.Evolved
                ? name + " 長大了！現在是「" + GrowthRules.StageName(outcome.StageAfter) + "」"
                : item + " 升到 " + outcome.LevelAfter + " 等！";
            _message = _encourager.AfterLog(outcome, _variant, null);
            if (outcome.Evolved) _beast.Evolve(_variant, _palette, outcome.StageAfter);
            else _beast.Celebrate();
        }

        // ---- 畫面（IMGUI）：以 400 寬的邏輯座標排版 ----

        float _s, _x0;
        GUIStyle _title, _small, _button, _bubble;
        static readonly Color Ink = new Color(0.29f, 0.23f, 0.16f);
        static readonly Color Paper = new Color(0.99f, 0.96f, 0.89f);
        static readonly Color Leaf = new Color(0.55f, 0.78f, 0.49f);

        Rect R(float x, float y, float w, float h) => new Rect(_x0 + x * _s, y * _s, w * _s, h * _s);
        float LogicalHeight => Screen.height / _s;

        void EnsureStyles()
        {
            float width = Mathf.Min(Screen.width, Screen.height * 0.62f);
            float s = width / 400f;
            _x0 = (Screen.width - width) / 2f;
            if (_title != null && Mathf.Approximately(s, _s)) return;
            _s = s;
            var font = Resources.Load<Font>("Fonts/NotoSansTC-Subset");
            GUIStyle Make(GUIStyle from, int size)
            {
                var st = new GUIStyle(from) { fontSize = Mathf.RoundToInt(size * _s), wordWrap = true, alignment = TextAnchor.MiddleCenter };
                if (font != null) st.font = font;
                return st;
            }
            _title = Make(GUI.skin.label, 20);
            _small = Make(GUI.skin.label, 14);
            _button = Make(GUI.skin.button, 14);
            _bubble = Make(GUI.skin.label, 15);
            _title.normal.textColor = _small.normal.textColor = Ink;
            _bubble.normal.textColor = Color.white;
            _bubble.padding = new RectOffset(10, 10, 6, 6);
        }

        void OnGUI()
        {
            EnsureStyles();
            float top = LogicalHeight * BeastShare;
            Fill(new Rect(0, top * _s, Screen.width, Screen.height - top * _s), Paper);
            bool evolving = _beast != null && _beast.Evolving;
            var v = Catalog.FindVariant(_variant);

            // 上方：狀態、選靈獸（英文名）、選顏色
            GUI.Label(R(0, 4, 400, 30), (v?.DisplayName ?? _variant) + " · " + GrowthRules.StageName(_card.Stage), _title);
            GUI.Label(R(0, 30, 400, 22), "服事 " + _card.Total + " 次　·　小領袖靈獸 Demo", _small);
            GUI.enabled = !evolving;
            var variants = Catalog.AvailableVariants.ToList();
            for (int i = 0; i < variants.Count; i++)
            {
                if (Tint(R(70 + i * 90, 56, 82, 34), variants[i].DisplayName, variants[i].Id == _variant ? Leaf : Color.white))
                {
                    _variant = variants[i].Id;
                    _beast.Show(_variant, _palette, _card.Stage);
                }
            }
            for (int i = 0; i < Catalog.Palettes.Count; i++)
            {
                var p = Catalog.Palettes[i];
                var r = R(24 + i * 44, top - 48, 40, 40);
                if (p.Id == _palette) Fill(new Rect(r.x - 3, r.y - 3, r.width + 6, r.height + 6), Ink);
                Fill(r, PaletteMaterial.Hex(p.Main));
                Fill(new Rect(r.x, r.yMax - r.height * 0.3f, r.width * 0.5f, r.height * 0.3f), PaletteMaterial.Hex(p.Secondary));
                Fill(new Rect(r.center.x, r.yMax - r.height * 0.3f, r.width * 0.5f, r.height * 0.3f), PaletteMaterial.Hex(p.Accent));
                if (GUI.Button(r, GUIContent.none, GUIStyle.none))
                {
                    _palette = p.Id;
                    _beast.Show(_variant, _palette, _card.Stage);
                }
            }
            // 點靈獸：跳一下
            if (GUI.Button(R(0, 96, 400, top - 150), GUIContent.none, GUIStyle.none)) _beast.Hop();

            // 下方：鼓勵話語、六個服事項目（＋1）、還原
            float y = top + 8;
            var bubble = R(16, y, 368, 64);
            Fill(bubble, new Color(0.45f, 0.36f, 0.25f, 0.92f));
            GUI.Label(bubble, evolving ? "咦？靈獸發光了……" : _headline + "\n" + _message, _bubble);

            y += 72;
            var rows = _card.Rows.Where(row => !row.Retired).ToList();
            for (int i = 0; i < rows.Count; i++)
            {
                var row = rows[i];
                var r = R(16 + (i % 2) * 188, y + (i / 2) * 50, 180, 44);
                if (Tint(r, row.Item + "\n" + row.Level + " 等　＋1", row.Unexplored ? Color.white : Leaf)) Serve(row.Item);
            }
            y += ((rows.Count + 1) / 2) * 50 + 4;
            if (GUI.Button(R(120, y, 160, 40), "還原到初始", _button)) ResetJourney();
            GUI.enabled = true;
        }

        bool Tint(Rect rect, string text, Color tint)
        {
            var old = GUI.backgroundColor;
            GUI.backgroundColor = tint;
            bool clicked = GUI.Button(rect, text, _button);
            GUI.backgroundColor = old;
            return clicked;
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
