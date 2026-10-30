using System.Linq;
using NUnit.Framework;
using SpiritBeast.Core;

namespace SpiritBeast.Tests
{
    public class GrowthRulesTests
    {
        [TestCase(0, 1)]
        [TestCase(1, 2)]
        [TestCase(5, 6)]
        [TestCase(-3, 1)]
        public void Level_IsCountPlusOne(int count, int level)
        {
            Assert.That(GrowthRules.Level(count), Is.EqualTo(level));
        }

        [TestCase(0, 1)]
        [TestCase(3, 1)]
        [TestCase(4, 2)]
        [TestCase(11, 2)]
        [TestCase(12, 3)]
        [TestCase(23, 3)]
        [TestCase(24, 4)]
        [TestCase(500, 4)]
        public void Stage_FollowsThresholds(int total, int stage)
        {
            Assert.That(GrowthRules.Stage(total), Is.EqualTo(stage));
        }

        [Test]
        public void Evolved_OnlyWhenCrossingThreshold()
        {
            Assert.That(GrowthRules.Evolved(3, 4), Is.True);
            Assert.That(GrowthRules.Evolved(4, 5), Is.False);
            Assert.That(GrowthRules.Evolved(23, 24), Is.True);
            Assert.That(GrowthRules.Evolved(24, 25), Is.False);
            Assert.That(GrowthRules.Evolved(5, 4), Is.False, "刪除誤登不會「退化」動畫");
        }

        [Test]
        public void StageName_MatchesStage()
        {
            Assert.That(GrowthRules.StageName(1), Is.EqualTo("初生"));
            Assert.That(GrowthRules.StageName(4), Is.EqualTo("小領袖"));
        }

        [Test]
        public void Catalog_FirstReleaseHasThreeEnglishNamedVariants()
        {
            var names = Catalog.AvailableVariants.Select(v => v.DisplayName).ToArray();
            Assert.That(names, Is.EqualTo(new[] { "Lamb", "Dove", "Lion" }));
            Assert.That(Catalog.Variants.Count, Is.EqualTo(6));
        }

        [Test]
        public void Catalog_PalettesAndFruitsMatchDatabaseConstraints()
        {
            Assert.That(Catalog.Palettes.Select(p => p.Id), Is.EqualTo(Enumerable.Range(1, 8).Select(i => "p" + i)));
            Assert.That(Catalog.Fruits.Select(f => f.Name),
                Is.EqualTo(new[] { "仁愛", "喜樂", "和平", "忍耐", "恩慈", "良善", "信實", "溫柔", "節制" }));
            Assert.That(Catalog.FindPalette("p9").Id, Is.EqualTo("p1"), "未知配色退回預設");
        }

        [Test]
        public void Catalog_FruitIconsAreUniqueAsciiNames()
        {
            var icons = Catalog.Fruits.Select(f => f.Icon).ToList();
            Assert.That(icons.Distinct().Count(), Is.EqualTo(9));
            Assert.That(icons.All(i => i.All(c => c >= 'a' && c <= 'z')), Is.True, "檔名只用小寫英文");
        }

        [Test]
        public void Catalog_ServiceIconMatchesPlatformItemsByKeyword()
        {
            // 平台目前的七項（2026-10-30），各對到不同的圖示
            var icons = Catalog.DemoServiceItems.Select(i => Catalog.ServiceIcon(i.Name)).ToList();
            Assert.That(icons, Is.EqualTo(new[] { "offering", "tidy", "reading", "secretary", "instrument", "piano", "vocal" }));
            // 舊名稱（09 月的六項）也對得到：改名前登錄的紀錄照樣有圖示
            Assert.That(Catalog.ServiceIcon("收奉獻"), Is.EqualTo("offering"));
            Assert.That(Catalog.ServiceIcon("環境稽核"), Is.EqualTo("tidy"));
            Assert.That(Catalog.ServiceIcon("領讀天使-宣言/讀經/禱告"), Is.EqualTo("reading"));
            // 同工改名也對得到；對不到、空白回 null（介面只顯示文字）
            Assert.That(Catalog.ServiceIcon("敬拜-Vocal 主唱"), Is.EqualTo("vocal"));
            Assert.That(Catalog.ServiceIcon("領讀天使-禱告"), Is.EqualTo("reading"));
            Assert.That(Catalog.ServiceIcon("招待"), Is.Null);
            Assert.That(Catalog.ServiceIcon(null), Is.Null);
            Assert.That(Catalog.ServiceIcon(""), Is.Null);
        }

        [Test]
        public void Catalog_TextNeverCompares()
        {
            // 守則紅燈 #1／#7：文案不得出現比較或罪惡感字眼
            var all = Catalog.IdentityVerses.Concat(Catalog.ServiceVerses).Concat(Catalog.InvitationTemplates)
                .Concat(Catalog.Fruits.Select(f => f.Verse)).Concat(Catalog.Variants.Select(v => v.Verse));
            foreach (var word in new[] { "比別人", "第一名", "最棒的一個", "好久沒", "想你了", "落後" })
                Assert.That(all.Any(t => t.Contains(word)), Is.False, word);
        }
    }
}
