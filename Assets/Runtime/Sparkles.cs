using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// 慶祝效果（G3，GDD §4 S6）：升等時靈獸身邊冒出小星星與小圓點；進化時先一道柔光、再一大圈星星。
    /// 用 UGUI 畫在最上層（不用粒子系統模組，建置不變大；也不擋按鈕）。只在慶祝的那幾秒出現，平常沒有任何效果。
    /// 位置用畫布的比例座標（0–1，左下為原點），呼叫端給靈獸畫面的中心。
    /// </summary>
    public sealed class Sparkles : MonoBehaviour
    {
        static readonly Color Gold = new Color(1f, 0.84f, 0.35f);
        static Sprite _star, _dot;

        sealed class Particle
        {
            public RectTransform Rect;
            public Image Image;
            public Vector2 Pos, Vel;
            public float Age, Life, Size, Spin;
            public Color Color;
        }

        readonly List<Particle> _live = new List<Particle>();
        readonly List<(float at, System.Action run)> _later = new List<(float, System.Action)>();
        RectTransform _rect;
        Image _flash;
        float _flashAge = -1f, _flashLife;
        Color _flashColor;

        /// <summary>在畫布上建一層全螢幕、不接收點擊的效果層</summary>
        public static Sparkles Create(RectTransform canvasRoot)
        {
            var layer = UiKit.Group(canvasRoot, "Sparkles");
            var fx = layer.gameObject.AddComponent<Sparkles>();
            fx._rect = layer;
            fx._flash = new GameObject("Flash", typeof(RectTransform), typeof(Image)).GetComponent<Image>();
            fx._flash.transform.SetParent(layer, false);
            var rt = fx._flash.rectTransform;
            rt.anchorMin = Vector2.zero; rt.anchorMax = Vector2.one; rt.offsetMin = rt.offsetMax = Vector2.zero;
            fx._flash.raycastTarget = false;
            fx._flash.enabled = false;
            return fx;
        }

        /// <summary>升等：靈獸身邊冒出約 24 顆星星（主色、點綴色、金色、白色）</summary>
        public void LevelUp(Vector2 center, Color main, Color accent) =>
            Burst(center, 24, 220f, new[] { main, accent, Gold, Color.white });

        /// <summary>進化：配合靈獸的進化過場（1.5 秒時換成新形態）先亮一下柔光，再放一大圈星星</summary>
        public void Evolve(Vector2 center, Color main, Color accent)
        {
            After(1.2f, () => Flash(new Color(1f, 0.97f, 0.85f), 0.9f));
            After(1.5f, () => Burst(center, 48, 340f, new[] { main, accent, Gold, Color.white, Gold }));
            After(2.3f, () => Burst(center, 16, 180f, new[] { Gold, Color.white }));
        }

        void After(float seconds, System.Action run) => _later.Add((Time.unscaledTime + seconds, run));

        void Flash(Color color, float seconds)
        {
            _flashColor = color;
            _flashAge = 0f;
            _flashLife = seconds;
            _flash.enabled = true;
            _flash.transform.SetAsLastSibling();
        }

        void Burst(Vector2 center, int count, float speed, Color[] colors)
        {
            var size = _rect.rect.size;
            var origin = new Vector2(center.x * size.x, center.y * size.y);
            for (int i = 0; i < count; i++)
            {
                // 方向：一圈之中偏向上方，速度有快有慢，看起來像從靈獸身上「冒出來」
                float angle = (i + Random.value * 0.8f) / count * Mathf.PI * 2f;
                var dir = new Vector2(Mathf.Cos(angle), Mathf.Sin(angle) * 0.8f + 0.35f);
                var p = new Particle
                {
                    Pos = origin + dir * Random.Range(10f, 40f),
                    Vel = dir * speed * Random.Range(0.45f, 1f),
                    Life = Random.Range(1.1f, 1.9f),
                    Size = Random.Range(9f, 20f),
                    Spin = Random.Range(-180f, 180f),
                    Color = colors[i % colors.Length],
                };
                var img = new GameObject("Spark", typeof(RectTransform), typeof(Image)).GetComponent<Image>();
                img.transform.SetParent(_rect, false);
                img.sprite = i % 3 == 0 ? Dot : Star;
                img.type = Image.Type.Simple;
                img.raycastTarget = false;
                p.Image = img;
                p.Rect = img.rectTransform;
                p.Rect.anchorMin = p.Rect.anchorMax = Vector2.zero;
                _live.Add(p);
            }
        }

        void Update()
        {
            float now = Time.unscaledTime, dt = Time.unscaledDeltaTime;
            for (int i = _later.Count - 1; i >= 0; i--)
                if (now >= _later[i].at) { var run = _later[i].run; _later.RemoveAt(i); run(); }

            for (int i = _live.Count - 1; i >= 0; i--)
            {
                var p = _live[i];
                p.Age += dt;
                if (p.Age >= p.Life) { Destroy(p.Image.gameObject); _live.RemoveAt(i); continue; }
                p.Vel *= Mathf.Exp(-2.2f * dt);          // 空氣阻力：衝出去之後慢慢飄
                p.Vel.y -= 60f * dt;                     // 一點點往下飄
                p.Pos += p.Vel * dt;
                float k = p.Age / p.Life;
                float pop = Mathf.Min(1f, p.Age / 0.15f);                 // 一出現先「啵」一下長大
                float fade = k < 0.6f ? 1f : 1f - (k - 0.6f) / 0.4f;     // 最後 40% 慢慢淡掉
                p.Rect.anchoredPosition = p.Pos;
                p.Rect.sizeDelta = Vector2.one * p.Size * pop;
                p.Rect.localRotation = Quaternion.Euler(0f, 0f, p.Spin * p.Age);
                var c = p.Color; c.a = fade;
                p.Image.color = c;
            }

            if (_flashAge >= 0f)
            {
                _flashAge += dt;
                float k = Mathf.Clamp01(_flashAge / _flashLife);
                var c = _flashColor; c.a = Mathf.Sin(k * Mathf.PI) * 0.75f;   // 亮起來再退掉，不完全蓋住畫面
                _flash.color = c;
                if (k >= 1f) { _flashAge = -1f; _flash.enabled = false; }
            }
        }

        // 四角星（星形線 |u|^(2/3)+|v|^(2/3)=1，中間加一圈柔光）與柔邊小圓點：執行期各畫一次，不用另外放圖檔
        static Sprite Star => _star != null ? _star : (_star = Draw((u, v) =>
            Mathf.Max((1f - (Mathf.Pow(u, 2f / 3f) + Mathf.Pow(v, 2f / 3f))) * 6f, Mathf.Exp(-(u * u + v * v) * 9f) * 0.6f)));

        static Sprite Dot => _dot != null ? _dot : (_dot = Draw((u, v) => (1f - Mathf.Sqrt(u * u + v * v)) * 4f));

        /// <summary>alpha(u, v)：u、v 是到中心的距離（0–1）</summary>
        static Sprite Draw(System.Func<float, float, float> alpha)
        {
            const int size = 64;
            var tex = new Texture2D(size, size, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp };
            var px = new Color32[size * size];
            for (int y = 0; y < size; y++)
                for (int x = 0; x < size; x++)
                {
                    float u = Mathf.Abs((x + 0.5f) / size * 2f - 1f), v = Mathf.Abs((y + 0.5f) / size * 2f - 1f);
                    px[y * size + x] = new Color32(255, 255, 255, (byte)(Mathf.Clamp01(alpha(u, v)) * 255f));
                }
            tex.SetPixels32(px);
            tex.Apply(false, true);
            return Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), 100f);
        }
    }
}
