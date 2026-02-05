# OpenSearch Domain Optimization Analysis

**Generated:** 2026-02-05
**Region:** us-east-1
**EDP Discount Applied:** 31%

---

## Executive Summary

Your OpenSearch fleet has **1 of 4 domains already optimized** (luckyus-opensearch-dify). The remaining **3 domains** are candidates for Graviton migration and/or gp2→gp3 storage upgrades.

### Key Findings

| Metric | Value |
|--------|-------|
| Total Domains | 4 |
| Already Optimized | 1 (25%) |
| Optimization Candidates | 3 (75%) |
| **Monthly Savings Potential** | **$146.89** |
| **Annual Savings Potential** | **$1,762.68** |

### Savings Breakdown

| Category | Monthly Savings |
|----------|-----------------|
| Graviton Data Nodes (m5 → m6g) | $114.85 |
| gp2 → gp3 Storage | $32.04 |
| Graviton Master Nodes | $0.00 (t3 has no Graviton equivalent) |

---

## Domain Inventory

| Domain | Engine | Data Nodes | Master Nodes | Storage | UltraWarm | Cold |
|--------|--------|------------|--------------|---------|-----------|------|
| luckylfe-log | ES 7.10 | 4x m5.large.search | 3x t3.medium.search | gp2 80GB/node | No | No |
| luckycommon | ES 6.8 | 4x m5.large.search | 3x t3.small.search | gp3 100GB/node | No | No |
| luckyur-log | ES 7.10 | 4x m5.xlarge.search | 3x t3.medium.search | gp2 350GB/node | No | No |
| luckyus-opensearch-dify | OS 2.15 | 2x r6g.large.search | 3x m7g.large.search | gp3 30GB/node | No | No |

**Note:** None of your domains use UltraWarm or Cold Storage tiers.

---

## Optimization Opportunities

### Priority 1: luckyur-log (Highest Savings)

**Monthly Savings: $84.51 | Annual Savings: $1,014.12**

| Component | Current | Recommended | Savings/mo |
|-----------|---------|-------------|------------|
| Data Nodes | 4x m5.xlarge.search | 4x m6g.xlarge.search | $58.43 |
| Storage | gp2 350GB/node | gp3 350GB/node | $26.08 |
| Master Nodes | 3x t3.medium.search | (No change - t3 has no Graviton) | $0.00 |

**Current Metrics:**
- CPU: 16.5% avg, 90% max
- JVM Memory Pressure: 59.1% avg, 76.3% max (⚠️ approaching threshold)
- Free Storage: ~40GB/node minimum

**Risk Assessment:** MEDIUM
- Zone-aware (2 AZ), requires blue/green deployment
- High JVM pressure suggests memory-intensive workload; Graviton r6g may be better fit

### Priority 2: luckylfe-log

**Monthly Savings: $34.17 | Annual Savings: $410.04**

| Component | Current | Recommended | Savings/mo |
|-----------|---------|-------------|------------|
| Data Nodes | 4x m5.large.search | 4x m6g.large.search | $28.21 |
| Storage | gp2 80GB/node | gp3 80GB/node | $5.96 |
| Master Nodes | 3x t3.medium.search | (No change) | $0.00 |

**Current Metrics:**
- CPU: 8.2% avg, 43% max (healthy)
- JVM Memory Pressure: 45.3% avg, 75.5% max
- Free Storage: ~14GB/node minimum

**Risk Assessment:** MEDIUM
- Zone-aware (2 AZ), requires blue/green deployment

### Priority 3: luckycommon

**Monthly Savings: $28.21 | Annual Savings: $338.52**

| Component | Current | Recommended | Savings/mo |
|-----------|---------|-------------|------------|
| Data Nodes | 4x m5.large.search | 4x m6g.large.search | $28.21 |
| Storage | gp3 100GB/node | (Already gp3) | $0.00 |
| Master Nodes | 3x t3.small.search | (No change) | $0.00 |

**Current Metrics:**
- CPU: 12.4% avg, 77% max
- JVM Memory Pressure: 44.3% avg, 75.7% max
- Free Storage: ~36GB/node minimum

**Risk Assessment:** MEDIUM
- Zone-aware (2 AZ), requires blue/green deployment
- **Note:** Running Elasticsearch 6.8 (EOL) - consider upgrading to OpenSearch 2.x

---

## Already Optimized Domain

### luckyus-opensearch-dify

| Component | Configuration | Status |
|-----------|---------------|--------|
| Data Nodes | 2x r6g.large.search | ✅ Graviton |
| Master Nodes | 3x m7g.large.search | ✅ Graviton |
| Storage | gp3 30GB/node | ✅ gp3 |

**Monthly Cost:** $4.47 (fully optimized)

---

## CloudWatch Metrics Summary (7-day)

| Domain | Avg CPU | Max CPU | Avg JVM | Max JVM | Status |
|--------|---------|---------|---------|---------|--------|
| luckylfe-log | 8.2% | 43% | 45.3% | 75.5% | ✅ Healthy |
| luckycommon | 12.4% | 77% | 44.3% | 75.7% | ✅ Healthy |
| luckyur-log | 16.5% | 90% | 59.1% | 76.3% | ⚠️ High JVM |
| luckyus-opensearch-dify | 8.3% | 38% | 35.3% | 65.0% | ✅ Healthy |

**JVM Memory Pressure Thresholds:**
- <75%: Healthy
- 75-85%: Warning (GC overhead increasing)
- >85%: Critical (risk of circuit breaker)

---

## Migration Guide

### Step 1: Graviton Data Node Migration (Blue/Green)

OpenSearch uses a blue/green deployment for instance type changes:

```bash
# Example for luckyur-log
aws opensearch update-domain-config \
    --domain-name luckyur-log \
    --cluster-config '{
        "InstanceType": "m6g.xlarge.search",
        "InstanceCount": 4,
        "DedicatedMasterEnabled": true,
        "DedicatedMasterType": "t3.medium.search",
        "DedicatedMasterCount": 3,
        "ZoneAwarenessEnabled": true,
        "ZoneAwarenessConfig": {"AvailabilityZoneCount": 2}
    }'
```

**Expected Duration:** 30-60 minutes per domain

### Step 2: gp2 to gp3 Storage Migration

```bash
# Example for luckyur-log
aws opensearch update-domain-config \
    --domain-name luckyur-log \
    --ebs-options '{
        "EBSEnabled": true,
        "VolumeType": "gp3",
        "VolumeSize": 350,
        "Iops": 3000,
        "Throughput": 125
    }'
```

**Note:** gp2→gp3 migration can be done with zero downtime.

---

## Recommended Migration Order

| Order | Domain | Optimizations | Savings/mo | Rationale |
|-------|--------|---------------|------------|-----------|
| 1 | luckyur-log | Graviton + gp3 | $84.51 | Highest savings |
| 2 | luckylfe-log | Graviton + gp3 | $34.17 | Similar config, straightforward |
| 3 | luckycommon | Graviton only | $28.21 | Already on gp3, ES 6.8 upgrade needed |

---

## Additional Recommendations

### 1. Engine Version Upgrades

| Domain | Current | Recommended | Notes |
|--------|---------|-------------|-------|
| luckycommon | ES 6.8 | OpenSearch 2.x | ES 6.8 is EOL, significant security risk |
| luckylfe-log | ES 7.10 | OpenSearch 2.x | Consider after Graviton migration |
| luckyur-log | ES 7.10 | OpenSearch 2.x | Consider after Graviton migration |

### 2. Enable Auto-Tune

All domains have Auto-Tune disabled. Enable it for automatic JVM and cluster optimization:

```bash
aws opensearch update-domain-config \
    --domain-name <domain-name> \
    --auto-tune-options '{"DesiredState": "ENABLED"}'
```

### 3. Consider UltraWarm for Log Domains

For `luckylfe-log` and `luckyur-log`, consider UltraWarm storage for older indices:
- UltraWarm: ~$0.024/GB-month vs gp3: ~$0.108/GB-month
- Potential additional savings for infrequently accessed log data

### 4. Software Updates Available

All domains have pending software updates:

| Domain | Current | Available |
|--------|---------|-----------|
| luckylfe-log | ES 7.10 R20250625 | R20251106 |
| luckycommon | ES 6.8 R20250625 | R20251106 |
| luckyur-log | ES 7.10 R20250625 | R20251106 |
| luckyus-opensearch-dify | OS 2.15 R20250403 | R20251112-P2 |

---

## Cost Summary

### Current Monthly Costs (with 31% EDP)

| Domain | Data Nodes | Master Nodes | Storage | Total |
|--------|------------|--------------|---------|-------|
| luckyur-log | $571.68 | $110.01 | $131.23 | $812.92 |
| luckylfe-log | $285.84 | $110.01 | $29.97 | $425.82 |
| luckycommon | $285.84 | $79.44 | $29.97 | $395.25 |
| luckyus-opensearch-dify | $168.29 | $301.32* | $4.47 | $473.55 |
| **Total** | | | | **$2,107.54** |

*Note: luckyus-opensearch-dify shows higher master node cost due to m7g.large instances (larger than t3)

### Projected Monthly Costs (After Optimization)

| Domain | Data Nodes | Master Nodes | Storage | Total | Savings |
|--------|------------|--------------|---------|-------|---------|
| luckyur-log | $513.25 | $110.01 | $105.15 | $728.41 | $84.51 |
| luckylfe-log | $257.63 | $110.01 | $24.01 | $391.65 | $34.17 |
| luckycommon | $257.63 | $79.44 | $29.97 | $367.04 | $28.21 |
| luckyus-opensearch-dify | $168.29 | $301.32 | $4.47 | $473.55 | $0.00 |
| **Total** | | | | **$1,960.65** | **$146.89** |

---

## Files Generated

- CSV Report: `/app/opensearch_optimization_candidates.csv`
- Analysis Script: `/app/opensearch_optimization_analysis.py`
- This Report: `/app/opensearch_optimization_report.md`
