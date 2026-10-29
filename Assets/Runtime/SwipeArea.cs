using System;
using UnityEngine;
using UnityEngine.EventSystems;

namespace SpiritBeast.Runtime
{
    /// <summary>
    /// 一塊透明的觸控區：點一下＝onTap；拖曳（手機滑動、滑鼠拖）＝onDrag(位移，像素)。
    /// UGUI 的 EventSystem 會分辨：手指移動超過一點點就算拖曳，放開時不會再觸發點擊。
    /// </summary>
    public sealed class SwipeArea : MonoBehaviour, IPointerClickHandler, IBeginDragHandler, IDragHandler
    {
        public Action OnTap;
        public Action<Vector2> OnDragDelta;

        public void OnPointerClick(PointerEventData e)
        {
            if (!e.dragging) OnTap?.Invoke();
        }

        public void OnBeginDrag(PointerEventData e) { }

        public void OnDrag(PointerEventData e) => OnDragDelta?.Invoke(e.delta);
    }
}
