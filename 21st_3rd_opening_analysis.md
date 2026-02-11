# 21st & 3rd Store Opening Day Traffic Analysis
**Store:** 21st & 3rd (shop_no: US00020)
**Opening Date:** February 6, 2026 (Friday)
**Analysis Date:** February 11, 2026
**Data Coverage:** 6 days

---

## Executive Summary | 执行摘要

### English Conclusion

**Opening day traffic for 21st & 3rd was HIGHER than subsequent days, but with important caveats.**

The store opened at **12:06 PM on February 6** (half-day operation) and achieved **298 cups**. This represents:
- **91% higher** than the first weekend average (Feb 7-8: 156 + 145 = 150.5 avg)
- **47% higher** than the average of all subsequent full days (203 cups, days 2-6)
- **1% higher** than the next Tuesday (Feb 10: 296 cups — essentially the same)

**Key Finding:** The opening day "boost" appears **minimal to moderate (1.47x ratio)** compared to our 8-store analysis median of 1.34x. However, this comparison is complicated by three factors:

1. **Half-day operation:** Opening day only had 12 hours of operation (12 PM - midnight) vs. full 24-hour days afterward
2. **Weekend dip:** Days 2-3 were Saturday-Sunday with naturally lower traffic (weekend effect)
3. **Limited data:** Only 6 days of data limits statistical confidence

**Adjusted Conclusion:** If we compare opening day to other **weekdays only** (Mon Feb 9: 208, Tue Feb 10: 296, Wed Feb 11: 201 incomplete), the opening boost is **minimal**. The store quickly stabilized at 200-300 cups/day, suggesting good baseline performance without excessive opening promotion.

---

### 中文结论

**21st & 3rd 门店开业第一天流量高于后续几天，但有重要说明。**

门店于**2月6日中午12:06开业**（半天营业），当天完成了**298杯**。这意味着：
- 比首个周末平均**高91%**（2月7-8日：156 + 145 = 平均150.5杯）
- 比后续全天平均**高47%**（第2-6天平均203杯）
- 比下周二**高1%**（2月10日：296杯 — 基本持平）

**核心发现：** 开业日"提升效应"为**轻度至中度（1.47倍）**，低于我们8家门店分析的中位数1.34倍。但这一比较受三个因素影响：

1. **半天营业：** 开业日仅营业12小时（中午12点至午夜），而后续为全天24小时
2. **周末效应：** 第2-3天为周六-周日，自然流量较低
3. **数据有限：** 仅6天数据，统计置信度有限

**调整后的结论：** 如果仅比较工作日（周一2月9日：208杯，周二2月10日：296杯，周三2月11日：201杯未完整），开业提升效应**很小**。门店迅速稳定在200-300杯/天水平，说明基线表现良好，未过度促销。

---

## Data Discovery Results

### Available Data Tables

✅ **luckyus_iluckyhealth.t_collect_shop_make_inter**
- Metric: `shop_make_done_TOP` (completed drink cups)
- Granularity: Minute-level timestamps
- Coverage: Feb 6, 2026 12:06 PM - Feb 11, 2026 19:57 PM
- Available metrics for this store:
  - `shop_make_done_TOP` — Completed drinks ✓ (used)
  - `shop_to_make_TOP` — Orders to make
  - `shop_making_TOP` — Drinks in progress
  - `shop_make_cancel_TOP` — Cancelled orders
  - `shop_tenant_make_done_top` — Tenant completed drinks

❌ **Sales/Revenue Data:** Not found in `t_collect_order_inter` or `t_collect_payment_inter` for this store

### Data Quality Notes
- **Feb 6:** Half-day operation (opened at 12:06 PM)
- **Feb 7-10:** Full 24-hour operation
- **Feb 11:** Partial data (only through 19:57 PM)
- **No zero-cup days:** All days have meaningful traffic data

---

## 2a. Day-by-Day Performance Table

| Date | Day of Week | Day # | Cup Count | vs Opening Day | vs Day 2-6 Avg | Notes |
|------|-------------|-------|-----------|----------------|----------------|-------|
| **2026-02-06** | **Friday** | **0** | **298** | — | **+47%** | **OPENING (half-day, 12 PM start)** |
| 2026-02-07 | Saturday | 1 | 156 | -48% | -23% | Weekend dip |
| 2026-02-08 | Sunday | 2 | 145 | -51% | -29% | Weekend dip |
| 2026-02-09 | Monday | 3 | 208 | -30% | +2% | Weekday recovery |
| 2026-02-10 | Tuesday | 4 | 296 | -1% | +46% | Near opening day level |
| 2026-02-11 | Wednesday | 5 | 201 | -33% | -1% | Partial data (incomplete) |

**Summary Statistics:**
- **Opening day:** 298 cups
- **Average of days 2-6:** 203 cups
- **Opening-to-average ratio:** 1.47x (+47%)
- **Weekday average (Mon-Wed, excluding half-days):** 235 cups
- **Weekend average (Sat-Sun):** 151 cups
- **Weekday vs Weekend gap:** 56% higher on weekdays

---

## 2b. Key Comparisons

### 1. Opening Day (Feb 6) vs. Day 2 (Feb 7)
- **Opening day:** 298 cups (Friday, half-day from 12 PM)
- **Day 2:** 156 cups (Saturday, full 24 hours)
- **Difference:** +91% higher on opening day
- **Note:** Not apples-to-apples comparison due to half-day opening + weekend effect

### 2. Opening Day vs. First Weekend (Feb 8-9)
- **Opening day:** 298 cups
- **Weekend average:** 150.5 cups (Sat 156 + Sun 145)
- **Difference:** +98% higher on opening day
- **Conclusion:** Strong opening day vs. weekend, but weekends naturally have lower traffic

### 3. Opening Day vs. Average of All Subsequent Days
- **Opening day:** 298 cups (half-day)
- **Subsequent days average (days 1-5):** 203 cups (full days)
- **Ratio:** 1.47x
- **Conclusion:** Moderate opening boost compared to the 8-store analysis median (1.34x)

### 4. Opening Day vs. Following Friday (N/A)
- **Not applicable:** No data for Friday Feb 13 yet (only 6 days of data)
- **Next available comparison:** Tuesday Feb 10 (296 cups) — essentially matched opening day performance (-1% difference)

### 5. Daily Trend
- **Pattern:** Opening 298 → Weekend dip 156/145 → Weekday recovery 208/296/201
- **Trend:** **Stabilizing** at 200-300 cups on weekdays
- **No clear decline:** Unlike stores like "28th & 6th" which dropped 70% after opening
- **Conclusion:** Traffic is **stable and consistent**, not declining — a positive sign

---

## 2c. Hourly Pattern Analysis

### Opening Day (Feb 6, Friday) — Half-Day Operation
**Operating hours:** 12:06 PM - 11:59 PM (12 hours)

| Hour | Cup Count | % of Day | Notes |
|------|-----------|----------|-------|
| 12 PM | 16 | 5.4% | Opening hour |
| 1 PM | 28 | 9.4% | |
| 2 PM | 42 | 14.1% | **Afternoon peak** |
| 3 PM | 19 | 6.4% | |
| 4 PM | 59 | 19.8% | **🔥 Opening day rush (19.8% of daily traffic)** |
| 5 PM | 29 | 9.7% | |
| 6 PM | 36 | 12.1% | Dinner time |
| 7 PM | 25 | 8.4% | |
| 8 PM | 16 | 5.4% | |
| 9 PM | 14 | 4.7% | |
| 10 PM | 9 | 3.0% | |
| 11 PM | 5 | 1.7% | |

**Key Observations:**
- **4 PM peak:** 59 cups (19.8% of daily volume) — likely opening day curiosity/promotion rush
- **Afternoon concentration:** 2-6 PM accounts for 185 cups (62% of daily traffic)
- **Evening drop-off:** Steady decline after 6 PM

### Subsequent Weekdays Average (Feb 9-11, 12 PM - 11 PM)
**For comparison:** Average hourly traffic on Mon-Wed during same hours

| Hour | Avg Cup Count | vs Opening Day | Notes |
|------|---------------|----------------|-------|
| 12 PM | 14 | -13% | Similar |
| 1 PM | 29 | +4% | Similar |
| 2 PM | 25 | **-40%** | Opening day had rush |
| 3 PM | 18 | -5% | Similar |
| 4 PM | 24 | **-59%** | **Opening day had 2.5x rush at 4 PM** |
| 5 PM | 25 | -14% | Similar |
| 6 PM | 24 | -33% | Opening day higher |
| 7 PM | 22 | -12% | Similar |
| 8 PM | 32 | +100% | **Subsequent days have stronger evening** |
| 9 PM | 13 | -7% | Similar |
| 10 PM | 16 | +78% | Subsequent days stronger |
| 11 PM | 6 | +20% | Similar |

**Hourly Pattern Insights:**
1. **Opening day rush at 4 PM:** 59 cups vs. 24 cups average (+146% spike) — clear opening promotion effect
2. **Subsequent days have stronger evening (8-10 PM):** Customers learning the store stays open late
3. **Afternoon peak (2-4 PM) was inflated on opening day:** Normalized afterward
4. **Morning/lunch (12-1 PM) is consistent:** No opening day effect during early hours

**Conclusion:** Opening day had a **concentrated afternoon rush (2-6 PM)** that accounted for most of the opening day boost. Subsequent days show more **balanced distribution** throughout operating hours, with stronger evening traffic.

---

## Comparison to 8-Store Analysis Benchmark

| Metric | 21st & 3rd | 8-Store Median | Comparison |
|--------|------------|----------------|------------|
| **Opening-to-Average Ratio** | 1.47x | 1.34x | **10% above median** |
| **Opening Day Cups** | 298 (half-day) | 506 (full-day avg) | -41% (due to half-day) |
| **Subsequent Days Avg** | 203 | 380 | -47% (smaller store) |
| **Trend Pattern** | Stable | 63% decline | **Much better — stable** |
| **Weeks of Data** | <1 week | 4-32 weeks | Limited data |

**Key Findings:**
1. **Opening ratio (1.47x) is close to the 8-store median (1.34x)** — consistent pattern
2. **21st & 3rd is a smaller store** (200-300 cups/day vs. 380 avg for 8-store fleet)
3. **No post-opening collapse:** Unlike 28th & 6th (2.19x opening, then -70% drop), this store is **stable**
4. **Half-day opening makes direct comparison difficult:** Need another Friday (Feb 13) data to confirm

---

## Daily Traffic Trend Chart

```
Daily Cup Count (21st & 3rd)

300 ┤        ● (Opening Day, Fri)                    ● (Tue)
    ┤       ╱│╲                                      ╱│╲
250 ┤      ╱ │ ╲                                    ╱ │ ╲
    ┤     ╱  │  ╲                                  ╱  │  ╲
200 ┤    ╱   │   ╲        ●                            │   ● (Wed)
    ┤   ╱    │    ╲      ╱│╲                           │  ╱│
150 ┤  ╱     │     ● ___╱ │ ╲___                       │╱  │
    ┤ ╱      │    ╱│╲      │      ● (Mon)              │   │
100 ┤╱       │   ╱ │ ╲     │     ╱│╲                   │   │
    ┤        │  ╱  │  ●    │    ╱ │ ╲                  │   │
 50 ┤        │ ╱   │ (Sun) │   ╱  │  ╲                 │   │
    ┼────────┴─────┴───────┴──────┴────────────────────┴───┴──
      Feb 6   Feb 7  Feb 8  Feb 9  Feb 10  Feb 11
      (Fri)   (Sat)  (Sun)  (Mon)  (Tue)   (Wed)
    OPENING  Weekend ←──→   Weekday Recovery

Legend:
● = Daily cup count
Fri (Opening, half-day): 298 cups
Sat-Sun (Weekend): 156, 145 cups
Mon-Wed (Weekdays): 208, 296, 201 cups (Wed incomplete)
```

**Visual Pattern:**
- **Opening day spike** (298 cups, but half-day)
- **Weekend dip** (Sat/Sun: 145-156 cups)
- **Weekday recovery** (Mon-Tue: 208-296 cups)
- **Stabilizing trend:** No collapse, maintaining 200-300 cups

---

## Recommendations

### For 21st & 3rd Store Management

1. **Continue monitoring Friday performance:** Get data for Feb 13 (full Friday) to establish baseline weekday traffic
2. **Weekend traffic optimization:** 145-156 cups on weekends is low — consider weekend promotions
3. **Evening traffic is growing:** 8-10 PM traffic increased after opening — capitalize on late-night crowd
4. **Stable performance is good:** Unlike stores with extreme opening boosts (28th & 6th at 2.19x), this store has **sustainable** traffic

### For Future Store Openings

1. **21st & 3rd pattern (1.47x opening ratio) is healthy:** Moderate opening boost without unsustainable hype
2. **Half-day opening worked well:** 298 cups in 12 hours = 596 cups/day run rate if full day — strong performance
3. **Weekday strength (200-300 cups) is promising:** Store should stabilize at 250-300 cups/day long-term
4. **No "novelty collapse":** Unlike 28th & 6th or 54th & 8th, this store maintained traffic after opening

---

## Data Limitations & Caveats

⚠️ **Statistical Significance:** Only **6 days of data** — not enough for robust trend analysis
⚠️ **Half-day opening:** Opening day started at 12 PM, not comparable to full 24-hour days
⚠️ **No Friday comparison yet:** Cannot compare opening Friday to next Friday (Feb 13 data needed)
⚠️ **Incomplete last day:** Feb 11 data only through 7:57 PM
⚠️ **No promotion data:** Unknown if opening day had special discounts/giveaways

**Follow-up needed:** Re-analyze after 4+ weeks of data (by March 6, 2026) to confirm trend

---

## Appendix: Raw Hourly Data

### Opening Day (Feb 6, Friday) — Full Breakdown
```
12 PM:  16 cups | ████████
 1 PM:  28 cups | ██████████████
 2 PM:  42 cups | █████████████████████
 3 PM:  19 cups | █████████
 4 PM:  59 cups | █████████████████████████████  ← PEAK
 5 PM:  29 cups | ██████████████
 6 PM:  36 cups | ██████████████████
 7 PM:  25 cups | ████████████
 8 PM:  16 cups | ████████
 9 PM:  14 cups | ███████
10 PM:   9 cups | ████
11 PM:   5 cups | ██
```

**Total:** 298 cups in 12 hours (12 PM - midnight)

---

**Analysis prepared by:** DBA/Analytics Team
**For:** Luckin USA Operations & China HQ Leadership
**Next update:** After 4 weeks of data (March 6, 2026)
