using System;
using System.Collections.Generic;

namespace SpiritBeast.Core
{
    /// <summary>在 Unity 量到的模型數據（由 Runtime 的 PalettePreview 量測）</summary>
    public sealed class ModelMeasure
    {
        public string Name { get; set; } = "";
        public int Triangles { get; set; }
        public int MaterialCount { get; set; }
        public int MeshCount { get; set; }
        /// <summary>沒有頂點色（Mask 屬性）的網格數；有任何一個就無法換色</summary>
        public int MeshesWithoutVertexColor { get; set; }
        /// <summary>A≈1 的頂點（可換色）中，以 R／G／B 為主的數量</summary>
        public int PrimaryVertices { get; set; }
        public int SecondaryVertices { get; set; }
        public int AccentVertices { get; set; }
        /// <summary>A≈0 的頂點（固定色：眼睛、鼻子、蹄…）</summary>
        public int FixedVertices { get; set; }
        /// <summary>A 不是 0 也不是 1 的頂點：通常是匯出時被轉了色彩空間或做了平滑</summary>
        public int AmbiguousVertices { get; set; }
        /// <summary>頂點色讀不到時為 false（網格未開 Read/Write 且不在編輯器）</summary>
        public bool MaskReadable { get; set; } = true;
        /// <summary>模型放在原點、不旋轉不縮放時的外框（公尺）</summary>
        public float Height { get; set; }
        public float Width { get; set; }
        public float Depth { get; set; }
        /// <summary>外框底部的 y；原點在腳底時應接近 0</summary>
        public float MinY { get; set; }
    }

    public enum SpecLevel { Ok, Warning, Error }

    public sealed class SpecFinding
    {
        public SpecLevel Level { get; }
        public string Message { get; }

        public SpecFinding(SpecLevel level, string message) { Level = level; Message = message; }

        public override string ToString() =>
            (Level == SpecLevel.Ok ? "[OK] " : Level == SpecLevel.Warning ? "[注意] " : "[錯誤] ") + Message;
    }

    /// <summary>
    /// 靈獸模型規格（GDD §7.2–7.3、docs/ART_PIPELINE.md §5）。
    /// 場景同時只有一隻靈獸，所以 8000 三角形是硬上限；幼體 6000 是建議值。
    /// </summary>
    public static class ModelSpecRules
    {
        public const int TriangleLimit = 8000;
        public const int BabyTriangleTarget = 6000;
        public const float MinHeight = 0.3f, MaxHeight = 3f;

        public static bool IsBaby(string name) => name.IndexOf("baby", StringComparison.OrdinalIgnoreCase) >= 0;

        public static IReadOnlyList<SpecFinding> Check(ModelMeasure m)
        {
            var list = new List<SpecFinding>();

            if (m.Triangles > TriangleLimit)
                list.Add(new SpecFinding(SpecLevel.Error, $"三角形 {m.Triangles}，超過上限 {TriangleLimit}"));
            else if (IsBaby(m.Name) && m.Triangles > BabyTriangleTarget)
                list.Add(new SpecFinding(SpecLevel.Warning, $"三角形 {m.Triangles}，在上限 {TriangleLimit} 內，但高於幼體建議值 {BabyTriangleTarget}"));
            else
                list.Add(new SpecFinding(SpecLevel.Ok, $"三角形 {m.Triangles}（上限 {TriangleLimit}）"));

            list.Add(m.MaterialCount <= 1
                ? new SpecFinding(SpecLevel.Ok, $"材質 {m.MaterialCount} 個")
                : new SpecFinding(SpecLevel.Warning, $"材質 {m.MaterialCount} 個，規格是單一材質（換色靠頂點色，不靠多材質）"));

            if (m.MeshesWithoutVertexColor > 0)
                list.Add(new SpecFinding(SpecLevel.Error, $"{m.MeshesWithoutVertexColor} 個網格沒有頂點色，無法換色（匯出前要跑 finalize_export.py 寫入 Mask）"));
            else if (!m.MaskReadable)
                list.Add(new SpecFinding(SpecLevel.Warning, "讀不到頂點色數值（請在編輯器 Play 模式檢查）"));
            else
            {
                if (m.PrimaryVertices == 0)
                    list.Add(new SpecFinding(SpecLevel.Error, "沒有任何主色頂點，換色時看不出變化"));
                else
                    list.Add(new SpecFinding(SpecLevel.Ok,
                        $"頂點色遮罩：主色 {m.PrimaryVertices}、副色 {m.SecondaryVertices}、點綴 {m.AccentVertices}、固定色 {m.FixedVertices}"));
                if (m.AmbiguousVertices > 0)
                    list.Add(new SpecFinding(SpecLevel.Warning,
                        $"{m.AmbiguousVertices} 個頂點的 A 不是 0 或 1，可能是匯出時做了色彩空間轉換（應為 LINEAR）"));
            }

            if (m.Height < MinHeight || m.Height > MaxHeight)
                list.Add(new SpecFinding(SpecLevel.Error, $"身高 {m.Height:0.00} 公尺，不在 {MinHeight}–{MaxHeight} 之間，匯出單位可能錯了（應為 1 單位＝1 公尺）"));
            else
                list.Add(new SpecFinding(SpecLevel.Ok, $"尺寸 寬 {m.Width:0.00} × 高 {m.Height:0.00} × 長 {m.Depth:0.00} 公尺"));

            list.Add(Math.Abs(m.MinY) <= Math.Max(0.02f, m.Height * 0.03f)
                ? new SpecFinding(SpecLevel.Ok, "原點在腳底")
                : new SpecFinding(SpecLevel.Warning, $"外框底部在 y={m.MinY:0.00}，原點不在腳底（站上地面時會浮起或陷下）"));

            return list;
        }
    }
}
