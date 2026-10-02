using System;
using NUnit.Framework;
using Newtonsoft.Json.Linq;
using SpiritBeast.Core;

namespace SpiritBeast.Tests
{
    public class SupabaseApiTests
    {
        static readonly Guid Child = Guid.Parse("3f2504e0-4f89-11d3-9a0c-0305e82c3301");

        [Test]
        public void Config_ParsesAndTrimsTrailingSlash()
        {
            var c = SupabaseConfig.Parse("{\"url\":\"https://abc.supabase.co/\",\"anonKey\":\"key\"}");
            Assert.That(c.Url, Is.EqualTo("https://abc.supabase.co"));
            Assert.That(c.AnonKey, Is.EqualTo("key"));
        }

        [TestCase(null)]
        [TestCase("")]
        [TestCase("not json")]
        [TestCase("{\"url\":\"https://YOUR-PROJECT.supabase.co\",\"anonKey\":\"k\"}")]
        [TestCase("{\"url\":\"https://abc.supabase.co\",\"anonKey\":\"YOUR-ANON-KEY\"}")]
        [TestCase("{\"url\":\"http://abc.supabase.co\",\"anonKey\":\"k\"}")]
        [TestCase("{\"url\":\"https://abc.supabase.co\"}")]
        public void Config_RejectsMissingOrTemplateValues(string json)
        {
            Assert.That(SupabaseConfig.Parse(json), Is.Null);
        }

        [Test]
        public void Requests_FilterByThisChildOnly()
        {
            foreach (var r in new[] { SupabaseApi.GetChild(Child), SupabaseApi.GetEntries(Child), SupabaseApi.GetProfile(Child) })
            {
                Assert.That(r.Method, Is.EqualTo("GET"));
                Assert.That(r.Path, Does.Contain("=eq." + Child));
            }
            Assert.That(SupabaseApi.GetEntries(Child).Path, Does.Contain("order=created_at.desc"));
        }

        [Test]
        public void InsertEntry_SendsOnlyChildItemFruit()
        {
            var r = SupabaseApi.InsertEntry(Child, "收奉獻", "喜樂");
            Assert.That(r.Method, Is.EqualTo("POST"));
            Assert.That(r.Prefer, Is.EqualTo("return=representation"));
            var body = JObject.Parse(r.Body);
            Assert.That(body.Count, Is.EqualTo(3), "recorded_by／created_at 交給資料庫預設");
            Assert.That((string)body["item"], Is.EqualTo("收奉獻"));
            Assert.That(body["fruit"].Type, Is.EqualTo(JTokenType.String));
            Assert.That(JObject.Parse(SupabaseApi.InsertEntry(Child, "收奉獻", null).Body)["fruit"].Type, Is.EqualTo(JTokenType.Null));
        }

        [Test]
        public void InsertEntry_EscapesItemNames()
        {
            var r = SupabaseApi.InsertEntry(Child, "領讀天使-宣言/讀經/禱告\"x", null);
            Assert.That((string)JObject.Parse(r.Body)["item"], Is.EqualTo("領讀天使-宣言/讀經/禱告\"x"));
        }

        [Test]
        public void UpsertProfile_NeverOverwritesEncouragements()
        {
            var r = SupabaseApi.UpsertProfile(Child, "lamb", "p3");
            Assert.That(r.Path, Does.Contain("on_conflict=child_id"));
            Assert.That(r.Prefer, Does.Contain("resolution=merge-duplicates"));
            Assert.That(JObject.Parse(r.Body).ContainsKey("encouragements"), Is.False);
        }

        [Test]
        public void ParseChildName_EmptyWhenRlsHidesIt()
        {
            Assert.That(SupabaseApi.ParseChildName("[{\"name\":\"測試甲\"}]"), Is.EqualTo("測試甲"));
            Assert.That(SupabaseApi.ParseChildName("[]"), Is.Null);
        }

        [Test]
        public void ParseItemsAndEntries()
        {
            var items = SupabaseApi.ParseItems("[{\"name\":\"收奉獻\",\"sort_order\":1,\"active\":true},{\"name\":\"舊\",\"sort_order\":2,\"active\":false}]");
            Assert.That(items.Count, Is.EqualTo(2));
            Assert.That(items[1].Active, Is.False);

            var entries = SupabaseApi.ParseEntries(
                "[{\"item\":\"收奉獻\",\"fruit\":\"喜樂\",\"created_at\":\"2026-09-12T15:30:00.123456+00:00\"}," +
                "{\"item\":\"收奉獻\",\"fruit\":null,\"created_at\":\"2026-09-12T16:30:00+00:00\"}]");
            Assert.That(entries[0].Fruit, Is.EqualTo("喜樂"));
            Assert.That(entries[1].Fruit, Is.Null);
            Assert.That(entries[0].CreatedAt, Is.EqualTo(new DateTimeOffset(2026, 9, 12, 15, 30, 0, 123, TimeSpan.Zero).AddTicks(4560)));
        }

        [Test]
        public void ParseProfile_NullBeforeFirstMeeting()
        {
            Assert.That(SupabaseApi.ParseProfile("[]"), Is.Null);
            var p = SupabaseApi.ParseProfile("[{\"variant\":\"dove\",\"palette\":\"p2\",\"encouragements\":[\"謝謝你\",\"加油\"]}]");
            Assert.That((p.Variant, p.Palette), Is.EqualTo(("dove", "p2")));
            Assert.That(p.Encouragements, Is.EqualTo(new[] { "謝謝你", "加油" }));
        }

        [Test]
        public void DisplayDate_UsesTaiwanTime()
        {
            // UTC 9/12 16:30 ＝ 台灣 9/13 00:30
            Assert.That(Display.Date(new DateTimeOffset(2026, 9, 12, 16, 30, 0, TimeSpan.Zero)), Is.EqualTo("2026/09/13"));
        }

        [TestCase(0, "網路")]
        [TestCase(401, "重新開啟")]
        [TestCase(503, "稍後")]
        public void DescribeError_IsFriendly(long status, string expected)
        {
            Assert.That(SupabaseApi.DescribeError(status), Does.Contain(expected));
        }
    }
}
