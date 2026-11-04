using System;
using System.Collections;
using System.Linq;
using SpiritBeast.Core;
using UnityEngine;
using UnityEngine.UI;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// G1 核心迴圈（GDD §4）：S0 載入 → S1 第一次相遇 → S2 靈獸之家 ⇄ S3 服事卡／S4 換裝扮／S5 登錄服事 → S6 慶祝。
    /// 介面用 UGUI（UiKit；G2 由 IMGUI 改過來）；流程與規則都在 Core，畫面只負責呈現。
    /// 遊戲內沒有任何文字輸入（手機 Web 的中文輸入體驗差），要打字的都在牧區平台。
    /// </summary>
    public sealed class GameApp : MonoBehaviour
    {
#if UNITY_WEBGL && !UNITY_EDITOR
        [System.Runtime.InteropServices.DllImport("__Internal")]
        static extern string SB_TakeAuthFragment();
        [System.Runtime.InteropServices.DllImport("__Internal")]
        static extern void SB_BackToPlatform();
#else
        // 編輯器 Play 模式：以環境變數 SPIRIT_DEV_FRAGMENT 提供片段（見 docs/DEVELOPMENT.md）
        static string SB_TakeAuthFragment() => Environment.GetEnvironmentVariable("SPIRIT_DEV_FRAGMENT") ?? "";
        static void SB_BackToPlatform() => Debug.Log("[遊戲] 回到牧區平台（網頁版才會換頁）");
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

        // S1／S4 挑選中的外觀；換裝扮另有「背景」分頁（背景、渲染風格：存在這台裝置，按儲存才算數）
        string _pickVariant, _pickPalette, _pickBackdrop;
        RenderMode _pickStyle;
        int _wardrobeTab;
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
            BackgroundMusic.Init();
            _beast = new GameObject("Beast").AddComponent<BeastView>();
            Render();   // 「靈獸準備中…」

            var auth = AuthFragment.Parse(_fragment);
            // 測試資料庫：本機放 Resources/supabase_test.json（不進版控）就改連它，正式的 supabase.json 不用動
            var configAsset = Resources.Load<TextAsset>("supabase_test");
            if (configAsset == null) configAsset = Resources.Load<TextAsset>("supabase");
            var config = SupabaseConfig.Parse(configAsset != null ? configAsset.text : null);
            if (!auth.IsValid) { Fail("請從牧區平台的「我的 → 小領袖靈獸」開啟"); return; }
            if (config == null)
            {
                // 給開發者看的原因（家長只看到下面那句）：用了哪個檔、為什麼不能用
                var file = configAsset == null ? "找不到 Resources/supabase.json"
                    : "Resources/" + configAsset.name + ".json 的 url／anonKey 格式不對或仍是範本值";
                Debug.LogError("[設定] 連線設定無法使用：" + file);
                Fail("遊戲設定尚未完成，請通知同工");
                return;
            }

            // 連到哪個資料庫（只有網址）：本機測試時拿到 401 先看這行——平台與遊戲要連同一個專案
            Debug.Log("[設定] 連線到 " + config.Url + "（Resources/" + configAsset.name + ".json）");
            _childId = auth.ChildId;
            _api = new SupabaseClient(config, auth.AccessToken);
            StartCoroutine(LoadAll());
        }

        void SetupCamera()
        {
            _camera = Camera.main;
            if (_camera == null) _camera = new GameObject("Main Camera").AddComponent<Camera>();
            _camera.clearFlags = CameraClearFlags.SolidColor;
            // 鏡頭固定在框得下小領袖的距離（進化時看得出長大）；2026-11-01 組長：原本 5 公尺太遠、靈獸太小。
            // 2.6 公尺＋靈獸畫面延伸到對話框：每公尺約 146 個邏輯像素（原本 50），小領袖頭頂仍在標題列下面
            _camera.transform.position = new Vector3(0f, 1.0f, -2.6f);
            _camera.transform.LookAt(LookAt);
            var offset = _camera.transform.position - LookAt;
            _basePitch = Mathf.Asin(offset.y / offset.magnitude) * Mathf.Rad2Deg;
            _distance = offset.magnitude;
            // 渲染風格（卡通／光影）與背景：孩子在「換裝扮 → 背景」選，記在這台裝置
            RenderStyle.Init(_camera);
            _backdrop = Backdrop.Load();
            ApplyBackdrop(Shown());
        }

        // ---- 拖拉視角（跟 Demo 一樣）：左右滑＝轉靈獸，上下滑＝鏡頭以目前角度為中心上下各 30° ----
        static readonly Vector3 LookAt = new Vector3(0f, 0.8f, 0f);
        const float PitchRange = 30f;
        float _basePitch, _pitch, _distance;

        void Orbit(Vector2 delta)
        {
            Touched();
            if (_beast.Evolving) return;
            _beast.Yaw -= delta.x / Screen.width * 360f;
            _pitch = Mathf.Clamp(_pitch - delta.y / Screen.height * 120f, -PitchRange, PitchRange);
            float a = (_basePitch + _pitch) * Mathf.Deg2Rad;
            _camera.transform.position = LookAt + new Vector3(0f, Mathf.Sin(a), -Mathf.Cos(a)) * _distance;
            _camera.transform.LookAt(LookAt);
        }

        // ---- 背景與渲染風格 ----
        Backdrop _backdrop;

        /// <summary>現在畫面用的背景：光影風格固定攝影棚灰；卡通風格用選的那一組（換裝扮時用正在預覽的）</summary>
        Backdrop Shown()
        {
            if (RenderStyle.Mode == RenderMode.Blender) return Backdrop.Studio;
            return _page == Page.Wardrobe && _pickBackdrop != null ? Backdrop.Find(_pickBackdrop) : _backdrop;
        }

        /// <summary>鏡頭背景（上方）；介面底色（下方）在 Render 用同一色</summary>
        void ApplyBackdrop(Backdrop b)
        {
            if (_camera != null) _camera.backgroundColor = b.Color;
        }

        void ApplyStyle(RenderMode mode)
        {
            if (RenderStyle.Mode != mode) RenderStyle.Apply(mode);
            ApplyBackdrop(Shown());
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
            Render();
            long failed = -1;
            yield return _api.Send(SupabaseApi.UpsertProfile(_childId, _pickVariant, _pickPalette), _ => { }, c => failed = c);
            _busy = false;
            if (failed >= 0) { _notice = SupabaseApi.DescribeError(failed); Render(); yield break; }
            _profile = new BeastProfile(_pickVariant, _pickPalette,
                _profile != null ? _profile.Encouragements : new string[0]);
            _backdrop = Backdrop.Find(_pickBackdrop ?? _backdrop.Id);
            Backdrop.Save(_backdrop);
            GoHome();
        }

        IEnumerator SaveLog()
        {
            _busy = true;
            Render();
            string json = null;
            long failed = -1;
            yield return _api.Send(SupabaseApi.InsertEntry(_childId, _pickItem, _pickFruit), s => json = s, c => failed = c);
            _busy = false;
            if (failed >= 0) { _notice = SupabaseApi.DescribeError(failed); Render(); yield break; }

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
            // 星星從靈獸畫面的中間冒出來（靈獸畫面的高度由版面決定，所以換頁之後才算）
            var pal = Catalog.FindPalette(_profile.Palette);
            var main = PaletteMaterial.Hex(pal.Main); var accent = PaletteMaterial.Hex(pal.Accent);
            var center = new Vector2(0.5f, 1f - _camera.rect.height * 0.5f);
            if (_outcome.Evolved) _fx.Evolve(center, main, accent);
            else _fx.LevelUp(center, main, accent);
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
            // 每次打開遊戲，第一次回到靈獸之家時揮手打招呼（組長 2026-10-29）
            if (!_waved) { _waved = _beast.Play(BeastView.Wave); }
        }

        // ---- 靈獸自己的小動作（只在靈獸之家）----
        // 6 秒沒碰：玩一下球；15 秒：睡著（點一下就醒來，播 Happy）。
        // 只是讓靈獸看起來有生命，不提醒、不催促（守則紅燈 #2：沒有任何「回來看我」的機制）。
        const float PlayAfter = 6f, SleepAfter = 15f;   // 組長 2026-10-29
        bool _waved, _playedToy;
        float _lastTouch;

        void Touched()
        {
            _lastTouch = Time.time;
            _playedToy = false;
        }

        void IdleBehaviour()
        {
            if (_page != Page.Home || _beast == null || _beast.Evolving || _beast.Sleeping) return;
            float idle = Time.time - _lastTouch;
            if (idle > SleepAfter) _beast.Play(BeastView.Sleep);
            else if (idle > PlayAfter && !_playedToy)
            {
                _beast.Play(BeastView.PlayToy);   // 沒有這個動作的模型就什麼都不做
                _playedToy = true;                // 每段閒置只玩一次
            }
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
            Render();
        }

        void ShowPreview() =>
            _beast.Show(_pickVariant, _pickPalette, _page == Page.FirstMeet || _card == null ? 1 : _card.Stage);

        // ---- 畫面（UGUI，UiKit 以 400 寬的邏輯座標排版）----
        // 狀態一變就整頁重建（Render）：頁面元件少，重建比逐一更新簡單、不會漏改。

        RectTransform _column, _root, _ui, _background;
        Sparkles _fx;
        bool _wasEvolving;
        Vector2Int _screen;
        float _height, _top;

        void Update()
        {
            IdleBehaviour();
            bool evolving = _beast != null && _beast.Evolving;
            var screen = new Vector2Int(Screen.width, Screen.height);
            // 畫布第一個影格的尺寸可能還沒算好：欄的高度一變就重畫
            bool resized = _column != null && Mathf.Abs(_column.rect.height - _height) > 0.5f;
            if ((_page == Page.Celebrate && evolving != _wasEvolving) || screen != _screen || resized) Render();
        }

        void Render()
        {
            Touched();   // 每次重畫都是因為有操作（或換頁）
            if (_column == null)
            {
                _column = UiKit.CreateCanvas("GameUI", out _root);
                _fx = Sparkles.Create(_root);   // 效果層在介面上面，換頁重建時不動它
            }
            if (_ui != null) Destroy(_ui.gameObject);
            if (_background != null) Destroy(_background.gameObject);
            _ui = UiKit.Group(_column, "Page");
            _background = UiKit.Group(_root, "Background");
            _background.SetAsFirstSibling();
            _screen = new Vector2Int(Screen.width, Screen.height);
            _wasEvolving = _beast != null && _beast.Evolving;

            _height = UiKit.Height(_column);
            // 靈獸之家與慶祝頁：靈獸畫面往下延伸到對話框上緣（2026-11-01：對話框改貼在下方按鈕上面）
            if (_page == Page.Home || _page == Page.Celebrate)
            {
                float share0 = Mathf.Clamp((BubbleY() - 6f) / _height, 0.45f, 0.82f);
                _camera.rect = new Rect(0f, 1f - share0, 1f, share0);
            }
            float share = _camera != null && _camera.enabled ? _camera.rect.height : 0f;
            _top = _height * share;
            // 上下同一色：下方介面的底色跟靈獸身後一樣（2026-11-01 組長）
            var shown = Shown();
            ApplyBackdrop(shown);
            UiKit.Band(_background, shown.Color, 0f, 1f - share);

            switch (_page)
            {
                case Page.Loading: DrawLoading(); break;
                case Page.Error: DrawError(); break;
                case Page.FirstMeet: DrawPicker(true); break;
                case Page.Home: DrawHome(); break;
                case Page.Card: DrawCard(); break;
                case Page.Wardrobe: DrawPicker(false); break;
                case Page.Log: DrawLog(); break;
                case Page.Celebrate: DrawCelebrate(); break;
            }

            if (_busy) UiKit.Label(_ui, "儲存中…", 14, 0, _height - 130, 400, 30);
            if (_notice != null) UiKit.Label(_ui, _notice, 14, 16, _height - 130, 368, 40);
        }

        // ---- 下方的對話框：貼在按鈕上面（慶祝頁中間夾一行邀請）----
        const float BubbleH = 88f, ButtonsGap = 84f;

        float BubbleY()
        {
            float bottom = _height - ButtonsGap - 10f;                       // 按鈕上緣再空一點
            if (_page == Page.Celebrate && _invitation != null) bottom -= 40f; // 邀請那一行
            return bottom - BubbleH;
        }

        // 按鈕的共同設定：儲存中全部不能按
        Button Btn(string text, float x, float y, float w, float h, Action onClick, Color? tint = null,
                   int size = 18, string icon = null, bool enabled = true) =>
            UiKit.Button(_ui, text, x, y, w, h, onClick, tint, size, icon, enabled && !_busy);

        void DrawLoading()
        {
            UiKit.Label(_ui, "靈獸準備中…", 22, 0, _height / 2 - 30, 400, 60);
        }

        void DrawError()
        {
            UiKit.Label(_ui, _error, 22, 24, _height / 2 - 110, 352, 100);
            UiKit.Label(_ui, "回到牧區平台，再點一次「小領袖靈獸」就好。\n靈獸和服事紀錄都好好的，不會不見。", 14, 24, _height / 2, 352, 50);
            Btn("回到牧區平台", 100, _height / 2 + 70, 200, 56, SB_BackToPlatform, UiKit.Leaf);
        }

        void DrawHome()
        {
            var v = Catalog.FindVariant(_profile.Variant);
            UiKit.Label(_ui, (v != null ? v.DisplayName : _profile.Variant) + " · " + GrowthRules.StageName(_card.Stage), 22, 0, 8, 400, 34);
            Btn(BackgroundMusic.Label, 316, 8, 76, 26, () => { BackgroundMusic.Toggle(); Render(); }, size: 12);   // 聚會現場可以關掉
            // 點靈獸：跳一下（睡著時點一下＝醒來）；拖拉＝轉靈獸、上下看（跟 Demo 一樣）
            UiKit.Swipe(_ui, 0, 64, 400, _top - 70, () => { Touched(); _beast.Hop(); }, Orbit);

            UiKit.Bubble(_ui, _bubble, 24, BubbleY(), 352, BubbleH, 15);

            float y = _height - ButtonsGap;
            CuteBtn("服事卡", 16, y, 116, 0, () => Go(Page.Card));
            CuteBtn("換裝扮", 142, y, 116, 1, () =>
            {
                _pickVariant = _profile.Variant;
                _pickPalette = _profile.Palette;
                _pickBackdrop = _backdrop.Id;
                _pickStyle = _pickStyleBefore = RenderStyle.Mode;
                _wardrobeTab = 0;
                Go(Page.Wardrobe);
            });
            CuteBtn("＋1 服事", 268, y, 116, 2, () =>
            {
                _logStep = 0; _parentConfirmed = false; _pickItem = null; _pickFruit = null;
                Go(Page.Log);
            });
        }

        /// <summary>3D 可愛按鈕：顏色跟著背景，卡通風格加描邊、光影風格改用落影</summary>
        Button CuteBtn(string text, float x, float y, float w, int colorIndex, Action onClick)
        {
            var b = Shown();
            var face = b.Buttons[Mathf.Clamp(colorIndex, 0, b.Buttons.Length - 1)];
            return UiKit.CuteButton(_ui, text, x, y, w, 66, onClick, face, RenderStyle.Mode == RenderMode.Toon,
                                    18, !_busy);
        }

        void DrawCard()
        {
            UiKit.Label(_ui, "服事卡", 22, 0, 8, 400, 34);
            float y = _top + 12;
            foreach (var row in _card.Rows)
            {
                var icon = IconPath.Service(row.Item);
                var iconTex = icon != null ? Resources.Load<Texture2D>(icon) : null;
                float x = 24;
                if (iconTex != null)
                {
                    var raw = new GameObject("Icon", typeof(RectTransform), typeof(RawImage)).GetComponent<RawImage>();
                    raw.transform.SetParent(_ui, false);
                    raw.texture = iconTex;
                    raw.raycastTarget = false;
                    UiKit.Place(raw, x, y + 1, 28, 28);
                    x += 34;
                }
                UiKit.Label(_ui, row.Item + (row.Retired ? "（已停用）" : ""), 17, x, y, 244 - x, 30, TextAnchor.MiddleLeft);
                var right = row.Unexplored ? "1 等 · 等你來探索" : row.Level + " 等";
                UiKit.Label(_ui, right, 17, 200, y, 176, 30, TextAnchor.MiddleRight);
                y += 32;
            }
            y += 10;
            UiKit.Label(_ui, "最近的服事", 17, 24, y, 352, 28, TextAnchor.MiddleLeft);
            y += 30;
            var recent = _card.Recent(10);
            if (recent.Count == 0) UiKit.Label(_ui, "還沒有紀錄，第一次服事就從這裡開始。", 14, 24, y, 352, 26);
            foreach (var e in recent)
            {
                if (y > _height - 110) break;
                UiKit.Label(_ui, DisplayText.Date(e.CreatedAt) + "　" + e.Item + (e.Fruit != null ? " · " + e.Fruit : ""), 14, 24, y, 352, 26);
                y += 26;
            }
            Btn("回到靈獸", 130, _height - 76, 140, 56, GoHome);
        }

        void DrawPicker(bool first)
        {
            if (first)
            {
                UiKit.Label(_ui, "天父為你預備了一位夥伴", 22, 0, 8, 400, 34);
                UiKit.Label(_ui, _childName + "，選一位陪你一起長大的靈獸吧", 14, 0, 40, 400, 24);
            }
            else
            {
                UiKit.Label(_ui, "換裝扮", 22, 16, 8, 140, 34, TextAnchor.MiddleLeft);
                // 分頁：靈獸（種類、顏色）｜背景（背景、渲染風格）
                Btn("靈獸", 196, 8, 94, 34, () => { _wardrobeTab = 0; Render(); }, _wardrobeTab == 0 ? UiKit.Leaf : Color.white, 15);
                Btn("背景", 298, 8, 94, 34, () => { _wardrobeTab = 1; Render(); }, _wardrobeTab == 1 ? UiKit.Leaf : Color.white, 15);
            }
            // 拖拉看靈獸的每個角度（標題列下面）
            UiKit.Swipe(_ui, 0, 64, 400, _top - 70, () => _beast.Hop(), Orbit);

            if (!first && _wardrobeTab == 1) { DrawBackdropPicker(); return; }

            float y = _top + 14;
            var variants = Catalog.AvailableVariants.ToList();
            float w = 352f / variants.Count;
            for (int i = 0; i < variants.Count; i++)
            {
                var id = variants[i].Id;
                // 靈獸名稱一律英文顯示（組長裁決 2026-09-30）
                Btn(variants[i].DisplayName, 24 + i * w, y, w - 8, 56, () =>
                {
                    _pickVariant = id;
                    ShowPreview();
                    Render();
                }, id == _pickVariant ? UiKit.Leaf : Color.white);
            }

            y += 76;
            UiKit.Label(_ui, "選顏色", 17, 24, y, 352, 26, TextAnchor.MiddleLeft);
            y += 30;
            for (int i = 0; i < Catalog.Palettes.Count; i++)
            {
                var p = Catalog.Palettes[i];
                UiKit.Swatch(_ui, p, p.Id == _pickPalette, 24 + (i % 4) * 88, y + (i / 4) * 62, 80, 54, () =>
                {
                    if (_busy) return;
                    _pickPalette = p.Id;
                    ShowPreview();
                    Render();
                });
            }

            float by = _height - 84;
            if (first)
                Btn("就是你了！", 100, by, 200, 60, () => StartCoroutine(SaveLook()), UiKit.Leaf);
            else WardrobeButtons();
        }

        void WardrobeButtons()
        {
            float by = _height - 84;
            Btn("取消", 40, by, 150, 60, () =>
            {
                // 背景、渲染風格是即時預覽：取消就換回原本的
                _pickBackdrop = _backdrop.Id;
                ApplyStyle(_pickStyleBefore);
                GoHome();
            });
            Btn("儲存", 210, by, 150, 60, () => StartCoroutine(SaveLook()), UiKit.Leaf);
        }

        RenderMode _pickStyleBefore;

        /// <summary>
        /// 換裝扮 →「背景」分頁：先選畫面風格；卡通風格才有四種背景可選，光影風格固定美術預覽的攝影棚灰。
        /// 點了立刻預覽，儲存才算數。
        /// </summary>
        void DrawBackdropPicker()
        {
            float y = _top + 14;
            UiKit.Label(_ui, "畫面風格", 17, 24, y, 352, 26, TextAnchor.MiddleLeft);
            y += 30;
            var styles = new[] { (RenderMode.Toon, "卡通", "描邊、顏色明亮"), (RenderMode.Blender, "光影", "柔和的光與影子") };
            for (int i = 0; i < styles.Length; i++)
            {
                var (mode, name, hint) = styles[i];
                Btn(name + "\n" + hint, 24 + i * 180, y, 172, 58, () =>
                {
                    _pickStyle = mode;
                    ApplyStyle(mode);
                    Render();
                }, _pickStyle == mode ? UiKit.Leaf : Color.white, 15);
            }

            y += 78;
            // 光影風格固定攝影棚背景，不列背景選項（2026-11-01 組長：不需要說明文字）
            if (_pickStyle == RenderMode.Toon)
            {
                UiKit.Label(_ui, "背景", 17, 24, y, 352, 26, TextAnchor.MiddleLeft);
                y += 30;
                for (int i = 0; i < Backdrop.All.Count; i++)
                {
                    var b = Backdrop.All[i];
                    float x = 24 + i * 88;
                    if (b.Id == _pickBackdrop) UiKit.Box(_ui, UiKit.Ink, x - 4, y - 4, 88, 66);
                    var sw = UiKit.Box(_ui, b.Color, x, y, 80, 58);
                    UiKit.Label(sw.transform, b.Name, 15, 0, 0, 80, 58);
                    UiKit.Hotspot(_ui, x, y, 80, 58, () =>
                    {
                        if (_busy) return;
                        _pickBackdrop = b.Id;
                        ApplyBackdrop(Shown());
                        Render();
                    });
                }
            }
            WardrobeButtons();
        }

        void DrawLog()
        {
            UiKit.Label(_ui, "＋1 服事", 22, 0, 8, 400, 34);
            float y = _top + 14;
            switch (_logStep)
            {
                case 0:
                    // 家長守門：只是提醒（UX），真正的邊界是資料庫 RLS——只有綁定的家長帳號寫得進去
                    UiKit.Label(_ui, "請家長確認：紙本服事卡上已經有老師的簽名。", 17, 24, y, 352, 80, TextAnchor.MiddleLeft);
                    Btn(_parentConfirmed ? "已確認：老師簽過名了" : "我是家長，已看到老師的簽名", 24, y + 90, 352, 64,
                        () => { _parentConfirmed = !_parentConfirmed; Render(); }, _parentConfirmed ? UiKit.Leaf : Color.white);
                    Btn("下一步", 210, _height - 84, 150, 60, () => { _logStep = 1; Render(); }, enabled: _parentConfirmed);
                    break;
                case 1:
                    UiKit.Label(_ui, "這次服事的項目是？", 17, 24, y, 352, 30, TextAnchor.MiddleLeft);
                    var items = _card.LoggableItems;
                    if (items.Count == 0) UiKit.Label(_ui, "目前沒有可登錄的服事項目，請通知同工。", 14, 24, y + 40, 352, 60);
                    for (int i = 0; i < items.Count; i++)
                    {
                        var item = items[i];
                        Btn(item, 24 + (i % 2) * 180, y + 40 + (i / 2) * 66, 172, 58,
                            () => { _pickItem = item; _logStep = 2; Render(); }, size: 15, icon: IconPath.Service(item));
                    }
                    break;
                case 2:
                    UiKit.Label(_ui, "這次服事，你嘗到哪一顆果子？", 17, 24, y, 352, 30, TextAnchor.MiddleLeft);
                    for (int i = 0; i < Catalog.Fruits.Count; i++)
                    {
                        var fruit = Catalog.Fruits[i];
                        Btn(fruit.Name, 24 + (i % 3) * 120, y + 40 + (i / 3) * 62, 112, 54,
                            () => { _pickFruit = fruit.Name; _logStep = 3; _beast.Play(BeastView.Eat); Render(); }, icon: IconPath.Fruit(fruit));
                    }
                    Btn("跳過", 130, y + 236, 140, 50, () => { _pickFruit = null; _logStep = 3; Render(); });
                    break;
                case 3:
                    UiKit.Label(_ui, "要記下這一次服事嗎？", 17, 24, y, 352, 30, TextAnchor.MiddleLeft);
                    UiKit.Bubble(_ui, _pickItem + (_pickFruit != null ? " · " + _pickFruit : ""), 24, y + 40, 352, 80);
                    Btn("上一步", 40, y + 136, 150, 54, () => { _logStep = 2; Render(); });
                    Btn("儲存", 210, y + 136, 150, 54, () => StartCoroutine(SaveLog()), UiKit.Leaf);
                    break;
            }
            Btn("取消", 40, _height - 84, 150, 60, GoHome);
        }

        void DrawCelebrate()
        {
            if (_beast.Evolving)
            {
                UiKit.Label(_ui, "咦？靈獸發光了……", 22, 0, _top + 40, 400, 60);
                return;
            }
            var v = Catalog.FindVariant(_profile.Variant);
            var name = v != null ? v.DisplayName : _profile.Variant;
            var headline = _outcome.Evolved
                ? name + " 長大了！現在是「" + GrowthRules.StageName(_outcome.StageAfter) + "」"
                : _outcome.Item + " 升到 " + _outcome.LevelAfter + " 等！";
            UiKit.Label(_ui, headline, 22, 0, 8, 400, 40);
            UiKit.Swipe(_ui, 0, 56, 400, _top - 62, () => { if (!_beast.Evolving) _beast.Hop(); }, Orbit);
            float by = BubbleY();
            UiKit.Bubble(_ui, _celebrateMessage, 24, by, 352, BubbleH, 15);
            if (_invitation != null) UiKit.Label(_ui, _invitation, 14, 24, by + BubbleH + 4f, 352, 34);
            CuteBtn("好！", 130, _height - ButtonsGap, 140, 2, GoHome);
        }
    }
}
