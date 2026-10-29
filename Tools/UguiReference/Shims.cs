// 2021.3 的 UnityEngine 模組參考裡沒有、但新版 UGUI 原始碼用到的型別（只為了編譯參考組件）
namespace UnityEngine
{
    [System.Flags]
    public enum PenStatus { None = 0, Contact = 1, Barrel = 2, Inverted = 4, Eraser = 8 }
}
