using NUnit.Framework;
using SpiritBeast.Core;

namespace SpiritBeast.Tests
{
    // 平台 → 遊戲的授權片段解析（GDD §6.2）
    public class AuthFragmentTests
    {
        const string Token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ4In0.sig-_1";
        const string Child = "3f2504e0-4f89-11d3-9a0c-0305e82c3301";

        [Test]
        public void Parse_ValidFragment_WithHash()
        {
            var a = AuthFragment.Parse("#at=" + Token + "&child=" + Child);
            Assert.That(a.IsValid, Is.True);
            Assert.That(a.AccessToken, Is.EqualTo(Token));
            Assert.That(a.ChildId.ToString(), Is.EqualTo(Child));
        }

        [Test]
        public void Parse_ValidFragment_WithoutHash_AnyOrder()
        {
            var a = AuthFragment.Parse("child=" + Child + "&at=" + Token);
            Assert.That(a.IsValid, Is.True);
            Assert.That(a.AccessToken, Is.EqualTo(Token));
        }

        [TestCase(null)]
        [TestCase("")]
        [TestCase("#")]
        public void Parse_Empty(string fragment)
        {
            Assert.That(AuthFragment.Parse(fragment).Error, Is.EqualTo(AuthFragmentError.Empty));
        }

        [TestCase("child=" + Child)]
        [TestCase("at=&child=" + Child)]
        [TestCase("at&child=" + Child)]
        public void Parse_MissingToken(string fragment)
        {
            Assert.That(AuthFragment.Parse(fragment).Error, Is.EqualTo(AuthFragmentError.MissingToken));
        }

        [TestCase("at=" + Token)]
        [TestCase("at=" + Token + "&child=")]
        public void Parse_MissingChild(string fragment)
        {
            Assert.That(AuthFragment.Parse(fragment).Error, Is.EqualTo(AuthFragmentError.MissingChild));
        }

        [TestCase("not-a-guid")]
        [TestCase("{" + Child + "}")]
        [TestCase("3f2504e04f8911d39a0c0305e82c3301")]
        public void Parse_InvalidChildId(string child)
        {
            var a = AuthFragment.Parse("at=" + Token + "&child=" + child);
            Assert.That(a.Error, Is.EqualTo(AuthFragmentError.InvalidChildId));
            Assert.That(a.IsValid, Is.False);
        }

        [Test]
        public void Parse_DecodesPercentEncoding_ButKeepsPlus()
        {
            var a = AuthFragment.Parse("at=a%2Eb+c&child=" + Child);
            Assert.That(a.AccessToken, Is.EqualTo("a.b+c"));
        }

        [Test]
        public void Parse_IgnoresUnknownKeys_AndFirstDuplicateWins()
        {
            var a = AuthFragment.Parse("x=1&at=first&at=second&child=" + Child + "&y");
            Assert.That(a.IsValid, Is.True);
            Assert.That(a.AccessToken, Is.EqualTo("first"));
        }

        [Test]
        public void InvalidResult_HasNoToken()
        {
            var a = AuthFragment.Parse("at=" + Token + "&child=bad");
            Assert.That(a.AccessToken, Is.Null);
        }

        [Test]
        public void ToString_NeverContainsToken()
        {
            var a = AuthFragment.Parse("at=" + Token + "&child=" + Child);
            Assert.That(a.ToString(), Does.Not.Contain(Token));
            Assert.That(a.ToString(), Does.Contain(Child));
        }
    }
}
