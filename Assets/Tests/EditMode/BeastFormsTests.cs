using NUnit.Framework;
using SpiritBeast.Core;

namespace SpiritBeast.Tests
{
    public class BeastFormsTests
    {
        [TestCase(1, "Baby")]
        [TestCase(2, "Baby")]
        [TestCase(3, "Adult")]
        [TestCase(4, "Leader")]
        public void FormName_ThreeMeshesForFourStages(int stage, string form)
        {
            Assert.That(BeastForms.FormName(stage), Is.EqualTo(form));
        }

        [Test]
        public void ResourcePath_UsesEnglishNameAndForm()
        {
            Assert.That(BeastForms.ResourcePath("Lamb", 1), Is.EqualTo("Beasts/Lamb_Baby"));
            Assert.That(BeastForms.ResourcePath("Lamb", 4), Is.EqualTo("Beasts/Lamb_Leader"));
        }

        [Test]
        public void Scale_OnlyGrowthStageIsBiggerWithinBabyMesh()
        {
            Assert.That(BeastForms.Scale(2), Is.GreaterThan(BeastForms.Scale(1)));
            Assert.That(BeastForms.Scale(3), Is.EqualTo(1f));
        }

        [Test]
        public void DemoItems_AreTheSixActiveServiceItems()
        {
            var card = new ServiceCard(Catalog.DemoServiceItems, new ServiceEntry[0]);
            Assert.That(card.LoggableItems.Count, Is.EqualTo(6));
            Assert.That(card.LoggableItems[0], Is.EqualTo("收奉獻"));
        }

        [Test]
        public void DemoJourney_ReachesLeaderAtTwentyFourServices()
        {
            // Demo 一路按到底：第 4、12、24 次進化，之後不再進化
            var card = new ServiceCard(Catalog.DemoServiceItems, new ServiceEntry[0]);
            int evolutions = 0;
            for (int i = 1; i <= 30; i++)
            {
                var after = card.With(new ServiceEntry("收奉獻", null, System.DateTimeOffset.UnixEpoch));
                if (new LogOutcome(card, after, "收奉獻").Evolved) evolutions++;
                card = after;
            }
            Assert.That(evolutions, Is.EqualTo(3));
            Assert.That(BeastForms.FormName(card.Stage), Is.EqualTo("Leader"));
        }
    }
}
