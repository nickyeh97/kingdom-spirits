mergeInto(LibraryManager.library, {
  // 取走 index.html 暫存的授權片段：取一次即清空，token 之後只留在 C# 記憶體
  SB_TakeAuthFragment: function () {
    var s = window.__sbAuthFragment || '';
    window.__sbAuthFragment = '';
    var size = lengthBytesUTF8(s) + 1;
    var buffer = _malloc(size);
    stringToUTF8(s, buffer, size);
    return buffer;
  }
});
