// 靈獸卡通著色器（URP）：依頂點色遮罩 Mask 套用三個色槽，加卡通明暗與描邊（GDD §7.2、art/ART_PROFILE.md）
//   A≈1：可換色，R／G／B → 主色／副色／點綴色槽，再乘上花紋貼圖（_Pattern，沒有花紋＝白色＝不變）
//        花紋強度 _PatternStrength 依成長階段設定（BeastForms.PatternStrength：幼體網格在階段 1 不顯示花紋）
//   A≈0：固定色，RGB 本身就是顏色（眼睛、鼻子、蹄、羊角、金飾）
//   公式與 art/blender/finalize_export.py 的 Blender 預覽材質相同
//   固定色不做色彩轉換：Blender 寫的是線性值（FLOAT_COLOR、匯出 colors_type='LINEAR'），
//   Unity 也原值讀入，專案是 Linear 色彩空間，兩邊看到的顏色一致
// 明暗：兩段卡通光（亮面／暗面），交界以 _ShadowSoftness 稍微柔化；暗面用暖色 _ShadowTint，不會變黑。
// 描邊：反向外殼（第二個 pass，只畫背面，沿法線在螢幕空間外推）；粗細以螢幕高度比例計，遠近一致。
// 純色模式（_UseMask = 0）：給還沒有正式模型的占位幾何體用，顏色取 _BaseColor。
// 渲染模式（全域 _SpiritStyle，由 Runtime 的 RenderStyle 切換，所有材質一起換）：
//   0 卡通：上面說的兩段明暗＋描邊
//   1 Blender 預覽：跟美術檢查用的 Cycles 預覽圖一致——蘭伯特漫射＋太陽投影＋均勻環境光，
//     再經過 Blender 的 AgX 色調映射（AgX_Lut.png 是用 Blender 4.2 Cycles 實際算出來的 32³ 查找表），不畫描邊
// 放在 Resources 底下，確保 Web 建置會打包（以 Shader.Find 載入）。
Shader "SpiritBeast/PaletteMask"
{
    Properties
    {
        _Primary ("Primary", Color) = (0.96, 0.93, 0.86, 1)
        _Secondary ("Secondary", Color) = (1, 0.95, 0.90, 1)
        _Accent ("Accent", Color) = (0.95, 0.55, 0.65, 1)
        _Pattern ("Pattern", 2D) = "white" {}
        _PatternStrength ("Pattern Strength (by stage)", Range(0, 1)) = 1
        [ToggleUI] _UseMask ("Use Vertex Mask", Float) = 1
        _BaseColor ("Base Color (when mask is off)", Color) = (1, 1, 1, 1)

        _ShadowTint ("Shadow Tint", Color) = (0.72, 0.66, 0.72, 1)
        _ShadowThreshold ("Shadow Threshold", Range(-1, 1)) = 0
        _ShadowSoftness ("Shadow Softness", Range(0.001, 0.5)) = 0.05
        _AmbientStrength ("Ambient Strength", Range(0, 1)) = 0.35
        _MinLight ("Min Light", Range(0, 1)) = 0.35

        _OutlineColor ("Outline Color", Color) = (0.24, 0.17, 0.12, 1)
        _OutlineWidth ("Outline Width (screen height)", Range(0, 0.02)) = 0.004

        // 診斷用：0 正常、1 遮罩 RGB 原值、2 遮罩 A（白＝可換色、黑＝固定色）、3 不打光的顏色
        _View ("Debug View", Float) = 0
    }

    HLSLINCLUDE
    #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

    // SRP Batcher：兩個 pass 共用同一組材質常數
    CBUFFER_START(UnityPerMaterial)
        float4 _Primary;
        float4 _Secondary;
        float4 _Accent;
        float4 _Pattern_ST;
        float _PatternStrength;
        float4 _BaseColor;
        float4 _ShadowTint;
        float4 _OutlineColor;
        float _UseMask;
        float _ShadowThreshold;
        float _ShadowSoftness;
        float _AmbientStrength;
        float _MinLight;
        float _OutlineWidth;
        float _View;
    CBUFFER_END

    // 全域（不屬於單一材質）：RenderStyle 用 Shader.SetGlobal* 設定
    float _SpiritStyle;          // 0 卡通、1 Blender 預覽
    float4 _SpiritAmbient;       // Blender 預覽的環境光（線性值＝Blender 世界顏色 × 強度）
    ENDHLSL

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

        Pass
        {
            Name "ToonForward"
            Tags { "LightMode" = "UniversalForward" }
            Cull Back

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            // 接收太陽投影（只有 Blender 預覽模式讓太陽投影；卡通模式燈光不投影，這些變體不會用到陰影圖）
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Color.hlsl"

            TEXTURE2D(_Pattern);
            SAMPLER(sampler_Pattern);
            TEXTURE2D(_SpiritAgxLut);
            SAMPLER(sampler_SpiritAgxLut);

            // AgX 查找表：1024×32 橫條＝32 片（藍）× 每片 32×32（紅 × 綠）；輸入用 log2 編碼，涵蓋 2^-12 ～ 2^4
            // （跟 Blender 烘表的腳本 Tools/bake_agx_lut.py 用同一組常數）
            #define AGX_N 32.0
            #define AGX_MINEV -12.0
            #define AGX_MAXEV 4.0
            float3 BlenderAgX(float3 linearColor)
            {
                float3 t = saturate((log2(max(linearColor, 1e-6)) - AGX_MINEV) / (AGX_MAXEV - AGX_MINEV)) * (AGX_N - 1.0);
                float b0 = floor(t.b);
                float b1 = min(b0 + 1.0, AGX_N - 1.0);
                float2 uv0 = float2((b0 * AGX_N + t.r + 0.5) / (AGX_N * AGX_N), (t.g + 0.5) / AGX_N);
                float2 uv1 = float2((b1 * AGX_N + t.r + 0.5) / (AGX_N * AGX_N), (t.g + 0.5) / AGX_N);
                float3 c0 = SAMPLE_TEXTURE2D_LOD(_SpiritAgxLut, sampler_SpiritAgxLut, uv0, 0).rgb;
                float3 c1 = SAMPLE_TEXTURE2D_LOD(_SpiritAgxLut, sampler_SpiritAgxLut, uv1, 0).rgb;
                float3 display = lerp(c0, c1, t.b - b0);     // 查表結果是螢幕用的 sRGB 編碼值
                return SRGBToLinear(display);                // 畫面緩衝會再編回 sRGB，所以先轉回線性
            }

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float4 color : COLOR;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 normalWS : TEXCOORD0;
                float2 uv : TEXCOORD1;
                float3 positionWS : TEXCOORD2;
                float4 mask : COLOR;
            };

            Varyings vert (Attributes v)
            {
                Varyings o;
                o.positionWS = TransformObjectToWorld(v.positionOS.xyz);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.normalWS = TransformObjectToWorldNormal(v.normalOS);
                o.uv = TRANSFORM_TEX(v.uv, _Pattern);
                o.mask = v.color;
                return o;
            }

            half4 frag (Varyings i) : SV_Target
            {
                if (_View > 0.5 && _View < 1.5) return half4(i.mask.rgb, 1);
                if (_View > 1.5 && _View < 2.5) return half4(i.mask.aaa, 1);

                float3 slot = (i.mask.r * _Primary.rgb + i.mask.g * _Secondary.rgb + i.mask.b * _Accent.rgb)
                              * lerp(1.0, SAMPLE_TEXTURE2D(_Pattern, sampler_Pattern, i.uv).rgb, _PatternStrength);
                float3 albedo = lerp(i.mask.rgb, slot, saturate(i.mask.a));
                albedo = lerp(_BaseColor.rgb, albedo, _UseMask);
                if (_View > 2.5) return half4(albedo, 1);

                float3 n = normalize(i.normalWS);
                if (_SpiritStyle > 0.5)
                {
                    // Blender 預覽：Cycles 實測——太陽強度 S 照在白色漫射面上＝S/π、均勻世界光 L＝L，
                    // 所以這裡用蘭伯特（燈光強度由 RenderStyle 設成 S/π）＋環境光，再過 AgX
                    Light sun = GetMainLight(TransformWorldToShadowCoord(i.positionWS));
                    float3 radiance = albedo * (sun.color * saturate(dot(n, sun.direction)) * sun.shadowAttenuation
                                                + _SpiritAmbient.rgb);
                    return half4(BlenderAgX(radiance), 1);
                }
                Light light = GetMainLight();
                float ndl = dot(n, light.direction);
                float lit = smoothstep(_ShadowThreshold - _ShadowSoftness, _ShadowThreshold + _ShadowSoftness, ndl);
                float3 shade = lerp(_ShadowTint.rgb, float3(1, 1, 1), lit) * light.color;
                float3 ambient = SampleSH(n) * _AmbientStrength;
                // 卡通風：再暗也保留最低亮度，不會整片黑掉
                float3 color = albedo * max(shade + ambient, _MinLight);
                return half4(color, 1);
            }
            ENDHLSL
        }

        Pass
        {
            Name "Outline"
            Tags { "LightMode" = "SRPDefaultUnlit" }
            Cull Front

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
            };

            Varyings vert (Attributes v)
            {
                Varyings o;
                float4 positionCS = TransformObjectToHClip(v.positionOS.xyz);
                float3 normalCS = TransformWorldToHClipDir(TransformObjectToWorldNormal(v.normalOS));
                float2 dir = normalize(normalCS.xy + 1e-5);
                dir.x *= _ScreenParams.y / _ScreenParams.x;          // 寬螢幕上也保持等粗
                positionCS.xy += dir * _OutlineWidth * 2.0 * positionCS.w;  // ×w：遠近一致的螢幕寬度
                o.positionCS = positionCS;
                return o;
            }

            half4 frag (Varyings i) : SV_Target
            {
                if (_View > 0.5 || _SpiritStyle > 0.5) clip(-1);   // 診斷顯示、Blender 預覽時不畫描邊
                return half4(_OutlineColor.rgb, 1);
            }
            ENDHLSL
        }

        Pass
        {
            // 投影：Blender 預覽模式的太陽會投影（頭在胸口上的影子等）；卡通模式燈光不投影，這個 pass 不會執行
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On
            ZTest LEqual
            ColorMask 0
            Cull Back

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            float3 _LightDirection;     // URP 畫陰影圖時設定（光線方向）

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
            };

            Varyings vert (Attributes v)
            {
                Varyings o;
                float3 positionWS = TransformObjectToWorld(v.positionOS.xyz);
                float3 normalWS = TransformObjectToWorldNormal(v.normalOS);
                float4 positionCS = TransformWorldToHClip(ApplyShadowBias(positionWS, normalWS, _LightDirection));
            #if UNITY_REVERSED_Z
                positionCS.z = min(positionCS.z, UNITY_NEAR_CLIP_VALUE);
            #else
                positionCS.z = max(positionCS.z, UNITY_NEAR_CLIP_VALUE);
            #endif
                o.positionCS = positionCS;
                return o;
            }

            half4 frag (Varyings i) : SV_Target
            {
                return 0;
            }
            ENDHLSL
        }
    }
}
