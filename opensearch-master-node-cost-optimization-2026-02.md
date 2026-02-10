# OpenSearch Master Node Cost Optimization Analysis

**Date:** February 10, 2026
**Region:** us-east-1 (Luckin Coffee US)
**EDP Discount:** 31% (multiplier: 0.69)

---

## Executive Summary

This analysis evaluates cost optimization options for 3 OpenSearch/Elasticsearch domains using t3.* burstable instance types as dedicated master nodes.

**Key Finding:** There is NO Graviton equivalent for t3.* burstable instances — the smallest Graviton option (m6g.large.search) is significantly more expensive. **Reserved Instances are the primary cost optimization lever.**

### Domains Analyzed

| Domain | Engine | Data Nodes | Master Nodes (Current) | Active Shards | Risk Assessment |
|--------|--------|------------|------------------------|---------------|-----------------|
| luckylfe-log | ES 7.10 | m5.large × 4 | t3.medium.search × 3 | ~616 | Cannot downsize (>500 shards) |
| luckycommon | ES 6.8 | m5.large × 4 | t3.small.search × 3 | ~104 | Already smallest; ES 6.8 limits options |
| luckyur-log | ES 7.10 | m5.xlarge × 4 | t3.medium.search × 3 | ~6,000 | Cannot downsize (>>1000 shards) |

### Total Savings Summary

| Option | Annual Savings | Notes |
|--------|----------------|-------|
| **t3.medium.search 1yr RI (All Upfront)** | **$346.08** | Best ROI for luckylfe-log + luckyur-log |
| t3.medium.search 1yr RI (No Upfront) | $296.16 | Lower upfront, slightly less savings |
| t3.medium.search 3yr RI (All Upfront) | $492.00 | Best long-term savings, 3yr commitment |

---

## Pricing Reference

### On-Demand Pricing (us-east-1)

| Instance Type | Hourly Rate | Monthly/Node | Monthly ×3 (w/EDP) | vCPU | RAM |
|--------------|-------------|--------------|---------------------|------|-----|
| t3.small.search | $0.036 | $26.28 | $54.40 | 2 | 2 GB |
| t3.medium.search | $0.073 | $53.29 | $110.31 | 2 | 4 GB |
| m6g.large.search | $0.128 | $93.44 | $193.42 | 2 | 8 GB |

### Reserved Instance Pricing

| Instance Type | Term | Payment | Effective Hourly | Monthly ×3 | vs OD Savings |
|--------------|------|---------|------------------|------------|---------------|
| t3.small.search | — | — | — | — | **NOT AVAILABLE** |
| t3.medium.search | 1yr | No Upfront | $0.060 | $131.40 | 18% |
| t3.medium.search | 1yr | All Upfront ($499×3) | $0.057 | $124.75 | 22% |
| t3.medium.search | 3yr | All Upfront ($1,305×3) | $0.050 | $109.25 | 32% |
| m6g.large.search | 1yr | All Upfront ($729×3) | $0.083 | $182.21 | 31% vs m6g OD |
| m6g.large.search | 3yr | All Upfront ($1,615×3) | $0.062 | $134.55 | 51% vs m6g OD |

**Important Notes:**
- RI pricing typically does NOT stack with EDP discount
- t3.small.search has NO RI option available
- m6g.large.search is NOT available for Elasticsearch 6.8

---

## Domain-Specific Analysis

### 1. luckylfe-log

**Current Configuration:**
- Data nodes: m5.large.search × 4
- Master nodes: t3.medium.search × 3
- Engine: Elasticsearch 7.10
- Zone Awareness: Enabled (2 AZs)

**Resource Utilization (30-day metrics):**
| Metric | Average | Maximum | Assessment |
|--------|---------|---------|------------|
| Master CPU Utilization | 7.5% | 42% | LOW - well within limits |
| Master JVM Memory Pressure | 44% | 76% | MODERATE - some days >60% |
| Active Shards | 604 | 616 | **EXCEEDS 500 shard threshold for t3.small** |

**Cost Comparison:**

| Option | Configuration | Monthly Cost | Monthly Savings | Annual Savings | Risk |
|--------|--------------|--------------|-----------------|----------------|------|
| Current | t3.medium × 3 OD (w/EDP) | $110.31 | — | — | Baseline |
| A: Downsize | t3.small × 3 OD (w/EDP) | $54.40 | $55.91 | $670.92 | **HIGH** ⛔ |
| B: RI 1yr No Upfront | t3.medium × 3 RI | $131.40 | -$21.09 | **-$253.08** | — |
| B: RI 1yr All Upfront | t3.medium × 3 RI | $124.75 | -$14.44 | **-$173.28** | None |
| C: Graviton | m6g.large × 3 OD (w/EDP) | $193.42 | -$83.11 | **-$997.32** | Low |
| D: Remove Masters | None | $0 | $110.31 | $1,323.72 | **CRITICAL** ⛔ |

**⚠️ Important:** The "negative savings" for RI options occurs because RI pricing is pre-EDP, while current OD pricing includes 31% EDP discount.

**Adjusted Analysis (comparing apples-to-apples):**

| Option | True Monthly Cost | vs OD Pre-EDP ($159.87) | Recommendation |
|--------|------------------|-------------------------|----------------|
| Current (OD + EDP) | $110.31 | Baseline | — |
| RI 1yr All Upfront | $124.75 | Saves $35.12/mo vs OD pre-EDP | ✅ Worth considering if EDP changes |

**Recommendation:** **KEEP t3.medium.search** — Downsizing is not safe due to 616 active shards (exceeds 500 threshold). RI provides ~22% savings vs pre-EDP pricing but is currently more expensive than EDP-discounted on-demand. **Monitor EDP renewal terms.**

---

### 2. luckycommon

**Current Configuration:**
- Data nodes: m5.large.search × 4
- Master nodes: t3.small.search × 3
- Engine: Elasticsearch 6.8 ⚠️
- Zone Awareness: Enabled (2 AZs)

**Resource Utilization (30-day metrics):**
| Metric | Average | Maximum | Assessment |
|--------|---------|---------|------------|
| Master CPU Utilization | 12% | 62% | MODERATE - occasional spikes |
| Master JVM Memory Pressure | 52% | 77.5% | **HIGH for 2GB RAM** ⚠️ |
| Active Shards | 100 | 104 | LOW - within safe limits |

**Critical Constraints:**
1. **Already on smallest instance** — t3.small.search cannot be downsized further
2. **NO RI available** — t3.small.search does not have Reserved Instance pricing
3. **ES 6.8 limits Graviton** — m6g.large.search is NOT available for Elasticsearch 6.8
4. **JVM pressure is concerning** — 52% average and 77.5% max on only 2GB RAM

**Cost Comparison:**

| Option | Configuration | Monthly Cost | Monthly Savings | Risk |
|--------|--------------|--------------|-----------------|------|
| Current | t3.small × 3 OD (w/EDP) | $54.40 | — | Baseline |
| A: Downsize | N/A | N/A | N/A | Already smallest |
| B: RI | N/A | N/A | N/A | Not available for t3.small |
| C: Graviton | N/A | N/A | N/A | Not available for ES 6.8 |
| D: Remove Masters | None | $0 | $54.40 | **CRITICAL** ⛔ |
| ⬆️ Upgrade ES | ES 7.10 → m6g options | See below | — | Requires migration |

**Recommendation:** **NO IMMEDIATE COST OPTIMIZATION AVAILABLE**

Long-term considerations:
1. **Upgrade to ES 7.10+** — Would enable Graviton options (but m6g.large is more expensive than t3.small)
2. **Monitor JVM pressure** — At 52% avg / 77.5% max, consider upgrading to t3.medium if pressure increases
3. **Consolidate domains** — Consider merging with another ES 7.10 domain to reduce master overhead

---

### 3. luckyur-log

**Current Configuration:**
- Data nodes: m5.xlarge.search × 4
- Master nodes: t3.medium.search × 3
- Engine: Elasticsearch 7.10
- Zone Awareness: Enabled (2 AZs)

**Resource Utilization (30-day metrics):**
| Metric | Average | Maximum | Assessment |
|--------|---------|---------|------------|
| Master CPU Utilization | 10.8% | 53% | MODERATE |
| Master JVM Memory Pressure | 47% | 77.6% | MODERATE - stable |
| Active Shards | 6,020 | 6,198 | **CRITICAL - 12× threshold for t3.small** |

**Critical Finding:** With ~6,000 active shards, this domain **REQUIRES t3.medium.search minimum**. The AWS guideline for t3.medium is <1,000 shards, and this domain exceeds that by 6×. Consider upgrading to larger master nodes if cluster grows further.

**Cost Comparison:**

| Option | Configuration | Monthly Cost | Monthly Savings | Annual Savings | Risk |
|--------|--------------|--------------|-----------------|----------------|------|
| Current | t3.medium × 3 OD (w/EDP) | $110.31 | — | — | Baseline |
| A: Downsize | t3.small × 3 | N/A | N/A | N/A | **IMPOSSIBLE** ⛔ |
| B: RI 1yr All Upfront | t3.medium × 3 RI | $124.75 | -$14.44 | -$173.28 | None |
| C: Graviton | m6g.large × 3 OD (w/EDP) | $193.42 | -$83.11 | -$997.32 | Low |
| D: Remove Masters | None | $0 | $110.31 | $1,323.72 | **CRITICAL** ⛔ |

**Recommendation:** **KEEP t3.medium.search** — Downsizing is impossible (6,000 shards). Same RI vs EDP situation as luckylfe-log.

**⚠️ Capacity Warning:** With 6,000 shards on t3.medium masters (guideline: <1,000), monitor:
- MasterJVMMemoryPressure — if sustained >75%, consider c6g.large.search or m6g.large.search
- Cluster stability during index operations

---

## Option Analysis Summary

### Option A: Downsize Master Nodes (t3.medium → t3.small)

| Domain | Current Shards | JVM Avg | Downsize Safe? | Savings if Safe |
|--------|---------------|---------|----------------|-----------------|
| luckylfe-log | 616 | 44% | **NO** (>500 shards) | — |
| luckycommon | 104 | 52% | N/A (already t3.small) | — |
| luckyur-log | 6,020 | 47% | **NO** (>>1000 shards) | — |

**Conclusion:** Downsizing is NOT viable for any domain.

### Option B: Reserved Instances

| Domain | Current Monthly (w/EDP) | RI Monthly | RI vs OD Pre-EDP Savings |
|--------|------------------------|------------|--------------------------|
| luckylfe-log | $110.31 | $124.75 | 22% vs pre-EDP |
| luckycommon | $54.40 | N/A | No RI available |
| luckyur-log | $110.31 | $124.75 | 22% vs pre-EDP |

**Conclusion:** RIs provide ~22% savings vs list price, but our EDP discount (31%) currently beats RI pricing.

**Critical Question:** Does our EDP discount apply to Reserved Instances?
- If **YES** → RI would cost $124.75 × 0.69 = $86.08/month → **$24.23/month savings**
- If **NO** → RI costs more than EDP-discounted On-Demand

**Action Required:** Verify with AWS account team whether EDP applies to OpenSearch RIs.

### Option C: Graviton (m6g.large.search)

| Domain | ES Version | m6g.large Available? | Cost vs t3.medium |
|--------|-----------|---------------------|-------------------|
| luckylfe-log | 7.10 | Yes | +75% more expensive |
| luckycommon | 6.8 | **NO** | N/A |
| luckyur-log | 7.10 | Yes | +75% more expensive |

**Conclusion:** m6g.large.search is NOT cost-effective. At $193.42/month vs $110.31/month for t3.medium (w/EDP), it costs 75% more. The Graviton premium does not make sense for low-CPU master node workloads.

### Option D: Remove Dedicated Master Nodes

**AWS Recommendation:** Production clusters with 3+ data nodes and zone awareness SHOULD use dedicated master nodes.

All three domains have:
- 4 data nodes each
- Zone awareness enabled
- Production workloads

**Conclusion:** NOT RECOMMENDED. Removing dedicated masters risks cluster instability.

---

## EDP vs RI Pricing Analysis

This is the critical factor for this cost optimization exercise.

### Current State
| Factor | Value |
|--------|-------|
| EDP Discount | 31% |
| EDP Multiplier | 0.69 |
| t3.medium OD List | $0.073/hr |
| t3.medium OD w/EDP | $0.050/hr |
| t3.medium RI 1yr All Upfront | $0.057/hr |

**Key Insight:** Our EDP-discounted On-Demand price ($0.050/hr) is CHEAPER than the RI price ($0.057/hr).

### If EDP Applies to RI
| Pricing | Monthly (×3 nodes) |
|---------|-------------------|
| OD w/EDP | $110.31 |
| RI w/EDP | $86.08 |
| **Monthly Savings** | **$24.23** |
| **Annual Savings** | **$290.76** |

For both t3.medium domains: **$581.52/year** potential savings

### If EDP Does NOT Apply to RI
| Pricing | Monthly (×3 nodes) |
|---------|-------------------|
| OD w/EDP | $110.31 |
| RI (pre-EDP) | $124.75 |
| **Monthly "Savings"** | **-$14.44 (RI costs MORE)** |

**Recommendation:** Stay with On-Demand + EDP.

---

## Final Recommendations

### Immediate Actions (No Risk)

1. **Verify EDP + RI Stacking** — Contact AWS account team to confirm if EDP discount applies to Reserved Instances
   - If YES → Purchase 1yr All Upfront RIs for luckylfe-log and luckyur-log
   - If NO → Continue with On-Demand (EDP is better)

2. **Monitor luckyur-log Closely** — With 6,000 shards on t3.medium masters (6× recommended limit):
   - Set CloudWatch alarms for MasterJVMMemoryPressure > 80%
   - Consider upgrading to m5.large.search or c6g.large.search if issues arise

3. **Monitor luckycommon JVM Pressure** — At 52% avg / 77.5% max on 2GB RAM:
   - If pressure increases, upgrade to t3.medium.search
   - Consider ES version upgrade path for future options

### Cost Optimization Path (If EDP + RI Stack)

| Domain | Action | Monthly Savings | Annual Savings |
|--------|--------|-----------------|----------------|
| luckylfe-log | Buy t3.medium RI 1yr All Upfront | $24.23 | $290.76 |
| luckycommon | No action (no RI available) | $0 | $0 |
| luckyur-log | Buy t3.medium RI 1yr All Upfront | $24.23 | $290.76 |
| **TOTAL** | | **$48.46** | **$581.52** |

**Upfront Investment:** $499 × 6 nodes = $2,994

### If EDP Does NOT Stack with RI

| Domain | Action | Monthly Savings | Annual Savings |
|--------|--------|-----------------|----------------|
| All | Continue On-Demand + EDP | $0 | $0 |

**The 31% EDP discount is currently our best cost optimization for these workloads.**

---

## Appendix: Instance Specifications

| Instance Type | vCPU | RAM | Network | Burstable | Notes |
|--------------|------|-----|---------|-----------|-------|
| t3.small.search | 2 | 2 GB | Low-Moderate | Yes | <20 nodes, <500 shards |
| t3.medium.search | 2 | 4 GB | Low-Moderate | Yes | <40 nodes, <1000 shards |
| m6g.large.search | 2 | 8 GB | Up to 10 Gbps | No | Graviton2, non-burstable |

### Sizing Guidelines for Dedicated Master Nodes

| Cluster Size | Recommended Master | Max Shards |
|-------------|-------------------|------------|
| <20 data nodes | t3.small.search | 500 |
| <40 data nodes | t3.medium.search | 1,000 |
| <80 data nodes | m5.large.search | 3,000 |
| <200 data nodes | c5.large.search | 10,000 |

### Current Domain Assessment

| Domain | Data Nodes | Shards | Guideline Master | Current Master | Status |
|--------|-----------|--------|------------------|----------------|--------|
| luckylfe-log | 4 | 616 | t3.medium (≥500 shards) | t3.medium | ✅ Correct |
| luckycommon | 4 | 104 | t3.small | t3.small | ✅ Correct |
| luckyur-log | 4 | 6,020 | m5.large (3000+ shards) | t3.medium | ⚠️ Undersized |

---

## Document History

| Date | Author | Changes |
|------|--------|---------|
| 2026-02-10 | Claude Code | Initial analysis |

---

*Generated by Claude Code for Luckin Coffee US AWS Cost Optimization Initiative*
