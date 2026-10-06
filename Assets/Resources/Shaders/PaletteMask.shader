// 靈獸換色著色器（內建渲染管線）：依頂點色遮罩 Mask 套用三個色槽（GDD §7.2）
//   A≈1：可換色，RGB 哪個通道亮就是哪一槽 → R×主色 + G×副色 + B×點綴色
//   A≈0：固定色，RGB 本身就是顏色（眼睛、鼻子、蹄、羊角）
// 公式與 art/blender/finalize_export.py 的 Blender 預覽材質一致，兩邊看到的顏色才會相同。
// 光照是簡易 toon 色階；正式 toon 著色器（描邊等）於 G2 完成。
// 放在 Resources 底下，確保 Web 建置會打包（以 Shader.Find 載入）。
Shader "SpiritBeast/PaletteMask"
{
    Properties
    {
        _Primary ("Primary", Color) = (0.96, 0.93, 0.86, 1)
        _Secondary ("Secondary", Color) = (1, 0.95, 0.90, 1)
        _Accent ("Accent", Color) = (0.95, 0.55, 0.65, 1)
        _Bands ("Toon Bands", Range(1, 6)) = 3
        _MinLight ("Min Light", Range(0, 1)) = 0.35
        // 診斷用：0 正常、1 遮罩 RGB 原值、2 遮罩 A（白＝可換色、黑＝固定色）、3 不打光的顏色
        _View ("Debug View", Float) = 0
    }
    SubShader
    {
        Tags { "RenderType" = "Opaque" "Queue" = "Geometry" }
        Pass
        {
            Tags { "LightMode" = "ForwardBase" }
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            #include "Lighting.cginc"

            fixed4 _Primary;
            fixed4 _Secondary;
            fixed4 _Accent;
            float _Bands;
            float _MinLight;
            float _View;

            struct appdata
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
                float4 color : COLOR;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                float3 normal : TEXCOORD0;
                float4 mask : COLOR;
            };

            v2f vert (appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.normal = UnityObjectToWorldNormal(v.normal);
                o.mask = v.color;
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                if (_View > 0.5 && _View < 1.5) return fixed4(i.mask.rgb, 1);
                if (_View > 1.5 && _View < 2.5) return fixed4(i.mask.aaa, 1);

                float3 slot = i.mask.r * _Primary.rgb + i.mask.g * _Secondary.rgb + i.mask.b * _Accent.rgb;
                float3 albedo = lerp(i.mask.rgb, slot, saturate(i.mask.a));
                if (_View > 2.5) return fixed4(albedo, 1);

                float3 n = normalize(i.normal);
                float ndl = saturate(dot(n, normalize(_WorldSpaceLightPos0.xyz)));
                ndl = floor(ndl * _Bands + 0.5) / _Bands;
                // 卡通風：暗面保留最低亮度，不會整片黑掉（環境光沒算好的新場景也一樣看得到）
                float3 light = _LightColor0.rgb * ndl + max(ShadeSH9(float4(n, 1)), _MinLight);
                return fixed4(albedo * light, 1);
            }
            ENDCG
        }
    }
    Fallback "Diffuse"
}
