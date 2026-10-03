using System;
using System.Collections;
using System.Text;
using SpiritBeast.Core;
using UnityEngine.Networking;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// 以家長的 access token 呼叫 Supabase REST（GDD §6.2）。
    /// token 只放在記憶體與 Authorization 標頭，不寫入任何 log 或儲存空間。
    /// </summary>
    public sealed class SupabaseClient
    {
        readonly SupabaseConfig _config;
        readonly string _accessToken;

        public SupabaseClient(SupabaseConfig config, string accessToken)
        {
            _config = config;
            _accessToken = accessToken;
        }

        /// <summary>送出請求；成功回傳回應內容，失敗回傳 HTTP 狀態碼（連線失敗為 0）</summary>
        public IEnumerator Send(ApiRequest request, Action<string> onOk, Action<long> onFail)
        {
            using (var www = new UnityWebRequest(_config.Url + request.Path, request.Method))
            {
                if (request.Body != null)
                    www.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(request.Body));
                www.downloadHandler = new DownloadHandlerBuffer();
                www.SetRequestHeader("apikey", _config.AnonKey);
                www.SetRequestHeader("Authorization", "Bearer " + _accessToken);
                www.SetRequestHeader("Content-Type", "application/json");
                if (request.Prefer != null) www.SetRequestHeader("Prefer", request.Prefer);

                yield return www.SendWebRequest();

                if (www.result == UnityWebRequest.Result.Success) onOk(www.downloadHandler.text);
                else onFail(www.result == UnityWebRequest.Result.ConnectionError ? 0 : www.responseCode);
            }
        }
    }
}
