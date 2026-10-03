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
