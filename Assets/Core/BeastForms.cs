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
    }
}
