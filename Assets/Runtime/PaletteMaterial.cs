using System.Linq;
using SpiritBeast.Core;
using UnityEngine;

namespace SpiritBeast.Runtime
{
    /// <summary>依配色建立換色材質（著色器 SpiritBeast/PaletteMask，讀頂點色遮罩 Mask）並套到整個模型</summary>
    public static class PaletteMaterial
    {
        static Shader _shader;

        public static Material Create(Palette p)
        {
            if (_shader == null) _shader = Shader.Find("SpiritBeast/PaletteMask");
            if (_shader == null) return null;
            var mat = new Material(_shader) { name = "Palette_" + p.Id };
            mat.SetColor("_Primary", Hex(p.Main));
            mat.SetColor("_Secondary", Hex(p.Secondary));
            mat.SetColor("_Accent", Hex(p.Accent));
            return mat;
        }

        /// <summary>把模型所有 Renderer 的材質換成同一個換色材質；回傳建立的材質（呼叫端負責 Destroy）</summary>
        public static Material Apply(GameObject go, Palette p)
        {
            var mat = Create(p);
            if (mat == null) return null;
            foreach (var r in go.GetComponentsInChildren<Renderer>())
                r.sharedMaterials = Enumerable.Repeat(mat, Mathf.Max(1, r.sharedMaterials.Length)).ToArray();
            return mat;
        }

        public static Color Hex(string hex) => ColorUtility.TryParseHtmlString(hex, out var c) ? c : Color.white;
    }
}
