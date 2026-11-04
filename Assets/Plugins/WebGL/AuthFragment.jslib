mergeInto(LibraryManager.library, {
  // 取走 index.html 暫存的授權片段：取一次即清空，token 之後只留在 C# 記憶體
  SB_TakeAuthFragment: function () {
    var s = window.__sbAuthFragment || '';
    window.__sbAuthFragment = '';
    var size = lengthBytesUTF8(s) + 1;
    var buffer = _malloc(size);
    stringToUTF8(s, buffer, size);
    return buffer;
  },
  // 回到牧區平台：平台是在同一個分頁打開遊戲的，上一頁就是平台；直接開遊戲網址（沒有上一頁）時改開平台首頁
  SB_BackToPlatform: function () {
    if (history.length > 1) history.back();
    else location.href = window.__sbPlatformUrl || '/';
  }
});
