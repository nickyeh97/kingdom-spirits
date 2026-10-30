namespace SpiritBeast.Core
{
    /// <summary>
    /// 成長階段對應的模型（GDD §7.2：每種靈獸 3 個網格）。
    /// 階段 1–2 共用幼體網格（階段 2 放大一點區分），階段 3 成體，階段 4 小領袖。
    /// 模型放在任一 Resources 資料夾的 Beasts/ 底下，檔名「英文名_形態」，例如 Beasts/Lamb_Baby.fbx。
    /// </summary>
    public static class BeastForms
    {
        public static string FormName(int stage) => stage <= 2 ? "Baby" : stage == 3 ? "Adult" : "Leader";

        public static string ResourcePath(string displayName, int stage) => "Beasts/" + displayName + "_" + FormName(stage);

        /// <summary>同一個網格內用縮放區分階段：只有階段 2（成長）比初生大一點</summary>
        public static float Scale(int stage) => stage == 2 ? 1.12f : 1f;

        /// <summary>
        /// 花紋貼圖的顯示強度（著色器 _PatternStrength：0＝不顯示、1＝完整）。
        /// GDD §7.2：花紋從階段 2 開始出現；幼體網格是階段 1–2 共用的，所以要靠這個開關區分。
        /// 例外：小獅的自然毛色從初生就有（組長 2026-10-12 決定，見 art/briefs/Lion_Baby.md）。
        /// 沒有花紋貼圖的模型（例如小羊）不受影響。
        /// </summary>
        public static float PatternStrength(string variantId, int stage)
        {
            int from = variantId == "lion" ? 1 : 2;
            return stage >= from ? 1f : 0f;
        }
    }
}
