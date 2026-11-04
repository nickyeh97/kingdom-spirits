using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace SpiritBeast.Runtime
{
    /// <summary>按下時把按鈕面往下沉（露出的側邊變少），放開彈回：3D 按鈕的手感</summary>
    public sealed class PressSink : MonoBehaviour, IPointerDownHandler, IPointerUpHandler, IPointerExitHandler
    {
        public float Depth = 5f;
        bool _down;

        public void OnPointerDown(PointerEventData e)
        {
            var b = GetComponent<Selectable>();
            if (_down || (b != null && !b.IsInteractable())) return;
            _down = true;
            ((RectTransform)transform).anchoredPosition += new Vector2(0f, -Depth);
        }

        public void OnPointerUp(PointerEventData e) => Release();
        public void OnPointerExit(PointerEventData e) => Release();

        void Release()
        {
            if (!_down) return;
            _down = false;
            ((RectTransform)transform).anchoredPosition += new Vector2(0f, Depth);
        }
    }
}
