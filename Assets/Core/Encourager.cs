using System;
using System.Collections.Generic;
using System.Linq;

namespace SpiritBeast.Core
{
    /// <summary>
    /// 鼓勵話語挑選（GDD §3.5）。一個顯示位置每次一句：
    /// 家長的話優先；家長沒寫時用天父的話（經文）；邀請只在慶祝之後出現、最多一句。
    /// </summary>
    public sealed class Encourager
    {
        readonly IReadOnlyList<string> _parentWords;
        readonly Random _random;

        public Encourager(IEnumerable<string> parentWords, Random random)
        {
            _parentWords = (parentWords ?? Enumerable.Empty<string>())
                .Where(w => !string.IsNullOrWhiteSpace(w)).Select(w => w.Trim()).ToList();
            _random = random;
        }

        public bool HasParentWords => _parentWords.Count > 0;

        /// <summary>開啟遊戲時（主畫面）：家長的話，否則身分經文。不出現邀請，避免每次開啟都被提醒「還有沒做的」</summary>
        public string OnOpen() => HasParentWords ? Pick(_parentWords) : Pick(Catalog.IdentityVerses);

        /// <summary>
        /// 登錄服事後：家長的話必出一句；家長沒寫時，進化用靈獸錨定經文、有選果子用果子經文、否則服事經文。
        /// </summary>
        public string AfterLog(LogOutcome outcome, string variantId, string fruit)
        {
            if (HasParentWords) return Pick(_parentWords);
            if (outcome.Evolved)
            {
                var v = Catalog.FindVariant(variantId);
                if (v != null) return v.Verse;
            }
            var f = fruit == null ? null : Catalog.FindFruit(fruit);
            return f != null ? f.Verse : Pick(Catalog.ServiceVerses);
        }

        /// <summary>慶祝後的邀請：隨機一個還沒探索的項目；全部探索過就不邀請（回 null）</summary>
        public string Invitation(ServiceCard card)
        {
            var open = card.UnexploredItems;
            if (open.Count == 0) return null;
            return string.Format(Pick(Catalog.InvitationTemplates), Pick(open));
        }

        string Pick(IReadOnlyList<string> list) => list[_random.Next(list.Count)];
    }
}
