using NUnit.Framework;
using SpiritBeast.Core;

namespace SpiritBeast.Tests
{
    public class DemoModeTests
    {
        [TestCase("demo", false, true)]
        [TestCase("#demo", false, true)]
        [TestCase("", true, true)]
        [TestCase(null, true, true)]
        [TestCase("", false, false)]
        [TestCase("at=x&child=3f2504e0-4f89-11d3-9a0c-0305e82c3301", true, false)]
        [TestCase("demo=1", false, false)]
        public void Wants(string fragment, bool isEditor, bool expected)
        {
            Assert.That(DemoMode.Wants(fragment, isEditor), Is.EqualTo(expected));
        }
    }
}
