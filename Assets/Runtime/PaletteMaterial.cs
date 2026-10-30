using System.Linq;
using SpiritBeast.Core;
using UnityEngine;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// 依配色建立換色材質（著色器 SpiritBeast/PaletteMask，讀頂點色遮罩 Mask）並套到整個模型。
    /// 模型若有花紋貼圖（Resources 裡同名的「模型名_Pattern」），一起設上。
    /// 占位幾何體用 Flat：同一個著色器的純色模式（不讀遮罩），明暗與描邊和正式模型一致。
    /// </summary>
    public static class PaletteMaterial
    {
        static Shader _shader;

        static Shader FindShader()
        {
            if (_shader == null) _shader = Shader.Find("SpiritBeast/PaletteMask");
            return _shader;
        }

        public static Material Create(Palette p, Texture pattern = null)
        {
            if (FindShader() == null) return null;
            var mat = new Material(_shader) { name = "Palette_" + p.Id };
            mat.SetColor("_Primary", Hex(p.Main));
            mat.SetColor("_Secondary", Hex(p.Secondary));
            mat.SetColor("_Accent", Hex(p.Accent));
            if (pattern != null) mat.SetTexture("_Pattern", pattern);
            return mat;
        }

        /// <summary>純色材質（_UseMask = 0，顏色取 _BaseColor）；呼叫端負責 Destroy</summary>
        public static Material Flat(Color color)
        {
            if (FindShader() == null) return null;
            var mat = new Material(_shader) { name = "Flat_" + ColorUtility.ToHtmlStringRGB(color) };
            mat.SetFloat("_UseMask", 0f);
            mat.SetColor("_BaseColor", color);
            return mat;
        }

        /// <summary>找模型的花紋貼圖：Resources/Beasts/模型名_Pattern（例如 Lion_Baby_Pattern.png）；沒有就回 null</summary>
        public static Texture2D FindPattern(string modelName) => Resources.Load<Texture2D>("Beasts/" + modelName + "_Pattern");

        /// <summary>把模型所有 Renderer 的材質換成同一個換色材質；回傳建立的材質（呼叫端負責 Destroy）</summary>
        public static Material Apply(GameObject go, Palette p, Texture pattern = null)
        {
            var mat = Create(p, pattern);
            if (mat == null) return null;
            foreach (var r in go.GetComponentsInChildren<Renderer>())
                r.sharedMaterials = Enumerable.Repeat(mat, Mathf.Max(1, r.sharedMaterials.Length)).ToArray();
            return mat;
        }

        public static Color Hex(string hex) => ColorUtility.TryParseHtmlString(hex, out var c) ? c : Color.white;
    }
}
