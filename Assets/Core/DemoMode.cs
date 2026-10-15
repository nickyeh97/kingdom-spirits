namespace SpiritBeast.Core
{
    /// <summary>
    /// 何時進入離線 Demo（不連平台、不讀寫資料）：網址片段是 #demo，或在編輯器直接按 Play 而沒有提供片段。
    /// 從平台帶 #at=…&amp;child=… 開啟時一律走正式流程。
    /// </summary>
    public static class DemoMode
    {
        public static bool Wants(string fragment, bool isEditor)
        {
            var f = (fragment ?? "").TrimStart('#').Trim();
            return f == "demo" || (isEditor && f.Length == 0);
        }
    }
}
