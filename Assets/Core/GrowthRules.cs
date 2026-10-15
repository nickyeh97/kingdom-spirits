namespace SpiritBeast.Core
{
    /// <summary>成長規則（GDD §3.2–3.3、§8.3）</summary>
    public static class GrowthRules
    {
        /// <summary>項目等級＝次數＋1：沒服事過是一等，第一次服事二等（組長裁決 2026-09-17）</summary>
        public static int Level(int count) => (count < 0 ? 0 : count) + 1;

        /// <summary>靈獸階段（1 起算）：總次數達到的最高門檻</summary>
        public static int Stage(int total)
        {
            int stage = 1;
            for (int i = 0; i < Catalog.StageThresholds.Count; i++)
                if (total >= Catalog.StageThresholds[i]) stage = i + 1;
            return stage;
        }

        public static string StageName(int stage) => Catalog.StageNames[stage - 1];

        public static bool Evolved(int totalBefore, int totalAfter) => Stage(totalAfter) > Stage(totalBefore);
    }
}
