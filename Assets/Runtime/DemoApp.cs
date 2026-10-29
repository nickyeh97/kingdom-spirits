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
            _camera.transform.LookAt(LookAt);
            // 上下滑動的基準：目前的仰角與距離（之後以這個角度為中心，上下各 30°）
            var offset = _camera.transform.position - LookAt;
            _basePitch = Mathf.Asin(offset.y / offset.magnitude) * Mathf.Rad2Deg;
            _distance = offset.magnitude;
            RenderStyle.Init(_camera);

            _beast = new GameObject("Beast").AddComponent<BeastView>();
            _encourager = new Encourager(null, _random);
            ResetJourney();
            Render();
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

        // ---- 滑動轉動 ----

        static readonly Vector3 LookAt = new Vector3(0f, 0.95f, 0f);
        const float PitchRange = 30f;
        float _basePitch, _pitch, _distance;

        /// <summary>delta：手指位移（像素）。滑過整個螢幕寬＝轉一圈；上下滑過螢幕高的一半＝30°</summary>
        void Orbit(Vector2 delta)
        {
            if (_beast.Evolving) return;
            _beast.Yaw -= delta.x / Screen.width * 360f;
            _pitch = Mathf.Clamp(_pitch - delta.y / Screen.height * 120f, -PitchRange, PitchRange);
            float a = (_basePitch + _pitch) * Mathf.Deg2Rad;
            _camera.transform.position = LookAt + new Vector3(0f, Mathf.Sin(a), -Mathf.Cos(a)) * _distance;
            _camera.transform.LookAt(LookAt);
        }

        // ---- 畫面（UGUI）：以 400 寬的邏輯座標排版（UiKit）----

        RectTransform _column, _root, _page, _background;
        bool _wasEvolving;
        Vector2Int _screen;
        float _height;

        void Update()
        {
            // 進化過場開始／結束、螢幕轉向時重畫（其他時候只在按鈕觸發後重畫）
            bool evolving = _beast != null && _beast.Evolving;
            var screen = new Vector2Int(Screen.width, Screen.height);
            // 畫布第一個影格的尺寸可能還沒算好：欄的高度一變就重畫
            bool resized = _column != null && Mathf.Abs(_column.rect.height - _height) > 0.5f;
            if (evolving != _wasEvolving || screen != _screen || resized) Render();
        }

        void Render()
        {
            if (_column == null) _column = UiKit.CreateCanvas("DemoUI", out _root);
            if (_page != null) Destroy(_page.gameObject);
            if (_background != null) Destroy(_background.gameObject);
            _page = UiKit.Group(_column, "Page");
            // 底色另放一層、橫跨整個畫面寬度（欄只有 400 寬），放在最底下
            _background = UiKit.Group(_root, "Background");
            _background.SetAsFirstSibling();
            _screen = new Vector2Int(Screen.width, Screen.height);
            bool evolving = _wasEvolving = _beast != null && _beast.Evolving;

            float height = _height = UiKit.Height(_column);
            float top = height * BeastShare;
            // 下方的紙色底（上方是 3D 靈獸）
            UiKit.Band(_background, UiKit.Paper, 0f, 1f - BeastShare);
            var v = Catalog.FindVariant(_variant);
            var p = _page;

            // 上方：狀態、選靈獸（英文名）、選顏色、渲染模式
            UiKit.Label(p, (v?.DisplayName ?? _variant) + " · " + GrowthRules.StageName(_card.Stage), 20, 0, 4, 400, 30);
            UiKit.Label(p, "服事 " + _card.Total + " 次　·　小領袖靈獸 Demo", 14, 0, 30, 400, 22);
            UiKit.Button(p, "渲染：" + RenderStyle.Label, 296, 4, 100, 26, () => { RenderStyle.Toggle(); Render(); }, size: 12);
            // 點靈獸：跳一下（放在選單按鈕下面，避免擋到按鈕）
            // 點一下＝跳；左右滑＝轉靈獸（看每個角度）；上下滑＝鏡頭繞著靈獸上下轉（上下各 30°）
            UiKit.Swipe(p, 0, 96, 400, top - 150, () => _beast.Hop(), Orbit);

            var variants = Catalog.AvailableVariants.ToList();
            for (int i = 0; i < variants.Count; i++)
            {
                var id = variants[i].Id;
                UiKit.Button(p, variants[i].DisplayName, 70 + i * 90, 56, 82, 34, () =>
                {
                    _variant = id;
                    _beast.Show(_variant, _palette, _card.Stage);
                    Render();
                }, id == _variant ? UiKit.Leaf : Color.white, interactable: !evolving);
            }
            for (int i = 0; i < Catalog.Palettes.Count; i++)
            {
                var pal = Catalog.Palettes[i];
                UiKit.Swatch(p, pal, pal.Id == _palette, 24 + i * 44, top - 48, 40, 40, () =>
                {
                    if (_beast.Evolving) return;
                    _palette = pal.Id;
                    _beast.Show(_variant, _palette, _card.Stage);
                    Render();
                });
            }

            // 下方：鼓勵話語、六個服事項目（＋1）、還原
            float y = top + 8;
            UiKit.Bubble(p, evolving ? "咦？靈獸發光了……" : _headline + "\n" + _message, 16, y, 368, 64, 15);
            y += 72;
            var rows = _card.Rows.Where(row => !row.Retired).ToList();
            for (int i = 0; i < rows.Count; i++)
            {
                var row = rows[i];
                UiKit.Button(p, row.Item + "\n" + row.Level + " 等　＋1", 16 + (i % 2) * 188, y + (i / 2) * 50, 180, 44,
                    () => { Serve(row.Item); Render(); }, row.Unexplored ? Color.white : UiKit.Leaf, 13,
                    icon: IconPath.Service(row.Item), interactable: !evolving);
            }
            y += ((rows.Count + 1) / 2) * 50 + 4;
            UiKit.Button(p, "還原到初始", 120, y, 160, 40, () => { ResetJourney(); Render(); }, interactable: !evolving);
        }
    }
}
