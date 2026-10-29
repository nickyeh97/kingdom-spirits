using System;
using SpiritBeast.Core;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// 用程式建 UGUI 介面的小工具（不用 prefab：場景只放相機與燈，畫面都在執行期建立）。
    /// 版面用「400 寬的邏輯座標」：中間一欄寬 400，所有元件以欄的左上角為原點擺放（x 往右、y 往下），
    /// CanvasScaler 的 Expand 模式讓這一欄在直式手機上撐滿寬度、在橫式螢幕上置中（跟原本 IMGUI 版一樣）。
    /// 觸控：EventSystem＋StandaloneInputModule（舊版 Input Manager 會把觸控轉成點擊）。
    /// </summary>
    public static class UiKit
    {
        public static readonly Color Ink = new Color(0.29f, 0.23f, 0.16f);
        public static readonly Color Paper = new Color(0.99f, 0.96f, 0.89f);
        public static readonly Color Leaf = new Color(0.55f, 0.78f, 0.49f);
        public static readonly Color BubbleColor = new Color(0.45f, 0.36f, 0.25f, 0.92f);
        public const float Width = 400f;

        static Font _font;
        static Sprite _round;

        public static Font Font => _font != null ? _font : (_font = Resources.Load<Font>("Fonts/NotoSansTC-Subset"));

        /// <summary>
        /// 建立畫布與中間的欄。回傳欄（所有元件的父物件）；root 是整個畫布（給橫跨全寬的底色用）。
        /// </summary>
        public static RectTransform CreateCanvas(string name, out RectTransform root)
        {
            EnsureEventSystem();
            var go = new GameObject(name, typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            var canvas = go.GetComponent<Canvas>();
            canvas.renderMode = UnityEngine.RenderMode.ScreenSpaceOverlay;   // 本專案的 RenderMode 是渲染模式切換，這裡要 Unity 的
            var scaler = go.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            // 寬 400；高度至少 645（＝IMGUI 版的「寬度不超過高度 × 0.62」）→ Expand：兩個方向都放得下
            scaler.referenceResolution = new Vector2(Width, 645f);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.Expand;
            root = (RectTransform)go.transform;

            var column = new GameObject("Column", typeof(RectTransform)).GetComponent<RectTransform>();
            column.SetParent(root, false);
            column.anchorMin = new Vector2(0.5f, 0f);
            column.anchorMax = new Vector2(0.5f, 1f);
            column.pivot = new Vector2(0.5f, 1f);
            column.sizeDelta = new Vector2(Width, 0f);
            column.anchoredPosition = Vector2.zero;
            return column;
        }

        static void EnsureEventSystem()
        {
            if (EventSystem.current != null) return;
            new GameObject("EventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
            // StandaloneInputModule 讀舊版 Input；輸入設定錯（只開新版 Input System）時每一格都會丟例外、按鈕全部點不動
            try { var _ = Input.mousePosition; }
            catch (System.InvalidOperationException)
            {
                Debug.LogError("[介面] 按鈕點不動：Project Settings → Player → Active Input Handling 要選 Input Manager (Old)，改完重開 Unity。");
            }
        }

        /// <summary>欄的實際高度（邏輯單位）；畫布要先排版過一次才準</summary>
        public static float Height(RectTransform column)
        {
            Canvas.ForceUpdateCanvases();
            return column.rect.height;
        }

        /// <summary>空的容器（換頁時整個刪掉重建）</summary>
        public static RectTransform Group(Transform parent, string name)
        {
            var rt = new GameObject(name, typeof(RectTransform)).GetComponent<RectTransform>();
            rt.SetParent(parent, false);
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.one;
            rt.offsetMin = rt.offsetMax = Vector2.zero;
            return rt;
        }

        /// <summary>以欄的左上角為原點擺放：x 往右、y 往下（跟 IMGUI 版的 R(x, y, w, h) 相同）</summary>
        public static T Place<T>(T c, float x, float y, float w, float h) where T : Component
        {
            var rt = (RectTransform)c.transform;
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f);
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = new Vector2(x, -y);
            rt.sizeDelta = new Vector2(w, h);
            return c;
        }

        /// <summary>依畫布比例擺放（0–1），給橫跨全寬的底色用：y0、y1 由下往上</summary>
        public static Image Band(Transform parent, Color color, float y0, float y1)
        {
            var img = NewImage(parent, "Band", color, false);
            var rt = img.rectTransform;
            rt.anchorMin = new Vector2(0f, y0);
            rt.anchorMax = new Vector2(1f, y1);
            rt.offsetMin = rt.offsetMax = Vector2.zero;
            img.raycastTarget = false;
            return img;
        }

        public static Image Box(Transform parent, Color color, float x, float y, float w, float h, bool rounded = true)
        {
            var img = Place(NewImage(parent, "Box", color, rounded), x, y, w, h);
            img.raycastTarget = false;
            return img;
        }

        public static Text Label(Transform parent, string text, int size, float x, float y, float w, float h,
                                 TextAnchor anchor = TextAnchor.MiddleCenter, Color? color = null)
        {
            var t = new GameObject("Label", typeof(RectTransform), typeof(Text)).GetComponent<Text>();
            t.transform.SetParent(parent, false);
            t.font = Font;
            t.text = text ?? "";
            t.fontSize = size;
            t.alignment = anchor;
            t.color = color ?? Ink;
            t.supportRichText = false;
            t.horizontalOverflow = HorizontalWrapMode.Wrap;
            t.verticalOverflow = VerticalWrapMode.Overflow;
            t.raycastTarget = false;
            return Place(t, x, y, w, h);
        }

        /// <summary>圓角按鈕；icon 是 Resources 底下的圖示路徑（可省略，找不到就只顯示文字）</summary>
        public static Button Button(Transform parent, string text, float x, float y, float w, float h,
                                    Action onClick, Color? tint = null, int size = 17, string icon = null, bool interactable = true)
        {
            var img = Place(NewImage(parent, "Button", tint ?? Color.white, true), x, y, w, h);
            var button = img.gameObject.AddComponent<Button>();
            button.targetGraphic = img;
            button.interactable = interactable;
            if (onClick != null) button.onClick.AddListener(() => onClick());

            var tex = icon != null ? Resources.Load<Texture2D>(icon) : null;
            if (tex != null)
            {
                // 圖示在左、文字在右；圖示大小跟著按鈕高度
                float s = Mathf.Min(h - 10f, 44f);
                var raw = new GameObject("Icon", typeof(RectTransform), typeof(RawImage)).GetComponent<RawImage>();
                raw.transform.SetParent(img.transform, false);
                raw.texture = tex;
                raw.raycastTarget = false;
                Place(raw, 6f, (h - s) / 2f, s, s);
                Label(img.transform, text, size, s + 10f, 0f, w - s - 14f, h);
            }
            else Label(img.transform, text, size, 4f, 0f, w - 8f, h);
            return button;
        }

        /// <summary>透明的大按鈕（例如點靈獸讓牠跳一下）</summary>
        public static Button Hotspot(Transform parent, float x, float y, float w, float h, Action onClick)
        {
            var img = Place(NewImage(parent, "Hotspot", new Color(1f, 1f, 1f, 0f), false), x, y, w, h);
            var button = img.gameObject.AddComponent<Button>();
            button.transition = Selectable.Transition.None;
            button.onClick.AddListener(() => onClick());
            return button;
        }

        /// <summary>對話框：深色圓角底＋白字</summary>
        public static void Bubble(Transform parent, string text, float x, float y, float w, float h, int size = 17)
        {
            var box = Box(parent, BubbleColor, x, y, w, h);
            Label(box.transform, text, size, 12f, 8f, w - 24f, h - 16f, TextAnchor.MiddleCenter, Color.white);
        }

        /// <summary>配色色票：上面主色，下面左副色、右點綴色；選中時外面加深色框。點了呼叫 onClick</summary>
        public static void Swatch(Transform parent, Palette p, bool selected, float x, float y, float w, float h, Action onClick)
        {
            if (selected) Box(parent, Ink, x - 4f, y - 4f, w + 8f, h + 8f);
            var main = Box(parent, PaletteMaterial.Hex(p.Main), x, y, w, h);
            float bh = h * 0.3f;
            Box(main.transform, PaletteMaterial.Hex(p.Secondary), 0f, h - bh, w / 2f, bh, false);
            Box(main.transform, PaletteMaterial.Hex(p.Accent), w / 2f, h - bh, w / 2f, bh, false);
            Hotspot(parent, x, y, w, h, onClick);
        }

        static Image NewImage(Transform parent, string name, Color color, bool rounded)
        {
            var img = new GameObject(name, typeof(RectTransform), typeof(Image)).GetComponent<Image>();
            img.transform.SetParent(parent, false);
            img.color = color;
            if (rounded)
            {
                img.sprite = RoundSprite;
                img.type = Image.Type.Sliced;
                img.pixelsPerUnitMultiplier = 1.6f;   // 圓角半徑約 10 個邏輯單位
            }
            return img;
        }

        /// <summary>圓角方塊的九宮格貼圖：執行期畫一次（不用另外放圖檔）</summary>
        static Sprite RoundSprite
        {
            get
            {
                if (_round != null) return _round;
                const int size = 64, r = 16;
                var tex = new Texture2D(size, size, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp };
                var px = new Color32[size * size];
                for (int y = 0; y < size; y++)
                    for (int x = 0; x < size; x++)
                    {
                        // 到最近的圓角圓心的距離 → 邊緣做 1 像素的抗鋸齒
                        float cx = Mathf.Clamp(x + 0.5f, r, size - r), cy = Mathf.Clamp(y + 0.5f, r, size - r);
                        float d = Vector2.Distance(new Vector2(x + 0.5f, y + 0.5f), new Vector2(cx, cy));
                        byte a = (byte)(Mathf.Clamp01(r - d + 0.5f) * 255f);
                        px[y * size + x] = new Color32(255, 255, 255, a);
                    }
                tex.SetPixels32(px);
                tex.Apply(false, true);
                _round = Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), 100f, 0,
                                       SpriteMeshType.FullRect, new Vector4(r + 2, r + 2, r + 2, r + 2));
                return _round;
            }
        }
    }
}
