# Reserved Instance & Savings Plans Coverage Analysis

**Generated:** 2026-02-05
**Region:** us-east-1
**Analysis Period:** January 2026

---

## Executive Summary

### Critical Finding: SIGNIFICANT RI COVERAGE GAPS

Your organization has **no active Savings Plans** and multiple **expired Reserved Instances** resulting in substantial unnecessary spend.

| Metric | Value |
|--------|-------|
| Total Monthly Spend (Jan 2026) | **$49,644.91** |
| RI Covered | $24,935.72 (50.2%) |
| On-Demand (Uncovered) | **$24,709.19 (49.8%)** |
| Savings Plans | **$0 (0%)** |
| **Potential Monthly Savings** | **$3,457.87** |
| **Potential Annual Savings** | **$41,494.50** |

### ⚠️ URGENT: Expired RIs Detected

Multiple Reserved Instances have **EXPIRED** and are now running at full On-Demand rates:
- **RDS:** Most RIs expired - now paying 98.7% On-Demand
- **OpenSearch:** 3 of 4 RI reservations expired
- **ElastiCache:** Only 2 nodes covered out of ~50+ deployed

---

## Coverage by Service

| Service | Total Spend | RI Covered | On-Demand | Coverage % | Status |
|---------|-------------|------------|-----------|------------|--------|
| EC2 | $26,693.06 | $24,131.45 | $2,561.61 | 90.4% | ✅ Good |
| RDS | $5,527.28 | $69.19 | $5,458.09 | 1.3% | 🔴 Critical |
| ElastiCache | $2,313.84 | $151.78 | $2,162.06 | 6.6% | 🔴 Critical |
| OpenSearch | $2,646.52 | $583.30 | $2,063.22 | 22.0% | 🟡 Poor |

---

## Current EC2 Reserved Instances

**Status: ✅ Well Covered (90.4%)**

| Instance Type | Count | Hourly Rate | Monthly Cost | Platform | Expiration |
|---------------|-------|-------------|--------------|----------|------------|
| c6i.large | 129 | $0.05623 | $5,295.18 | Linux/UNIX | 2026-08-28 |
| c6i.xlarge | 26 | $0.11246 | $2,134.49 | Linux/UNIX | 2026-08-28 |
| c6i.xlarge | 3 | $0.29646 | $649.25 | Windows | 2026-08-28 |
| c6i.2xlarge | 7 | $0.22491 | $1,149.29 | Linux/UNIX | 2026-08-28 |
| c6i.4xlarge | 1 | $0.44982 | $328.37 | Linux/UNIX | 2026-08-28 |
| c5.large | 1 | $0.05400 | $39.42 | Linux/UNIX | 2026-08-28 |
| m6i.4xlarge | 7 | $0.50803 | $2,596.03 | Linux/UNIX | 2026-08-27 |
| m6i.8xlarge | 13 | $1.01606 | $9,642.41 | Linux/UNIX | 2026-08-27 |
| m6a.large | 3 | $0.05715 | $125.16 | Linux/UNIX | 2026-08-27 |
| m6a.xlarge | 2 | $0.11431 | $166.89 | Linux/UNIX | 2026-08-27 |
| m5.xlarge | 5 | $0.12100 | $441.65 | Linux/UNIX | 2026-08-27 |
| m4.large | 1 | $0.06200 | $45.26 | Linux/UNIX | 2026-08-28 |
| m4.xlarge | 1 | $0.12390 | $90.45 | Linux/UNIX | 2026-08-27 |
| r6i.2xlarge | 2 | $0.33340 | $486.76 | Linux/UNIX | 2026-08-28 |
| r6i.4xlarge | 1 | $0.66679 | $486.76 | Linux/UNIX | 2026-08-27 |

**Total EC2 RI Commitment:** $23,677.37/month

### EC2 On-Demand Gap Analysis

Instances currently running On-Demand (not covered by RI):

| Instance Type | Monthly On-Demand Cost | Action |
|---------------|------------------------|--------|
| c6i.2xlarge | $1,264.80 | Consider RI after rightsizing |
| c6i.xlarge | $642.74 | Consider RI after rightsizing |
| c6i.4xlarge | $505.92 | Consider RI after rightsizing |
| m5.xlarge | $102.03 | Consider RI after rightsizing |
| t3.large | $44.21 | Low priority |

---

## Current RDS Reserved Instances

**Status: 🔴 CRITICAL - Most RIs EXPIRED**

### Active RDS RIs

| Instance Class | Count | Engine | Multi-AZ | Monthly Cost | Expiration |
|---------------|-------|--------|----------|--------------|------------|
| db.t4g.medium | 1 | mysql | True | $67.89 | 2026-08-27 |

**Active RDS RI Coverage:** Only 1 db.t4g.medium (Multi-AZ)

### RDS On-Demand Gap Analysis (URGENT)

| Instance Class | Monthly On-Demand Cost | Priority | Note |
|---------------|------------------------|----------|------|
| db.r5.xlarge | $1,488.00 | 🔴 HIGH | RI expired - renew immediately |
| db.t4g.medium | $1,439.64 | 🔴 HIGH | RI expired - renew immediately |
| db.t4g.micro | $900.31 | 🟡 MEDIUM | RI expired - renew immediately |
| db.t4g.xlarge | $384.65 | 🟡 MEDIUM | RI expired - renew immediately |
| db.t4g.large | $383.90 | 🟡 MEDIUM | RI expired - renew immediately |
| db.m5.large | $264.86 | 🟡 MEDIUM | RI expired - renew immediately |
| db.t3.small | $80.10 | 🟡 MEDIUM | RI expired - renew immediately |

---

## Current ElastiCache Reserved Instances

**Status: 🔴 CRITICAL - Very Low Coverage (6.6%)**

### Active ElastiCache RIs

| Node Type | Count | Engine | Monthly Cost | Expiration |
|-----------|-------|--------|--------------|------------|
| cache.m6g.large | 2 | redis | $148.92 | 2026-08-27 |

### ElastiCache On-Demand Gap Analysis

| Node Type | Monthly On-Demand Cost | Priority |
|-----------|------------------------|----------|
| cache.t4g.micro | $1,535.62 | 🔴 HIGH |
| cache.t4g.small | $357.12 | 🟡 MEDIUM |
| cache.t4g.medium | $193.44 | 🟡 MEDIUM |
| cache.t3.micro | $75.89 | 🟡 MEDIUM |

---

## Current OpenSearch Reserved Instances

**Status: 🟡 Poor Coverage - Most RIs EXPIRED (22%)**

### Active OpenSearch RIs

| Instance Type | Count | Monthly Cost | Expiration |
|--------------|-------|--------------|------------|
| m5.large.search | 8 | $572.32 | 2026-08-27 |

**OpenSearch On-Demand Spend:** $2,063.22/month

---

## Savings Plans Status

**Status: ❌ NO ACTIVE SAVINGS PLANS**

You currently have **no Compute Savings Plans or EC2 Instance Savings Plans**.

### Savings Plans vs Reserved Instances

| Feature | Savings Plans | Reserved Instances |
|---------|---------------|-------------------|
| Flexibility | ✅ Any instance family/size | ❌ Fixed instance type |
| Cross-region | ✅ Yes | ❌ No |
| Cross-service | ✅ EC2 + Fargate + Lambda | ❌ EC2 only |
| Discount | ~30% (Compute SP) | ~30-40% |
| Commitment | $ per hour | Instance count |

**Recommendation:** Consider Compute Savings Plans for maximum flexibility, especially given your infrastructure optimization initiatives (Graviton migration, rightsizing).

---

## RI Utilization Analysis

Your **existing** EC2 RIs are being utilized excellently:

| Metric | Value |
|--------|-------|
| Utilization Rate | **100.00%** |
| Purchased Hours | 150,288 |
| Actual Hours Used | 150,283.53 |
| Unused Hours | 4.47 |
| Net RI Savings | $12,186.66 |

This indicates your EC2 RI purchases are correctly sized. The issue is **missing RI coverage for RDS, ElastiCache, and OpenSearch**.

---

## Purchase Recommendations

### 🚨 CRITICAL: Sequence Matters!

**ALWAYS rightsize BEFORE purchasing new RIs/Savings Plans!**

If you purchase RIs based on current instance types and then rightsize, your RIs may not match your new instances, resulting in wasted spend.

### Recommended Sequence

```
1. Complete Graviton migrations (RDS, OpenSearch, MSK)
2. Complete rightsizing analysis
3. Wait 30-60 days to establish new usage patterns
4. Purchase RIs/Savings Plans based on optimized infrastructure
```

### High-Priority RI Recommendations (Post-Optimization)

| Priority | Service | Instance Type | On-Demand Cost | Est. RI Savings | Annual Savings |
|----------|---------|---------------|----------------|-----------------|----------------|
| HIGH | OpenSearch | m5/m6g instances | $2,063.22 | $618.97/mo | $7,427.59/yr |
| HIGH | ElastiCache | cache.t4g.micro | $1,535.62 | $460.69/mo | $5,528.23/yr |
| HIGH | RDS | db.r5.xlarge | $1,488.00 | $446.40/mo | $5,356.80/yr |
| HIGH | RDS | db.t4g.medium | $1,439.64 | $431.89/mo | $5,182.70/yr |
| MEDIUM | EC2 | c6i.2xlarge | $1,264.80 | $379.44/mo | $4,553.28/yr |
| MEDIUM | RDS | db.t4g.micro | $900.31 | $270.09/mo | $3,241.12/yr |
| MEDIUM | EC2 | c6i.xlarge | $642.74 | $192.82/mo | $2,313.86/yr |
| MEDIUM | EC2 | c6i.4xlarge | $505.92 | $151.78/mo | $1,821.31/yr |
| MEDIUM | RDS | db.t4g.xlarge | $384.65 | $115.39/mo | $1,384.74/yr |
| MEDIUM | RDS | db.t4g.large | $383.90 | $115.17/mo | $1,382.04/yr |

**Total Potential Savings:** $3,457.87/month ($41,494.50/year)

---

## Savings Plans Recommendation

Given your:
1. **Active optimization initiatives** (Graviton, rightsizing, gp3)
2. **Multi-service infrastructure** (EC2, RDS, ElastiCache, OpenSearch, MSK)
3. **Need for flexibility** during migration

### Recommended Approach

| Phase | Timeline | Action |
|-------|----------|--------|
| Phase 1 | Now | Complete all Graviton migrations |
| Phase 2 | +30 days | Complete rightsizing |
| Phase 3 | +60 days | Purchase Compute Savings Plan (covers ~70% of steady-state EC2) |
| Phase 4 | +60 days | Purchase RDS RIs for stable instances |
| Phase 5 | +90 days | Evaluate ElastiCache/OpenSearch RIs |

### Why Compute Savings Plans?

After rightsizing and Graviton migration, your instance mix will change significantly. A **Compute Savings Plan** provides:

- **Flexibility:** Applies to ANY EC2 instance type, including Graviton
- **Fargate coverage:** If you expand to containers
- **Lambda coverage:** If you use serverless
- **No re-purchase needed** when changing instance types

---

## RI Expiration Calendar

### Upcoming Expirations (Next 12 Months)

| Service | Instance Type | Count | Expiration | Days Left | Action |
|---------|---------------|-------|------------|-----------|--------|
| EC2 | m6i.4xlarge | 7 | 2026-08-27 | 202 | Plan renewal (post-optimization) |
| EC2 | m6i.8xlarge | 13 | 2026-08-27 | 202 | Plan renewal (post-optimization) |
| EC2 | m6a.large | 3 | 2026-08-27 | 202 | Plan renewal (post-optimization) |
| EC2 | m6a.xlarge | 2 | 2026-08-27 | 202 | Plan renewal (post-optimization) |
| EC2 | m5.xlarge | 5 | 2026-08-27 | 202 | Plan renewal (post-optimization) |
| EC2 | m4.xlarge | 1 | 2026-08-27 | 202 | Plan renewal (post-optimization) |
| EC2 | r6i.4xlarge | 1 | 2026-08-27 | 202 | Plan renewal (post-optimization) |
| RDS | db.t4g.medium | 1 | 2026-08-27 | 202 | Plan renewal (post-optimization) |
| ElastiCache | cache.m6g.large | 2 | 2026-08-27 | 202 | Plan renewal (post-optimization) |
| OpenSearch | m5.large.search | 8 | 2026-08-27 | 202 | Plan renewal (post-optimization) |
| EC2 | c6i.large | 129 | 2026-08-28 | 203 | Plan renewal (post-optimization) |
| EC2 | c6i.xlarge | 26 | 2026-08-28 | 203 | Plan renewal (post-optimization) |
| EC2 | c6i.xlarge | 3 | 2026-08-28 | 203 | Plan renewal (post-optimization) |
| EC2 | c6i.2xlarge | 7 | 2026-08-28 | 203 | Plan renewal (post-optimization) |
| EC2 | c6i.4xlarge | 1 | 2026-08-28 | 203 | Plan renewal (post-optimization) |
| EC2 | c5.large | 1 | 2026-08-28 | 203 | Plan renewal (post-optimization) |
| EC2 | m4.large | 1 | 2026-08-28 | 203 | Plan renewal (post-optimization) |
| EC2 | r6i.2xlarge | 2 | 2026-08-28 | 203 | Plan renewal (post-optimization) |

---

## Cost Impact Summary

### Current State (January 2026)

| Category | Monthly Cost | % of Total |
|----------|-------------|------------|
| RI-Covered Spend | $24,935.72 | 50.2% |
| On-Demand Spend | $24,709.19 | 49.8% |
| Savings Plans | $0.00 | 0.0% |
| **Total** | **$49,644.91** | 100% |

### Projected State (After RI/SP Optimization)

| Category | Monthly Cost | % of Total | Change |
|----------|-------------|------------|--------|
| RI/SP-Covered Spend | ~$42,198.17 | ~85% | +35% |
| On-Demand Spend | ~$7,446.74 | ~15% | -35% |
| **Total** | **~$46,187.04** | 100% | -$3,457.87 |

### Combined Savings Opportunity

| Optimization | Monthly Savings | Annual Savings |
|--------------|-----------------|----------------|
| Graviton Migration (EC2) | Already covered by existing RIs | - |
| Graviton Migration (RDS) | $78.57 | $942.84 |
| Graviton Migration (OpenSearch) | $146.89 | $1,762.68 |
| Graviton Migration (MSK) | $219.40 | $2,632.79 |
| **RI/SP Coverage** | **$3,457.87** | **$41,494.50** |
| **Total** | **$3,902.73** | **$46,832.81** |

---

## Immediate Action Items

### 🔴 Week 1: Assessment

- [ ] Review this analysis with Finance team
- [ ] Confirm rightsizing and Graviton migration timelines
- [ ] Identify instances that will NOT change (stable candidates for immediate RI)

### 🟡 Week 2-4: Optimization Execution

- [ ] Complete Graviton migrations (RDS → r6g, OpenSearch → m6g, MSK → m7g)
- [ ] Complete EC2 rightsizing
- [ ] Wait for usage patterns to stabilize

### 🟢 Week 5-8: RI/SP Purchases

- [ ] Purchase Compute Savings Plan (~$15/hour commitment)
- [ ] Purchase RDS RIs for stable instances
- [ ] Evaluate ElastiCache Reserved Nodes
- [ ] Evaluate OpenSearch Reserved Instances

---

## Files Generated

- CSV Report: `/app/ri_sp_coverage_inventory.csv`
- Analysis Script: `/app/ri_sp_coverage_analysis.py`
- This Report: `/app/ri_sp_coverage_report.md`
