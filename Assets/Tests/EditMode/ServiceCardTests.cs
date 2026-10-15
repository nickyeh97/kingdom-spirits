using System;
using System.Linq;
using NUnit.Framework;
using SpiritBeast.Core;

namespace SpiritBeast.Tests
{
    public class ServiceCardTests
    {
        static readonly ServiceItem[] Items =
        {
            new ServiceItem("環境稽核", 6, true),
            new ServiceItem("收奉獻", 1, true),
            new ServiceItem("舊項目", 3, false),
            new ServiceItem("沒人做過的停用項目", 4, false),
        };

        static ServiceEntry E(string item, int day, string fruit = null) =>
            new ServiceEntry(item, fruit, new DateTimeOffset(2026, 9, day, 10, 0, 0, TimeSpan.Zero));

        [Test]
        public void EmptyCard_AllActiveItemsAreLevelOneAndUnexplored()
        {
            var card = new ServiceCard(Items, new ServiceEntry[0]);
            Assert.That(card.Total, Is.EqualTo(0));
            Assert.That(card.Stage, Is.EqualTo(1));
            Assert.That(card.Rows.Select(r => r.Item), Is.EqualTo(new[] { "收奉獻", "環境稽核" }));
            Assert.That(card.Rows.All(r => r.Level == 1 && r.Unexplored), Is.True);
        }

        [Test]
        public void Rows_CountLevelsAndKeepRetiredHistory()
        {
            var card = new ServiceCard(Items, new[] { E("收奉獻", 1), E("收奉獻", 8), E("舊項目", 2), E("字典外", 3) });
            var rows = card.Rows.ToDictionary(r => r.Item);
            Assert.That(rows["收奉獻"].Level, Is.EqualTo(3));
            Assert.That(rows["環境稽核"].Unexplored, Is.True);
            Assert.That(rows["舊項目"].Retired && rows["舊項目"].Level == 2, Is.True);
            Assert.That(rows["字典外"].Retired, Is.True);
            Assert.That(rows.ContainsKey("沒人做過的停用項目"), Is.False, "停用且沒紀錄的項目不顯示");
            Assert.That(card.Total, Is.EqualTo(4), "停用與字典外的舊紀錄仍算進總次數");
            Assert.That(card.Stage, Is.EqualTo(2));
        }

        [Test]
        public void LoggableItems_OnlyActiveInSortOrder()
        {
            var card = new ServiceCard(Items, new ServiceEntry[0]);
            Assert.That(card.LoggableItems, Is.EqualTo(new[] { "收奉獻", "環境稽核" }));
        }

        [Test]
        public void Recent_NewestFirstAndLimited()
        {
            var card = new ServiceCard(Items, Enumerable.Range(1, 12).Select(d => E("收奉獻", d)));
            var recent = card.Recent(10);
            Assert.That(recent.Count, Is.EqualTo(10));
            Assert.That(recent[0].CreatedAt.Day, Is.EqualTo(12));
            Assert.That(recent[9].CreatedAt.Day, Is.EqualTo(3));
        }

        [Test]
        public void LogOutcome_FirstServiceGoesToLevelTwo()
        {
            var before = new ServiceCard(Items, new ServiceEntry[0]);
            var o = new LogOutcome(before, before.With(E("收奉獻", 1)), "收奉獻");
            Assert.That((o.LevelBefore, o.LevelAfter), Is.EqualTo((1, 2)));
            Assert.That(o.Evolved, Is.False);
        }

        [Test]
        public void LogOutcome_EvolvesAtFourthService()
        {
            var before = new ServiceCard(Items, new[] { E("收奉獻", 1), E("收奉獻", 2), E("環境稽核", 3) });
            var o = new LogOutcome(before, before.With(E("環境稽核", 4)), "環境稽核");
            Assert.That(o.Evolved, Is.True);
            Assert.That((o.StageBefore, o.StageAfter), Is.EqualTo((1, 2)));
            Assert.That(o.LevelAfter, Is.EqualTo(3));
        }
    }

    public class EncouragerTests
    {
        static readonly ServiceItem[] Items = { new ServiceItem("收奉獻", 1, true), new ServiceItem("環境稽核", 2, true) };

        static LogOutcome Outcome(bool evolve)
        {
            var entries = Enumerable.Range(0, evolve ? 3 : 0)
                .Select(i => new ServiceEntry("收奉獻", null, DateTimeOffset.UnixEpoch)).ToArray();
            var before = new ServiceCard(Items, entries);
            return new LogOutcome(before, before.With(new ServiceEntry("收奉獻", null, DateTimeOffset.UnixEpoch)), "收奉獻");
        }

        [Test]
        public void ParentWordsComeFirst_OnOpenAndAfterLog()
        {
            var e = new Encourager(new[] { "你願意幫忙，媽媽好感動" }, new Random(1));
            Assert.That(e.OnOpen(), Is.EqualTo("你願意幫忙，媽媽好感動"));
            Assert.That(e.AfterLog(Outcome(true), "lamb", "喜樂"), Is.EqualTo("你願意幫忙，媽媽好感動"));
        }

        [Test]
        public void NoParentWords_OnOpenUsesIdentityVerse()
        {
            var e = new Encourager(new[] { "  ", null }, new Random(1));
            Assert.That(e.HasParentWords, Is.False, "空白句不算");
            Assert.That(Catalog.IdentityVerses, Does.Contain(e.OnOpen()));
        }

        [Test]
        public void NoParentWords_AfterLogPrefersEvolutionThenFruitThenService()
        {
            var e = new Encourager(null, new Random(1));
            Assert.That(e.AfterLog(Outcome(true), "dove", "喜樂"), Is.EqualTo(Catalog.FindVariant("dove").Verse));
            Assert.That(e.AfterLog(Outcome(false), "dove", "喜樂"), Is.EqualTo(Catalog.FindFruit("喜樂").Verse));
            Assert.That(Catalog.ServiceVerses, Does.Contain(e.AfterLog(Outcome(false), "dove", null)));
        }

        [Test]
        public void Invitation_OnlyForUnexploredItems()
        {
            var e = new Encourager(null, new Random(1));
            var card = new ServiceCard(Items, new[] { new ServiceEntry("收奉獻", null, DateTimeOffset.UnixEpoch) });
            Assert.That(e.Invitation(card), Does.Contain("環境稽核"));
            var all = card.With(new ServiceEntry("環境稽核", null, DateTimeOffset.UnixEpoch));
            Assert.That(e.Invitation(all), Is.Null, "全部探索過就不邀請");
        }
    }
}
