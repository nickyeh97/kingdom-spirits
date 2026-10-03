using System.Linq;
using NUnit.Framework;
using SpiritBeast.Core;

namespace SpiritBeast.Tests
{
    public class ModelSpecTests
    {
        static ModelMeasure Good(string name = "Lamb_Adult") => new ModelMeasure
        {
            Name = name, Triangles = 7900, MaterialCount = 1, MeshCount = 2,
            PrimaryVertices = 3000, SecondaryVertices = 800, AccentVertices = 120, FixedVertices = 400,
            Height = 0.9f, Width = 0.7f, Depth = 0.8f, MinY = 0f,
        };

        static SpecLevel Worst(ModelMeasure m) => ModelSpecRules.Check(m).Max(f => f.Level);

        [Test]
        public void GoodModel_AllOk() => Assert.That(Worst(Good()), Is.EqualTo(SpecLevel.Ok));

        [Test]
        public void Triangles_OverLimitIsError()
        {
            var m = Good(); m.Triangles = 8001;
            Assert.That(Worst(m), Is.EqualTo(SpecLevel.Error));
        }

        [Test]
        public void Triangles_BabyOverTargetIsWarningOnly()
        {
            var m = Good("Lamb_Baby"); m.Triangles = 6800;
            Assert.That(Worst(m), Is.EqualTo(SpecLevel.Warning));
            var adult = Good("Lamb_Adult"); adult.Triangles = 6800;
            Assert.That(Worst(adult), Is.EqualTo(SpecLevel.Ok), "成體沒有 6000 建議值");
        }

        [Test]
        public void MissingVertexColor_IsError()
        {
            var m = Good(); m.MeshesWithoutVertexColor = 1;
            Assert.That(ModelSpecRules.Check(m).Any(f => f.Level == SpecLevel.Error && f.Message.Contains("頂點色")), Is.True);
        }

        [Test]
        public void NoPrimaryVertices_IsError()
        {
            var m = Good(); m.PrimaryVertices = 0;
            Assert.That(Worst(m), Is.EqualTo(SpecLevel.Error));
        }

        [Test]
        public void AmbiguousAlpha_IsWarning()
        {
            var m = Good(); m.AmbiguousVertices = 12;
            Assert.That(Worst(m), Is.EqualTo(SpecLevel.Warning));
        }

        [TestCase(0.05f)]
        [TestCase(90f)]
        public void WrongUnits_IsError(float height)
        {
            var m = Good(); m.Height = height;
            Assert.That(Worst(m), Is.EqualTo(SpecLevel.Error));
        }

        [Test]
        public void PivotNotAtFeet_IsWarning()
        {
            var m = Good(); m.MinY = -0.45f;
            Assert.That(Worst(m), Is.EqualTo(SpecLevel.Warning));
            m.MinY = 0.01f;
            Assert.That(Worst(m), Is.EqualTo(SpecLevel.Ok), "1 公分內視為貼地");
        }

        [Test]
        public void MultipleMaterials_IsWarning()
        {
            var m = Good(); m.MaterialCount = 3;
            Assert.That(Worst(m), Is.EqualTo(SpecLevel.Warning));
        }

        [Test]
        public void Finding_ToStringHasLevelPrefix()
        {
            Assert.That(new SpecFinding(SpecLevel.Error, "x").ToString(), Is.EqualTo("[錯誤] x"));
        }
    }
}
