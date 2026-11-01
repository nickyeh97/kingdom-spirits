using System.Collections.Generic;
using UnityEngine;

namespace SpiritBeast.Runtime
{
    /// <summary>一組背景：靈獸身後的天空色、下方介面的底色，以及三顆主要按鈕的糖果色（跟著背景一起換）</summary>
    public sealed class Backdrop
    {
        public string Id { get; }
        public string Name { get; }
        public Color Sky { get; }
        public Color Paper { get; }
        /// <summary>靈獸之家三顆按鈕：服事卡、換裝扮、＋1 服事（最後一顆是主要動作，顏色最飽和）</summary>
        public Color[] Buttons { get; }

        Backdrop(string id, string name, string sky, string paper, params string[] buttons)
        {
            Id = id; Name = name; Sky = Hex(sky); Paper = Hex(paper);
            Buttons = new Color[buttons.Length];
            for (int i = 0; i < buttons.Length; i++) Buttons[i] = Hex(buttons[i]);
        }

        static Color Hex(string hex) => ColorUtility.TryParseHtmlString(hex, out var c) ? c : Color.white;

        /// <summary>
        /// 背景選項（2026-11-01 組長測試後新增）：全部是淺色，介面的深棕字在每一組上都看得清楚。
        /// 第一組「奶油」就是原本的樣子。
        /// </summary>
        public static readonly IReadOnlyList<Backdrop> All = new[]
        {
            new Backdrop("cream", "奶油", "#FCF4E2", "#FCF4E2", "#FFD9AE", "#F8C9DA", "#A9DA8C"),
            new Backdrop("sky", "晴空", "#CFE8F8", "#EEF7FD", "#BCDDF6", "#D9CEF3", "#9FD9B2"),
            new Backdrop("meadow", "草地", "#DDF0CF", "#F2F9EB", "#F9E7A6", "#F6CBB8", "#90D17B"),
            new Backdrop("blush", "粉彩", "#F9DDE7", "#FDF1F5", "#F8C4D6", "#CBD8F8", "#AADEB8"),
        };

        public static Backdrop Find(string id)
        {
            foreach (var b in All) if (b.Id == id) return b;
            return All[0];
        }

        // ---- 記住選擇（跟渲染模式一樣存在這台裝置的 PlayerPrefs；不寫資料庫） ----
        const string PrefKey = "SpiritBeast.Backdrop";

        public static Backdrop Load()
        {
            try { return Find(PlayerPrefs.GetString(PrefKey, All[0].Id)); }
            catch { return All[0]; }
        }

        public static void Save(Backdrop b)
        {
            try { PlayerPrefs.SetString(PrefKey, b.Id); }
            catch { }
        }
    }
}
