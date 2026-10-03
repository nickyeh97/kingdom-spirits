using System;
using System.Collections.Generic;
using System.Linq;

namespace SpiritBeast.Core
{
    /// <summary>服事項目字典的一筆（平台 child_service_items）</summary>
    public sealed class ServiceItem
    {
        public string Name { get; }
        public int SortOrder { get; }
        public bool Active { get; }

        public ServiceItem(string name, int sortOrder, bool active) { Name = name; SortOrder = sortOrder; Active = active; }
    }

    /// <summary>一次服事紀錄（平台 service_card_entries）</summary>
    public sealed class ServiceEntry
    {
        public string Item { get; }
        /// <summary>聖靈果子，可為 null（孩子跳過）</summary>
        public string Fruit { get; }
        /// <summary>紀錄時間＝家長按下儲存的時刻</summary>
        public DateTimeOffset CreatedAt { get; }

        public ServiceEntry(string item, string fruit, DateTimeOffset createdAt) { Item = item; Fruit = fruit; CreatedAt = createdAt; }
    }

    public sealed class ServiceCardRow
    {
        public string Item { get; }
        public int Count { get; }
        public int Level => GrowthRules.Level(Count);
        /// <summary>還沒服事過：畫面顯示「等你來探索」，不是「缺少」</summary>
        public bool Unexplored => Count == 0;
        /// <summary>字典中停用或已不存在的項目：只顯示舊紀錄，不能再登錄</summary>
        public bool Retired { get; }

        public ServiceCardRow(string item, int count, bool retired) { Item = item; Count = count; Retired = retired; }
    }

    /// <summary>
    /// 孩子自己的服事卡（GDD §3.2）。只彙總這一個孩子的紀錄，不和任何人比較。
    /// </summary>
    public sealed class ServiceCard
    {
        public IReadOnlyList<ServiceItem> Items { get; }
        public IReadOnlyList<ServiceEntry> Entries { get; }

        public ServiceCard(IEnumerable<ServiceItem> items, IEnumerable<ServiceEntry> entries)
        {
            Items = items.ToList();
            Entries = entries.ToList();
        }

        /// <summary>總次數（含已停用項目的舊紀錄）</summary>
        public int Total => Entries.Count;
        public int Stage => GrowthRules.Stage(Total);

        public int CountOf(string item) => Entries.Count(e => e.Item == item);

        /// <summary>
        /// 顯示順序：啟用中的項目（依字典排序，含沒服事過的）→ 停用但有紀錄的項目 → 字典外但有紀錄的項目。
        /// </summary>
        public IReadOnlyList<ServiceCardRow> Rows
        {
            get
            {
                var ordered = Items.OrderBy(i => i.SortOrder).ToList();
                var rows = ordered.Where(i => i.Active)
                    .Select(i => new ServiceCardRow(i.Name, CountOf(i.Name), false)).ToList();
                rows.AddRange(ordered.Where(i => !i.Active && CountOf(i.Name) > 0)
                    .Select(i => new ServiceCardRow(i.Name, CountOf(i.Name), true)));
                var known = new HashSet<string>(Items.Select(i => i.Name));
                rows.AddRange(Entries.Select(e => e.Item).Where(n => !known.Contains(n)).Distinct()
                    .OrderBy(n => n, StringComparer.Ordinal)
                    .Select(n => new ServiceCardRow(n, CountOf(n), true)));
                return rows;
            }
        }

        /// <summary>可以登錄的項目（啟用中，依字典排序）</summary>
        public IReadOnlyList<string> LoggableItems =>
            Items.Where(i => i.Active).OrderBy(i => i.SortOrder).Select(i => i.Name).ToList();

        public IReadOnlyList<string> UnexploredItems => Rows.Where(r => r.Unexplored).Select(r => r.Item).ToList();

        public IReadOnlyList<ServiceEntry> Recent(int n) =>
            Entries.OrderByDescending(e => e.CreatedAt).Take(n).ToList();

        public ServiceCard With(ServiceEntry entry) => new ServiceCard(Items, Entries.Append(entry));
    }

    /// <summary>登錄一次服事後的變化，用來決定慶祝畫面（S6）</summary>
    public sealed class LogOutcome
    {
        public string Item { get; }
        public int LevelBefore { get; }
        public int LevelAfter { get; }
        public int StageBefore { get; }
        public int StageAfter { get; }
        public bool Evolved => StageAfter > StageBefore;

        public LogOutcome(ServiceCard before, ServiceCard after, string item)
        {
            Item = item;
            LevelBefore = GrowthRules.Level(before.CountOf(item));
            LevelAfter = GrowthRules.Level(after.CountOf(item));
            StageBefore = before.Stage;
            StageAfter = after.Stage;
        }
    }
}
