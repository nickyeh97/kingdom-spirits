using SpiritBeast.Core;
using UnityEngine;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// G0 骨架：證明兩件事——Web 建置能在手機瀏覽器跑（旋轉方塊），
    /// 以及平台帶來的授權片段能交到 C#（畫面左上顯示解析結果，不顯示 token）。
    /// G1 起由正式畫面取代。
    /// </summary>
    public sealed class Bootstrap : MonoBehaviour
    {
#if UNITY_WEBGL && !UNITY_EDITOR
        [System.Runtime.InteropServices.DllImport("__Internal")]
        static extern string SB_TakeAuthFragment();
#else
        static string SB_TakeAuthFragment() => string.Empty;
#endif

        AuthFragment _auth;
        Transform _cube;
        string _status;
        GUIStyle _style;

        // 不依賴場景內容：任何場景載入後都會建立自己
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Create() => new GameObject(nameof(Bootstrap)).AddComponent<Bootstrap>();

        void Start()
        {
            _auth = AuthFragment.Parse(SB_TakeAuthFragment());
            _status = _auth.IsValid
                ? "Fragment OK  child=" + _auth.ChildId.ToString().Substring(0, 8) + "..."
                : "Fragment: " + _auth.Error;
            _cube = CreateCube();
        }

        static Transform CreateCube()
        {
            var go = new GameObject("Cube");
            go.AddComponent<MeshFilter>().sharedMesh = Resources.GetBuiltinResource<Mesh>("Cube.fbx");
            var shader = Shader.Find("Legacy Shaders/Diffuse");
            if (shader == null) shader = Shader.Find("Sprites/Default");
            var renderer = go.AddComponent<MeshRenderer>();
            if (shader != null) renderer.sharedMaterial = new Material(shader) { color = new Color(0.98f, 0.78f, 0.42f) };
            go.transform.position = new Vector3(0f, 1f, -6f);
            return go.transform;
        }

        void Update() => _cube.Rotate(20f * Time.deltaTime, 45f * Time.deltaTime, 0f);

        void OnGUI()
        {
            // WebGL 沒有系統字型可用，G0 的除錯文字只用英數
            if (_style == null) _style = new GUIStyle(GUI.skin.label) { fontSize = Mathf.Max(16, Screen.height / 30), wordWrap = true };
            GUI.Label(new Rect(16, 16, Screen.width - 32, Screen.height / 4f), _status, _style);
        }
    }
}
