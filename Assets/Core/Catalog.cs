using System.Collections.Generic;
using System.Linq;

namespace SpiritBeast.Core
{
    public sealed class BeastVariant
    {
        public string Id { get; }
        /// <summary>顯示名稱一律英文（組長裁決 2026-09-30）</summary>
        public string DisplayName { get; }
        public string Prototype { get; }
        /// <summary>進化時顯示的錨定經文</summary>
        public string Verse { get; }
        public bool Available { get; }

        public BeastVariant(string id, string displayName, string prototype, string verse, bool available)
        {
            Id = id; DisplayName = displayName; Prototype = prototype; Verse = verse; Available = available;
        }
    }

    public sealed class Palette
    {
        public string Id { get; }
        public string Name { get; }
        /// <summary>主色／副色／點綴色，格式 #RRGGBB</summary>
        public string Main { get; }
        public string Secondary { get; }
        public string Accent { get; }

        public Palette(string id, string name, string main, string secondary, string accent)
        {
            Id = id; Name = name; Main = main; Secondary = secondary; Accent = accent;
        }
    }

    public sealed class Fruit
    {
        /// <summary>中文名稱，也是資料庫 service_card_entries.fruit 的值</summary>
        public string Name { get; }
        public string Verse { get; }

        public Fruit(string name, string verse) { Name = name; Verse = verse; }
    }

    /// <summary>
    /// 遊戲的固定資料（GDD §3.3–3.5、附錄 A）。
    /// 放在 Core 而不是 ScriptableObject：dotnet 與 Unity 兩邊的測試都能直接驗證，且只有一份來源。
    /// 經文與文案依腓立比書 4:8 審稿：只肯定孩子與行動本身，不比較、不用罪惡感。
    /// </summary>
    public static class Catalog
    {
        public static readonly IReadOnlyList<BeastVariant> Variants = new[]
        {
            new BeastVariant("lamb", "Lamb", "小羊", "耶和華是我的牧者，我必不致缺乏。（詩篇 23:1）", true),
            new BeastVariant("dove", "Dove", "鴿子", "神的靈彷彿鴿子降下。（馬太福音 3:16）", true),
            new BeastVariant("lion", "Lion", "小獅", "猶大支派中的獅子已得勝。（啟示錄 5:5）", true),
            new BeastVariant("deer", "Deer", "小鹿", "我的心切慕你，如鹿切慕溪水。（詩篇 42:1）", false),
            new BeastVariant("eagle", "Eagle", "雛鷹", "等候耶和華的必如鷹展翅上騰。（以賽亞書 40:31）", false),
            new BeastVariant("fish", "Fish", "小魚", "來跟從我，我要叫你們得人如得魚一樣。（馬太福音 4:19）", false),
        };

        public static IEnumerable<BeastVariant> AvailableVariants => Variants.Where(v => v.Available);

        public static BeastVariant FindVariant(string id) => Variants.FirstOrDefault(v => v.Id == id);

        public static readonly IReadOnlyList<Palette> Palettes = new[]
        {
            new Palette("p1", "奶油", "#F6E7C8", "#E2B97F", "#7A5C3E"),
            new Palette("p2", "櫻花", "#FFD3DA", "#F497A9", "#8A3B4D"),
            new Palette("p3", "晴空", "#CFE8FF", "#7FB6E8", "#2F5D8A"),
            new Palette("p4", "嫩芽", "#D6F2D0", "#8CCB7E", "#3F6E35"),
            new Palette("p5", "陽光", "#FFE9A8", "#F5C542", "#8A6A12"),
            new Palette("p6", "薰衣草", "#E5D9FF", "#AE97EA", "#4E3D86"),
            new Palette("p7", "蜜桃", "#FFD9B8", "#F59E5B", "#8A4A1C"),
            new Palette("p8", "雲朵", "#E9EEF2", "#A9B6C2", "#3C4A57"),
        };

        public static Palette FindPalette(string id) => Palettes.FirstOrDefault(p => p.Id == id) ?? Palettes[0];

        /// <summary>聖靈的果子（加拉太書 5:22–23）；名稱與資料庫 check 約束一致</summary>
        public static readonly IReadOnlyList<Fruit> Fruits = new[]
        {
            new Fruit("仁愛", "愛是恆久忍耐，又有恩慈。（哥林多前書 13:4）"),
            new Fruit("喜樂", "你們要靠主常常喜樂。（腓立比書 4:4）"),
            new Fruit("和平", "使人和睦的人有福了。（馬太福音 5:9）"),
            new Fruit("忍耐", "忍耐到底的，必然得救。（馬太福音 24:13）"),
            new Fruit("恩慈", "要以恩慈相待。（以弗所書 4:32）"),
            new Fruit("良善", "不可為惡所勝，反要以善勝惡。（羅馬書 12:21）"),
            new Fruit("信實", "人在最小的事上忠心，在大事上也忠心。（路加福音 16:10）"),
            new Fruit("溫柔", "溫柔的人有福了。（馬太福音 5:5）"),
            new Fruit("節制", "你們要謹慎自守。（彼得前書 4:7）"),
        };

        public static Fruit FindFruit(string name) => Fruits.FirstOrDefault(f => f.Name == name);

        /// <summary>
        /// 離線 Demo 用的服事項目（與平台 child_service_items 目前的六項一致）。
        /// 正式遊戲一律讀平台的字典，不用這份。
        /// </summary>
        public static readonly IReadOnlyList<ServiceItem> DemoServiceItems = new[]
        {
            new ServiceItem("收奉獻", 1, true),
            new ServiceItem("敬拜-司琴", 2, true),
            new ServiceItem("敬拜-小樂器", 3, true),
            new ServiceItem("敬拜-Vocal", 4, true),
            new ServiceItem("領讀天使-宣言/讀經/禱告", 5, true),
            new ServiceItem("環境稽核", 6, true),
        };

        /// <summary>成長階段的總服事次數門檻（GDD §3.3）；永不退階</summary>
        public static readonly IReadOnlyList<int> StageThresholds = new[] { 0, 4, 12, 24 };
        public static readonly IReadOnlyList<string> StageNames = new[] { "初生", "成長", "茁壯", "小領袖" };

        /// <summary>身分：開啟遊戲時、家長沒寫鼓勵話語的預設</summary>
        public static readonly IReadOnlyList<string> IdentityVerses = new[]
        {
            "你是天父獨一無二的孩子。（詩篇 139:14）",
            "天父看著你，說：這是好的。（創世記 1:31）",
            "你在天父眼中是寶貴的。（以賽亞書 43:4）",
        };

        /// <summary>服事：登錄服事後、家長沒寫鼓勵話語的預設</summary>
        public static readonly IReadOnlyList<string> ServiceVerses = new[]
        {
            "無論做什麼，都從心裡做，像是為主做的。（歌羅西書 3:23）",
            "施比受更為有福。（使徒行傳 20:35）",
            "人子來不是要受人的服事，乃是要服事人。（馬可福音 10:45）",
            "你做在一個最小的身上，就是做在主身上了。（馬太福音 25:40）",
        };

        /// <summary>邀請：慶祝之後、最多一句、只針對還沒探索的項目。{0}＝項目名稱</summary>
        public static readonly IReadOnlyList<string> InvitationTemplates = new[]
        {
            "下次想試試看「{0}」嗎？",
            "「{0}」的門為你開著，想的時候再進去就好。",
        };
    }
}
