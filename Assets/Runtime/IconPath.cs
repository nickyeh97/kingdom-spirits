using SpiritBeast.Core;

namespace SpiritBeast.Runtime
{
    /// <summary>圖示在 Resources 裡的路徑（檔名規則在 Core 的 Catalog，有測試）</summary>
    public static class IconPath
    {
        public static string Service(string item)
        {
            var key = Catalog.ServiceIcon(item);
            return key != null ? "Icons/Service/" + key : null;
        }

        public static string Fruit(Fruit fruit) => fruit != null ? "Icons/Fruits/" + fruit.Icon : null;
    }
}
