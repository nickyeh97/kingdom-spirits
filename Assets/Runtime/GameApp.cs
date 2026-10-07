using System;
using System.Collections;
using System.Linq;
using SpiritBeast.Core;
using UnityEngine;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// G1 核心迴圈（GDD §4）：S0 載入 → S1 第一次相遇 → S2 靈獸之家 ⇄ S3 服事卡／S4 換裝扮／S5 登錄服事 → S6 慶祝。
    /// 介面是 G1 的占位版（IMGUI），G2/G3 換成正式 UGUI 與美術；流程與規則都在 Core，畫面只負責呈現。
    /// 遊戲內沒有任何文字輸入（手機 Web 的中文輸入體驗差），要打字的都在牧區平台。
    /// </summary>
    public sealed class GameApp : MonoBehaviour
    {
#if UNITY_WEBGL && !UNITY_EDITOR
        [System.Runtime.InteropServices.DllImport("__Internal")]
        static extern string SB_TakeAuthFragment();
#else
        // 編輯器 Play 模式：以環境變數 SPIRIT_DEV_FRAGMENT 提供片段（見 docs/DEVELOPMENT.md）
        static string SB_TakeAuthFragment() => Environment.GetEnvironmentVariable("SPIRIT_DEV_FRAGMENT") ?? "";
#endif

        enum Page { Loading, Error, FirstMeet, Home, Card, Wardrobe, Log, Celebrate }

        string _fragment;   // 由 Create 取走一次後交給這裡（jslib 取一次即清空）

        Page _page = Page.Loading;
        string _error;
        string _notice;
        bool _busy;

        SupabaseClient _api;
        Guid _childId;
        string _childName;
        ServiceCard _card;
        BeastProfile _profile;
        Encourager _encourager;
        string _bubble;
        BeastView _beast;
        Camera _camera;
        readonly System.Random _random = new System.Random();

        // S1／S4 挑選中的外觀
        string _pickVariant, _pickPalette;
        // S5 登錄步驟：0 家長確認 → 1 選項目 → 2 選果子 → 3 確認
        int _logStep;
        bool _parentConfirmed;
        string _pickItem, _pickFruit;
        // S6
        LogOutcome _outcome;
        string _celebrateMessage, _invitation;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Create()
        {
            // 美術檢查用的配色預覽場景不啟動遊戲
            if (FindAnyObjectByType<PalettePreview>() != null) return;
            var fragment = SB_TakeAuthFragment();
            if (DemoMode.Wants(fragment, Application.isEditor))
            {
                new GameObject(nameof(DemoApp)).AddComponent<DemoApp>();
                return;
            }
            new GameObject(nameof(GameApp)).AddComponent<GameApp>()._fragment = fragment;
        }

        void Start()
        {
            SetupCamera();
            _beast = new GameObject("Beast").AddComponent<BeastView>();

            var auth = AuthFragment.Parse(_fragment);
            var configAsset = Resources.Load<TextAsset>("supabase");
            var config = SupabaseConfig.Parse(configAsset != null ? configAsset.text : null);
            if (!auth.IsValid) { Fail("請從牧區平台的「我的 → 小領袖靈獸」開啟"); return; }
            if (config == null) { Fail("遊戲設定尚未完成，請通知同工"); return; }

            _childId = auth.ChildId;
            _api = new SupabaseClient(config, auth.AccessToken);
            StartCoroutine(LoadAll());
        }

        void SetupCamera()
        {
            _camera = Camera.main;
            if (_camera == null) _camera = new GameObject("Main Camera").AddComponent<Camera>();
            _camera.clearFlags = CameraClearFlags.SolidColor;
            _camera.backgroundColor = new Color(0.99f, 0.96f, 0.89f);
            _camera.transform.position = new Vector3(0f, 1.2f, -5f);
            _camera.transform.LookAt(new Vector3(0f, 0.85f, 0f));
        }

        // ---- 資料 ----

        IEnumerator LoadAll()
        {
            string child = null, items = null, entries = null, profile = null;
            long failed = -1;
            yield return _api.Send(SupabaseApi.GetChild(_childId), s => child = s, c => failed = c);
            if (failed < 0) yield return _api.Send(SupabaseApi.GetItems(), s => items = s, c => failed = c);
            if (failed < 0) yield return _api.Send(SupabaseApi.GetEntries(_childId), s => entries = s, c => failed = c);
            if (failed < 0) yield return _api.Send(SupabaseApi.GetProfile(_childId), s => profile = s, c => failed = c);
            if (failed >= 0) { Fail(SupabaseApi.DescribeError(failed)); yield break; }

            try
            {
                _childName = SupabaseApi.ParseChildName(child);
                _card = new ServiceCard(SupabaseApi.ParseItems(items), SupabaseApi.ParseEntries(entries));
                _profile = SupabaseApi.ParseProfile(profile);
            }
            catch (Exception)
            {
                Fail("資料讀取失敗，請回到平台重新開啟");
                yield break;
            }
            // RLS 擋下（不是自己的孩子、帳號未審核）與查無此人，回應都是空陣列
            if (_childName == null) { Fail("找不到這位孩子的資料，請回到平台重新開啟"); yield break; }

            _encourager = new Encourager(_profile != null ? _profile.Encouragements : null, _random);
            if (_profile == null)
            {
                _pickVariant = Catalog.AvailableVariants.First().Id;
                _pickPalette = Catalog.Palettes[0].Id;
                Go(Page.FirstMeet);
            }
            else GoHome();
        }

        IEnumerator SaveLook()
        {
            _busy = true;
            long failed = -1;
            yield return _api.Send(SupabaseApi.UpsertProfile(_childId, _pickVariant, _pickPalette), _ => { }, c => failed = c);
            _busy = false;
            if (failed >= 0) { _notice = SupabaseApi.DescribeError(failed); yield break; }
            _profile = new BeastProfile(_pickVariant, _pickPalette,
                _profile != null ? _profile.Encouragements : new string[0]);
            GoHome();
        }

        IEnumerator SaveLog()
        {
            _busy = true;
            string json = null;
            long failed = -1;
            yield return _api.Send(SupabaseApi.InsertEntry(_childId, _pickItem, _pickFruit), s => json = s, c => failed = c);
            _busy = false;
            if (failed >= 0) { _notice = SupabaseApi.DescribeError(failed); yield break; }

            ServiceEntry saved = null;
            try { saved = SupabaseApi.ParseEntries(json).FirstOrDefault(); } catch (Exception) { }
            if (saved == null) saved = new ServiceEntry(_pickItem, _pickFruit, DateTimeOffset.UtcNow);

            var before = _card;
            _card = _card.With(saved);
            _outcome = new LogOutcome(before, _card, _pickItem);
            _celebrateMessage = _encourager.AfterLog(_outcome, _profile.Variant, _pickFruit);
            _invitation = _encourager.Invitation(_card);
            if (_outcome.Evolved) _beast.Evolve(_profile.Variant, _profile.Palette, _outcome.StageAfter);
            else _beast.Celebrate();
            Go(Page.Celebrate);
        }

        // ---- 導覽 ----

        void Fail(string message)
        {
            _error = message;
            Go(Page.Error);
        }

        void GoHome()
        {
            _beast.Show(_profile.Variant, _profile.Palette, _card.Stage);
            _bubble = _encourager.OnOpen();
            Go(Page.Home);
        }

        void Go(Page page)
        {
            _page = page;
            _notice = null;
            if (page == Page.FirstMeet || page == Page.Wardrobe) ShowPreview();
            // 文字多的頁面讓出畫面給清單；靈獸永遠在上方
            float beastShare = page == Page.Card || page == Page.Log ? 0.3f : page == Page.Error ? 0f : 0.45f;
            _camera.enabled = beastShare > 0f;
            if (beastShare > 0f) _camera.rect = new Rect(0f, 1f - beastShare, 1f, beastShare);
            _beast.gameObject.SetActive(beastShare > 0f && page != Page.Loading);
        }

        void ShowPreview() =>
            _beast.Show(_pickVariant, _pickPalette, _page == Page.FirstMeet || _card == null ? 1 : _card.Stage);

        // ---- 畫面（IMGUI 占位版）----

        float _s, _x0, _builtScale;
        Font _font;
        GUIStyle _title, _text, _small, _button, _bubbleStyle;
        static readonly Color Ink = new Color(0.29f, 0.23f, 0.16f);
        static readonly Color Paper = new Color(0.99f, 0.96f, 0.89f);
        static readonly Color Leaf = new Color(0.55f, 0.78f, 0.49f);

        /// <summary>以 400 寬的邏輯座標排版，換算成實際像素（字型直接用實際大小算繪，不會糊）</summary>
        Rect R(float x, float y, float w, float h) => new Rect(_x0 + x * _s, y * _s, w * _s, h * _s);
        float LogicalHeight => Screen.height / _s;
        float BeastBottom => _camera != null && _camera.enabled ? LogicalHeight * _camera.rect.height : 0f;

        void EnsureStyles()
        {
            float width = Mathf.Min(Screen.width, Screen.height * 0.62f);
            _s = width / 400f;
            _x0 = (Screen.width - width) / 2f;
            if (_title != null && Mathf.Approximately(_builtScale, _s)) return;
            _builtScale = _s;
            if (_font == null) _font = Resources.Load<Font>("Fonts/NotoSansTC-Subset");

            GUIStyle Make(GUIStyle from, int size, TextAnchor anchor)
            {
                var st = new GUIStyle(from) { fontSize = Mathf.RoundToInt(size * _s), wordWrap = true, alignment = anchor, richText = false };
                if (_font != null) st.font = _font;
                return st;
            }
            _title = Make(GUI.skin.label, 22, TextAnchor.MiddleCenter);
            _text = Make(GUI.skin.label, 17, TextAnchor.MiddleLeft);
            _small = Make(GUI.skin.label, 14, TextAnchor.MiddleCenter);
            _bubbleStyle = Make(GUI.skin.box, 17, TextAnchor.MiddleCenter);
            _button = Make(GUI.skin.button, 18, TextAnchor.MiddleCenter);
            foreach (var st in new[] { _title, _text, _small }) st.normal.textColor = Ink;
            _bubbleStyle.normal.textColor = Color.white;
            _bubbleStyle.padding = new RectOffset(12, 12, 10, 10);
        }

        void OnGUI()
        {
            EnsureStyles();
            float top = BeastBottom;
            Fill(new Rect(0, top * _s, Screen.width, Screen.height - top * _s), Paper);
            GUI.enabled = !_busy;

            switch (_page)
            {
                case Page.Loading: DrawLoading(); break;
                case Page.Error: DrawError(); break;
                case Page.FirstMeet: DrawPicker(true); break;
                case Page.Home: DrawHome(top); break;
                case Page.Card: DrawCard(top); break;
                case Page.Wardrobe: DrawPicker(false); break;
                case Page.Log: DrawLog(top); break;
                case Page.Celebrate: DrawCelebrate(top); break;
            }

            GUI.enabled = true;
            if (_busy) GUI.Label(R(0, LogicalHeight - 130, 400, 30), "儲存中…", _small);
            if (_notice != null) GUI.Label(R(16, LogicalHeight - 130, 368, 40), _notice, _small);
        }

        void DrawLoading()
        {
            GUI.Label(R(0, LogicalHeight / 2 - 30, 400, 60), "靈獸準備中…", _title);
        }

        void DrawError()
        {
            GUI.Label(R(24, LogicalHeight / 2 - 80, 352, 100), _error, _title);
            GUI.Label(R(24, LogicalHeight / 2 + 30, 352, 60), "可以關掉這個頁面，回到牧區平台再開一次。", _small);
        }

        void DrawHome(float top)
        {
            var v = Catalog.FindVariant(_profile.Variant);
            GUI.Label(R(0, 8, 400, 34), (v != null ? v.DisplayName : _profile.Variant) + " · " + GrowthRules.StageName(_card.Stage), _title);
            GUI.Label(R(0, 40, 400, 24), _childName + " 的靈獸", _small);
            // 點靈獸：跳一下（沒有其他玩法）
            if (GUI.Button(R(0, 64, 400, top - 70), GUIContent.none, GUIStyle.none)) _beast.Hop();

            Bubble(R(24, top + 16, 352, 120), _bubble);

            float y = LogicalHeight - 84;
            if (GUI.Button(R(16, y, 116, 60), "服事卡", _button)) Go(Page.Card);
            if (GUI.Button(R(142, y, 116, 60), "換裝扮", _button))
            {
                _pickVariant = _profile.Variant;
                _pickPalette = _profile.Palette;
                Go(Page.Wardrobe);
            }
            if (Colored(R(268, y, 116, 60), "＋1 服事", Leaf))
            {
                _logStep = 0; _parentConfirmed = false; _pickItem = null; _pickFruit = null;
                Go(Page.Log);
            }
        }

        void DrawCard(float top)
        {
            GUI.Label(R(0, 8, 400, 34), "服事卡", _title);
            float y = top + 12;
            foreach (var row in _card.Rows)
            {
                GUI.Label(R(24, y, 220, 30), row.Item + (row.Retired ? "（已停用）" : ""), _text);
                var right = row.Unexplored ? "1 等 · 等你來探索" : row.Level + " 等";
                var st = new GUIStyle(_text) { alignment = TextAnchor.MiddleRight };
                GUI.Label(R(200, y, 176, 30), right, st);
                y += 32;
            }
            y += 10;
            GUI.Label(R(24, y, 352, 28), "最近的服事", _text);
            y += 30;
            var recent = _card.Recent(10);
            if (recent.Count == 0) GUI.Label(R(24, y, 352, 26), "還沒有紀錄，第一次服事就從這裡開始。", _small);
            foreach (var e in recent)
            {
                if (y > LogicalHeight - 110) break;
                GUI.Label(R(24, y, 352, 26), DisplayText.Date(e.CreatedAt) + "　" + e.Item + (e.Fruit != null ? " · " + e.Fruit : ""), _small);
                y += 26;
            }
            if (GUI.Button(R(130, LogicalHeight - 76, 140, 56), "回到靈獸", _button)) GoHome();
        }

        void DrawPicker(bool first)
        {
            float top = BeastBottom;
            GUI.Label(R(0, 8, 400, 34), first ? "天父為你預備了一位夥伴" : "換裝扮", _title);
            if (first) GUI.Label(R(0, 40, 400, 24), _childName + "，選一位陪你一起長大的靈獸吧", _small);

            float y = top + 14;
            var variants = Catalog.AvailableVariants.ToList();
            float w = 352f / variants.Count;
            for (int i = 0; i < variants.Count; i++)
            {
                bool on = variants[i].Id == _pickVariant;
                // 靈獸名稱一律英文顯示（組長裁決 2026-09-30）
                if (Colored(R(24 + i * w, y, w - 8, 56), variants[i].DisplayName, on ? Leaf : Color.white))
                {
                    _pickVariant = variants[i].Id;
                    ShowPreview();
                }
            }

            y += 76;
            GUI.Label(R(24, y, 352, 26), "選顏色", _text);
            y += 30;
            for (int i = 0; i < Catalog.Palettes.Count; i++)
            {
                var p = Catalog.Palettes[i];
                var rect = R(24 + (i % 4) * 88, y + (i / 4) * 62, 80, 54);
                if (p.Id == _pickPalette) Fill(new Rect(rect.x - 4, rect.y - 4, rect.width + 8, rect.height + 8), Ink);
                Fill(rect, ColorUtility.TryParseHtmlString(p.Main, out var c) ? c : Color.white);
                if (GUI.Button(rect, GUIContent.none, GUIStyle.none))
                {
                    _pickPalette = p.Id;
                    ShowPreview();
                }
            }

            float by = LogicalHeight - 84;
            if (first)
            {
                if (Colored(R(100, by, 200, 60), "就是你了！", Leaf)) StartCoroutine(SaveLook());
            }
            else
            {
                if (GUI.Button(R(40, by, 150, 60), "取消", _button)) GoHome();
                if (Colored(R(210, by, 150, 60), "儲存", Leaf)) StartCoroutine(SaveLook());
            }
        }

        void DrawLog(float top)
        {
            GUI.Label(R(0, 8, 400, 34), "＋1 服事", _title);
            float y = top + 14;
            switch (_logStep)
            {
                case 0:
                    // 家長守門：只是提醒（UX），真正的邊界是資料庫 RLS——只有綁定的家長帳號寫得進去
                    GUI.Label(R(24, y, 352, 80), "請家長確認：紙本服事卡上已經有老師的簽名。", _text);
                    if (Colored(R(24, y + 90, 352, 64), _parentConfirmed ? "已確認：老師簽過名了" : "我是家長，已看到老師的簽名",
                            _parentConfirmed ? Leaf : Color.white))
                        _parentConfirmed = !_parentConfirmed;
                    GUI.enabled = !_busy && _parentConfirmed;
                    if (GUI.Button(R(210, LogicalHeight - 84, 150, 60), "下一步", _button)) _logStep = 1;
                    GUI.enabled = !_busy;
                    break;
                case 1:
                    GUI.Label(R(24, y, 352, 30), "這次服事的項目是？", _text);
                    var items = _card.LoggableItems;
                    if (items.Count == 0) GUI.Label(R(24, y + 40, 352, 60), "目前沒有可登錄的服事項目，請通知同工。", _small);
                    for (int i = 0; i < items.Count; i++)
                    {
                        if (GUI.Button(R(24 + (i % 2) * 180, y + 40 + (i / 2) * 66, 172, 58), items[i], _button))
                        {
                            _pickItem = items[i];
                            _logStep = 2;
                        }
                    }
                    break;
                case 2:
                    GUI.Label(R(24, y, 352, 30), "這次服事，你嘗到哪一顆果子？", _text);
                    for (int i = 0; i < Catalog.Fruits.Count; i++)
                    {
                        if (GUI.Button(R(24 + (i % 3) * 120, y + 40 + (i / 3) * 62, 112, 54), Catalog.Fruits[i].Name, _button))
                        {
                            _pickFruit = Catalog.Fruits[i].Name;
                            _logStep = 3;
                        }
                    }
                    if (GUI.Button(R(130, y + 236, 140, 50), "跳過", _button)) { _pickFruit = null; _logStep = 3; }
                    break;
                case 3:
                    GUI.Label(R(24, y, 352, 30), "要記下這一次服事嗎？", _text);
                    Bubble(R(24, y + 40, 352, 80), _pickItem + (_pickFruit != null ? " · " + _pickFruit : ""));
                    if (GUI.Button(R(40, y + 136, 150, 54), "上一步", _button)) _logStep = 2;
                    if (Colored(R(210, y + 136, 150, 54), "儲存", Leaf)) StartCoroutine(SaveLog());
                    break;
            }
            if (GUI.Button(R(40, LogicalHeight - 84, 150, 60), "取消", _button)) GoHome();
        }

        void DrawCelebrate(float top)
        {
            if (_beast.Evolving)
            {
                GUI.Label(R(0, top + 40, 400, 60), "咦？靈獸發光了……", _title);
                return;
            }
            var v = Catalog.FindVariant(_profile.Variant);
            var name = v != null ? v.DisplayName : _profile.Variant;
            var headline = _outcome.Evolved
                ? name + " 長大了！現在是「" + GrowthRules.StageName(_outcome.StageAfter) + "」"
                : _outcome.Item + " 升到 " + _outcome.LevelAfter + " 等！";
            GUI.Label(R(0, 8, 400, 40), headline, _title);
            Bubble(R(24, top + 16, 352, 120), _celebrateMessage);
            if (_invitation != null) GUI.Label(R(24, top + 146, 352, 50), _invitation, _small);
            if (Colored(R(130, LogicalHeight - 84, 140, 60), "好！", Leaf)) GoHome();
        }

        // ---- 小工具 ----

        void Bubble(Rect rect, string text)
        {
            Fill(rect, new Color(0.45f, 0.36f, 0.25f, 0.92f));
            GUI.Label(rect, text, _bubbleStyle);
        }

        bool Colored(Rect rect, string text, Color tint)
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
