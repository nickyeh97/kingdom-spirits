using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.IO;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace SpiritBeast.Core
{
    /// <summary>
    /// Supabase 專案的公開設定（URL 與 anon key 都是公開值；安全邊界是 RLS）。
    /// 來源：Assets/Resources/supabase.json，值同牧區平台的 VITE_SUPABASE_URL／VITE_SUPABASE_ANON_KEY。
    /// </summary>
    public sealed class SupabaseConfig
    {
        public string Url { get; }
        public string AnonKey { get; }

        SupabaseConfig(string url, string anonKey) { Url = url; AnonKey = anonKey; }

        /// <summary>設定檔缺漏或仍是範本值時回 null（畫面顯示「設定未完成」）</summary>
        public static SupabaseConfig Parse(string json)
        {
            try
            {
                var o = JObject.Parse(json ?? "");
                var url = ((string)o["url"] ?? "").Trim().TrimEnd('/');
                var key = ((string)o["anonKey"] ?? "").Trim();
                if (!url.StartsWith("https://") || url.Contains("YOUR-PROJECT") || key.Length == 0 || key.Contains("YOUR-ANON-KEY"))
                    return null;
                return new SupabaseConfig(url, key);
            }
            catch (JsonException)
            {
                return null;
            }
        }
    }

    /// <summary>要送出的一個 REST 請求（由 Runtime 用 UnityWebRequest 執行）</summary>
    public sealed class ApiRequest
    {
        public string Method { get; }
        public string Path { get; }
        public string Body { get; }
        public string Prefer { get; }

        public ApiRequest(string method, string path, string body = null, string prefer = null)
        {
            Method = method; Path = path; Body = body; Prefer = prefer;
        }
    }

    /// <summary>
    /// 遊戲用到的全部 REST 請求與回應解析（GDD §6）。只讀寫這一個孩子的資料，
    /// 能不能讀寫由資料庫 RLS 決定。
    /// </summary>
    public static class SupabaseApi
    {
        static string Id(Guid childId) => childId.ToString("D");

        public static ApiRequest GetChild(Guid childId) =>
            new ApiRequest("GET", $"/rest/v1/children?select=name&id=eq.{Id(childId)}");

        public static ApiRequest GetItems() =>
            new ApiRequest("GET", "/rest/v1/child_service_items?select=name,sort_order,active&order=sort_order");

        public static ApiRequest GetEntries(Guid childId) =>
            new ApiRequest("GET", $"/rest/v1/service_card_entries?select=item,fruit,created_at&child_id=eq.{Id(childId)}&order=created_at.desc");

        public static ApiRequest GetProfile(Guid childId) =>
            new ApiRequest("GET", $"/rest/v1/beast_profiles?select=variant,palette,encouragements&child_id=eq.{Id(childId)}");

        /// <summary>登錄一次服事。recorded_by 與 created_at 由資料庫預設（登入者、當下時刻）</summary>
        public static ApiRequest InsertEntry(Guid childId, string item, string fruit) =>
            new ApiRequest("POST", "/rest/v1/service_card_entries?select=item,fruit,created_at",
                new JObject { ["child_id"] = Id(childId), ["item"] = item, ["fruit"] = fruit }.ToString(Formatting.None),
                "return=representation");

        /// <summary>建立或更新外觀；只送 variant／palette，不會蓋掉家長在平台寫的鼓勵話語</summary>
        public static ApiRequest UpsertProfile(Guid childId, string variant, string palette) =>
            new ApiRequest("POST", "/rest/v1/beast_profiles?on_conflict=child_id",
                new JObject { ["child_id"] = Id(childId), ["variant"] = variant, ["palette"] = palette }.ToString(Formatting.None),
                "resolution=merge-duplicates,return=minimal");

        /// <summary>RLS 擋下時 PostgREST 回空陣列，所以「查無此孩子」與「不是你的孩子」看起來一樣——都回 null</summary>
        public static string ParseChildName(string json) =>
            ParseArray(json).Select(t => (string)t["name"]).FirstOrDefault();

        public static IReadOnlyList<ServiceItem> ParseItems(string json) =>
            ParseArray(json).Select(t => new ServiceItem((string)t["name"], (int?)t["sort_order"] ?? 0, (bool?)t["active"] ?? false)).ToList();

        public static IReadOnlyList<ServiceEntry> ParseEntries(string json) =>
            ParseArray(json).Select(ParseEntry).ToList();

        static ServiceEntry ParseEntry(JToken t) =>
            new ServiceEntry((string)t["item"], (string)t["fruit"], ParseTime(t["created_at"]));

        /// <summary>還沒建立靈獸（第一次相遇）時回 null</summary>
        public static BeastProfile ParseProfile(string json)
        {
            var t = ParseArray(json).FirstOrDefault();
            if (t == null) return null;
            var words = t["encouragements"] is JArray arr ? arr.Select(w => (string)w).ToList() : new List<string>();
            return new BeastProfile((string)t["variant"], (string)t["palette"], words);
        }

        /// <summary>
        /// 關掉 Newtonsoft 的自動日期轉換：預設會把 ISO 字串轉成「本機時間」的 DateTime，
        /// 結果隨執行環境的時區而變。保留原字串，由 ParseTime 依字串裡的時區解析。
        /// </summary>
        static JArray ParseArray(string json)
        {
            using (var reader = new JsonTextReader(new StringReader(json)) { DateParseHandling = DateParseHandling.None })
                return JArray.Load(reader);
        }

        static DateTimeOffset ParseTime(JToken t) =>
            DateTimeOffset.Parse((string)t, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal);

        /// <summary>HTTP 錯誤轉成給家長看的話（不顯示技術細節）</summary>
        public static string DescribeError(long status)
        {
            if (status == 0) return "連不上網路，請確認網路後再試一次";
            if (status == 401) return "登入已逾時，請回到平台重新開啟";
            if (status == 403) return "沒有權限，請回到平台重新開啟";
            if (status >= 500) return "伺服器暫時忙碌，請稍後再試";
            return "發生問題了，請回到平台重新開啟";
        }
    }

    public sealed class BeastProfile
    {
        public string Variant { get; }
        public string Palette { get; }
        public IReadOnlyList<string> Encouragements { get; }

        public BeastProfile(string variant, string palette, IReadOnlyList<string> encouragements)
        {
            Variant = variant; Palette = palette; Encouragements = encouragements;
        }
    }

    public static class Display
    {
        /// <summary>教會在台灣，紀錄日期一律以台灣時間顯示（WebGL 取不到裝置時區）</summary>
        public static readonly TimeSpan TaiwanOffset = TimeSpan.FromHours(8);

        public static string Date(DateTimeOffset t) => t.ToOffset(TaiwanOffset).ToString("yyyy/MM/dd", CultureInfo.InvariantCulture);
    }
}
