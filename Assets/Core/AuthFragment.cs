namespace SpiritBeast.Core
{
    public enum AuthFragmentError
    {
        None,
        Empty,
        MissingToken,
        MissingChild,
        InvalidChildId,
    }

    /// <summary>
    /// 平台開啟遊戲時帶的網址片段：<c>#at=&lt;access_token&gt;&amp;child=&lt;child_id&gt;</c>（GDD §6.2）。
    /// 只做格式檢查；token 是否有效、孩子是否屬於這位家長，由 Supabase RLS 決定。
    /// </summary>
    public sealed class AuthFragment
    {
        public string AccessToken { get; }
        public System.Guid ChildId { get; }
        public AuthFragmentError Error { get; }
        public bool IsValid => Error == AuthFragmentError.None;

        AuthFragment(string accessToken, System.Guid childId, AuthFragmentError error)
        {
            AccessToken = accessToken;
            ChildId = childId;
            Error = error;
        }

        public static AuthFragment Parse(string fragment)
        {
            if (fragment != null && fragment.StartsWith("#")) fragment = fragment.Substring(1);
            if (string.IsNullOrEmpty(fragment)) return Fail(AuthFragmentError.Empty);

            string token = null, child = null;
            foreach (var pair in fragment.Split('&'))
            {
                int eq = pair.IndexOf('=');
                if (eq <= 0) continue;
                string key = pair.Substring(0, eq);
                // 不把 '+' 當空白：片段不是表單編碼，JWT 也不含空白
                string value = System.Uri.UnescapeDataString(pair.Substring(eq + 1));
                if (key == "at" && token == null) token = value;
                else if (key == "child" && child == null) child = value;
            }

            if (string.IsNullOrEmpty(token)) return Fail(AuthFragmentError.MissingToken);
            if (string.IsNullOrEmpty(child)) return Fail(AuthFragmentError.MissingChild);
            if (!System.Guid.TryParseExact(child, "D", out var childId)) return Fail(AuthFragmentError.InvalidChildId);
            return new AuthFragment(token, childId, AuthFragmentError.None);
        }

        static AuthFragment Fail(AuthFragmentError error) => new AuthFragment(null, System.Guid.Empty, error);

        // 永遠不輸出 token，避免出現在任何 log
        public override string ToString() =>
            IsValid ? $"AuthFragment(child={ChildId}, token=<redacted>)" : $"AuthFragment(error={Error})";
    }
}
