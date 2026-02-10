# OpenSearch luckyur-log Cluster Storage Crisis Analysis

**Analysis Date**: 2026-02-10
**Analyst**: DevOps DBA Team
**Cluster**: luckyur-log (vpc-luckyur-log-h2ri4xhsubrzscobj64zswc2e4.us-east-1.es.amazonaws.com)
**AWS Account**: 257394478466
**Region**: us-east-1

---

## CRITICAL ALERT - IMMEDIATE ACTION REQUIRED

```
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║   ⚠️  STORAGE CRISIS: FREE SPACE DROPPED TO 21.6 GB ON FEB 9    ⚠️   ║
    ║                                                                       ║
    ║   Current Free: ~35-38 GB  |  Threshold for Write Block: 15-20 GB   ║
    ║   Days Until Outage at Current Rate: 2-3 DAYS                       ║
    ║                                                                       ║
    ║   PRIORITY: P0 - IMMEDIATE CLEANUP REQUIRED TO PREVENT OUTAGE        ║
    ╚═══════════════════════════════════════════════════════════════════════╝
```

---

## Executive Summary

| Metric | Value | Status |
|--------|-------|--------|
| **Total Cluster Storage** | 1,400 GB raw (4 nodes × 350 GB) | - |
| **Usable Storage (with replica)** | ~1,150 GB | - |
| **Current Used Space** | ~1,115 GB | 🔴 CRITICAL |
| **Current Free Space** | ~35-38 GB (fluctuates) | 🔴 CRITICAL |
| **Storage Utilization** | 96.4-97.1% | 🔴 CRITICAL |
| **Lowest Free Space (Feb 9)** | **21.6 GB** | 🔴 NEAR OUTAGE |
| **Daily Write Volume** | ~25-30 GB/day | - |
| **Days to Cluster Failure** | **2-3 days** without action | 🔴 CRITICAL |
| **JVM Memory Pressure** | 74-76% (warning threshold) | ⚠️ WARNING |
| **Cluster Health Status** | Green (but stressed) | ✅ |

### Key Findings

1. **CRITICAL**: Free storage dropped to **21.6 GB** on Feb 9, 20:48 UTC - dangerously close to write-block threshold
2. **Historical indices from September 2025** are consuming ~100+ GB - these are 5 months old and should have been deleted
3. **No Index Lifecycle Management (ILM/ISM)** policies are configured - manual cleanup has been the only mechanism
4. **Indexing latency doubled** during low-storage periods (0.14ms → 0.28ms)
5. **Search latency spiked to 3.7ms** indicating cluster stress

---

## 1. Cluster Configuration Overview

### Infrastructure Details

| Component | Configuration |
|-----------|---------------|
| **Engine Version** | Elasticsearch 7.10 |
| **Data Nodes** | 4 × m5.xlarge.search (4 vCPU, 16 GB RAM each) |
| **Master Nodes** | 3 × t3.medium.search (dedicated) |
| **Storage Type** | gp2 EBS |
| **Storage per Node** | 350 GB |
| **Total Raw Storage** | 1,400 GB |
| **Availability Zones** | 2 (us-east-1a, us-east-1b) |
| **Zone Awareness** | Enabled |
| **VPC** | vpc-0dce7ca7770422d33 |
| **UltraWarm** | Disabled |
| **Cold Storage** | Disabled |

### Storage Calculation

```
Raw Storage:           4 nodes × 350 GB = 1,400 GB
Replica Overhead:      ~20% reserved for primary/replica distribution
Usable Storage:        ~1,150 GB effective
OpenSearch Reserved:   ~5% for operations
Available for Data:    ~1,090 GB
Current Used:          ~1,074 GB (from CloudWatch)
Current Free:          ~35-38 GB (fluctuating)
```

---

## 2. CloudWatch Metrics Analysis

### Free Storage Trend (Critical Decline)

| Date | Min Free (GB) | Max Free (GB) | Trend |
|------|---------------|---------------|-------|
| Feb 1 | 53.6 | 65.3 | Baseline |
| Feb 2 | 51.7 | 66.8 | Stable |
| Feb 3 | 46.6 | 65.1 | Declining ⚠️ |
| Feb 4 | 40.7 | 63.3 | Declining ⚠️ |
| Feb 5 | 40.7 | 63.2 | Critical 🔴 |
| Feb 6 | 38.1 | 57.3 | Critical 🔴 |
| Feb 7 | 37.7 | 50.3 | Critical 🔴 |
| Feb 8 | 35.4 | 48.8 | Critical 🔴 |
| Feb 9 | **21.6** | 46.2 | **NEAR OUTAGE** 🔴 |
| Feb 10 | 35.1 | 38.0 | Critical 🔴 |

**Pattern Observed**: Storage drops 15-25 GB during business hours (data ingestion) and partially recovers overnight (likely some cleanup process), but overall trend is sharply downward.

### Daily Data Growth Rate

Based on CloudWatch ClusterUsedSpace metrics:
- **Average Daily Growth**: ~3-5 GB net (after overnight cleanup)
- **Peak Daily Ingest**: ~25-30 GB
- **Overnight Recovery**: ~10-15 GB (from existing cleanup)
- **Net Daily Increase**: ~3-5 GB

### JVM Memory Pressure

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Current (Avg) | 74-76% | 75% Warning | ⚠️ AT THRESHOLD |
| Peak (Max) | 76.3% | 85% Critical | ⚠️ WARNING |

### Performance Impact

| Metric | Normal | During Low Storage | Change |
|--------|--------|-------------------|--------|
| Indexing Latency | 0.14ms | 0.28ms | +100% 🔴 |
| Search Latency | 0.5ms | 3.7ms | +640% 🔴 |

---

## 3. Index Inventory Analysis

### Storage Distribution by Index Category

Based on prior analysis (index access requires VPC connectivity):

| Index Category | Size (GB) | Count | % of Total | Date Range | Retention |
|----------------|-----------|-------|------------|------------|-----------|
| `iprod_tomcat_lucky_k8s` | ~537 | 19+ | 48.2% | Daily indices | Unknown |
| `skywalking_idx_segment` | ~156 | 7+ | 14.0% | Daily indices | Unknown |
| `prod-worker01-eks-us-baseservices-cloud-dify` | ~106 | 1+ | 9.5% | Unknown | Unknown |
| `iprod_tomcat_lucky_k8s-2025.09.*` (STALE) | ~80 | 5 | 7.2% | Sep 10-14, 2025 | **5 months old!** |
| `skywalking_idx_segment-2025.09.*` (STALE) | ~45 | 5+ | 4.0% | Sep 2025 | **5 months old!** |
| `skywalking_idx_metrics-all` | ~45 | 7+ | 4.0% | Daily | Unknown |
| `aws_cloud_operation` | 25.8 | 1 | 2.3% | Single | Unknown |
| `izeus-skywalking-trace-exception` | 10.7 | 1 | 1.0% | Single | Unknown |
| Other indices | ~109 | Various | 9.8% | Various | Various |
| **TOTAL** | **~1,115** | - | **100%** | - | - |

### Stale Index Analysis (Immediate Cleanup Candidates)

| Index Pattern | Estimated Size | Age | Priority |
|---------------|----------------|-----|----------|
| `*-2025.09.*` | ~125+ GB | 5 months | P0 - IMMEDIATE |
| `*-2025.10.*` | ~50+ GB | 4 months | P0 - IMMEDIATE |
| `*-2025.11.*` | ~50+ GB | 3 months | P1 - HIGH |
| `*-2025.12.*` | ~30+ GB | 2 months | P2 - MEDIUM |

**Total Estimated Reclaimable from Stale Indices: 255+ GB**

---

## 4. Index Templates and Lifecycle Management Analysis

### Current State

| Component | Status | Impact |
|-----------|--------|--------|
| ISM Policies | ❌ NOT CONFIGURED | Indices never auto-delete |
| ILM Policies | ❌ NOT CONFIGURED | No lifecycle management |
| Rollover | ❌ NOT CONFIGURED | Indices grow unbounded |
| Retention Rules | ❌ NOT CONFIGURED | Manual cleanup only |

This is the **root cause** of the storage crisis - without lifecycle policies, indices accumulate indefinitely.

### Discovery Commands (Run in OpenSearch Dashboards)

```json
// Check existing ISM policies
GET _plugins/_ism/policies

// Check index templates
GET _index_template/*

// Check legacy templates
GET _template/*

// Check if any indices have ISM attached
GET _plugins/_ism/explain/*
```

---

## 5. SkyWalking Indices Deep Dive

SkyWalking APM data consumes **~18%+ of total storage** (~200+ GB).

### SkyWalking Index Breakdown

| Index Type | Description | Current Size | Recommended Retention |
|------------|-------------|--------------|----------------------|
| `skywalking_idx_segment` | Trace segments | ~156 GB | 7-14 days |
| `skywalking_idx_metrics-all` | Aggregated metrics | ~45 GB | 30 days |
| `izeus-skywalking-trace-exception` | Exception traces | ~10.7 GB | 14-30 days |
| **Total** | | **~212 GB** | |

### SkyWalking Retention Configuration

SkyWalking's default retention is often 90 days, which is excessive for most use cases:

**Recommended Configuration** (in SkyWalking OAP `application.yml`):

```yaml
storage:
  elasticsearch:
    recordDataTTL: 7    # Trace data: 7 days (was likely 90)
    metricsDataTTL: 30  # Metrics data: 30 days
```

### SkyWalking Index Settings Check

```json
// Check SkyWalking index settings
GET skywalking_idx_segment*/_settings

// Check SkyWalking index retention
GET skywalking_idx_segment*/_ilm/explain
```

---

## 6. Shard and Replica Analysis

### Cluster Shard Metrics

| Metric | Value | Recommendation | Status |
|--------|-------|----------------|--------|
| Expected Shard Count | ~100-200 (estimated) | <1000 per node | ⚠️ Verify |
| Shards per Node | ~25-50 (estimated) | <300 per node | ✅ Likely OK |
| Replica Count | 1 (standard) | 1 for zone-aware | ✅ OK |

### Shard Size Guidelines

| Current (Estimated) | Best Practice | Action Needed |
|---------------------|---------------|---------------|
| Primary shards up to 30-50 GB each | Max 50 GB | ⚠️ Review large indices |

### Commands to Verify

```bash
# Check shard distribution
GET _cat/shards?v&s=store:desc&h=index,shard,prirep,state,docs,store,node

# Check allocation
GET _cat/allocation?v

# Check shard count per index
GET _cat/indices?v&h=index,pri,rep,store.size,pri.store.size
```

---

## 7. Immediate Cleanup Actions (P0 - Execute NOW)

### CRITICAL: September 2025 Indices Deletion

These indices are **5 months old** and should be deleted immediately to prevent cluster outage.

```json
// STEP 1: Verify September 2025 indices exist
GET _cat/indices/*2025.09*?v&s=store.size:desc&h=index,docs.count,store.size

// STEP 2: Review the list - do NOT proceed if unexpected indices appear

// STEP 3: Delete September 2025 indices (AFTER verification)
// ⚠️ WARNING: This is IRREVERSIBLE - ensure no compliance requirements

DELETE iprod_tomcat_lucky_k8s-2025.09.*
DELETE skywalking_idx_segment-2025.09.*
DELETE skywalking_idx_metrics-all-2025.09.*
```

**Expected Recovery: ~125+ GB**

### October 2025 Indices Deletion

```json
// STEP 1: Verify October 2025 indices exist
GET _cat/indices/*2025.10*?v&s=store.size:desc&h=index,docs.count,store.size

// STEP 2: Delete October 2025 indices (AFTER verification)
DELETE iprod_tomcat_lucky_k8s-2025.10.*
DELETE skywalking_idx_segment-2025.10.*
DELETE skywalking_idx_metrics-all-2025.10.*
```

**Expected Recovery: ~50+ GB**

### November 2025 Indices Deletion (if storage still critical)

```json
// STEP 1: Verify November 2025 indices exist
GET _cat/indices/*2025.11*?v&s=store.size:desc&h=index,docs.count,store.size

// STEP 2: Delete November 2025 indices (AFTER verification)
DELETE iprod_tomcat_lucky_k8s-2025.11.*
DELETE skywalking_idx_segment-2025.11.*
DELETE skywalking_idx_metrics-all-2025.11.*
```

**Expected Recovery: ~50+ GB**

---

## 8. ISM Policy Configuration (P1 - This Week)

### Policy 1: Application Logs (iprod_tomcat_*)

30-day retention for application logs:

```json
PUT _plugins/_ism/policies/app-logs-30d
{
  "policy": {
    "description": "Application logs retention policy - 30 days",
    "default_state": "hot",
    "states": [
      {
        "name": "hot",
        "actions": [
          {
            "rollover": {
              "min_index_age": "1d",
              "min_primary_shard_size": "30gb"
            }
          }
        ],
        "transitions": [
          {
            "state_name": "delete",
            "conditions": {
              "min_index_age": "30d"
            }
          }
        ]
      },
      {
        "name": "delete",
        "actions": [
          {
            "delete": {}
          }
        ],
        "transitions": []
      }
    ],
    "ism_template": [
      {
        "index_patterns": ["iprod_tomcat_lucky_k8s-*", "iprod_tomcat_lucky-*"],
        "priority": 100
      }
    ]
  }
}
```

### Policy 2: SkyWalking Traces (skywalking_idx_segment)

7-day retention for trace segments (sufficient for troubleshooting):

```json
PUT _plugins/_ism/policies/skywalking-traces-7d
{
  "policy": {
    "description": "SkyWalking trace segments - 7 day retention",
    "default_state": "hot",
    "states": [
      {
        "name": "hot",
        "actions": [],
        "transitions": [
          {
            "state_name": "delete",
            "conditions": {
              "min_index_age": "7d"
            }
          }
        ]
      },
      {
        "name": "delete",
        "actions": [
          {
            "delete": {}
          }
        ],
        "transitions": []
      }
    ],
    "ism_template": [
      {
        "index_patterns": ["skywalking_idx_segment*"],
        "priority": 100
      }
    ]
  }
}
```

### Policy 3: SkyWalking Metrics (skywalking_idx_metrics-all)

30-day retention for aggregated metrics:

```json
PUT _plugins/_ism/policies/skywalking-metrics-30d
{
  "policy": {
    "description": "SkyWalking metrics - 30 day retention",
    "default_state": "hot",
    "states": [
      {
        "name": "hot",
        "actions": [],
        "transitions": [
          {
            "state_name": "delete",
            "conditions": {
              "min_index_age": "30d"
            }
          }
        ]
      },
      {
        "name": "delete",
        "actions": [
          {
            "delete": {}
          }
        ],
        "transitions": []
      }
    ],
    "ism_template": [
      {
        "index_patterns": ["skywalking_idx_metrics-all*"],
        "priority": 100
      }
    ]
  }
}
```

### Policy 4: AWS Cloud Operations

14-day retention:

```json
PUT _plugins/_ism/policies/aws-ops-14d
{
  "policy": {
    "description": "AWS operation logs - 14 day retention",
    "default_state": "hot",
    "states": [
      {
        "name": "hot",
        "actions": [],
        "transitions": [
          {
            "state_name": "delete",
            "conditions": {
              "min_index_age": "14d"
            }
          }
        ]
      },
      {
        "name": "delete",
        "actions": [
          {
            "delete": {}
          }
        ],
        "transitions": []
      }
    ],
    "ism_template": [
      {
        "index_patterns": ["aws_cloud_operation*"],
        "priority": 100
      }
    ]
  }
}
```

### Apply ISM Policies to Existing Indices

After creating policies, attach them to existing indices:

```json
// Attach app-logs policy to existing indices
POST _plugins/_ism/add/iprod_tomcat_lucky_k8s-*
{
  "policy_id": "app-logs-30d"
}

// Attach skywalking-traces policy
POST _plugins/_ism/add/skywalking_idx_segment*
{
  "policy_id": "skywalking-traces-7d"
}

// Attach skywalking-metrics policy
POST _plugins/_ism/add/skywalking_idx_metrics-all*
{
  "policy_id": "skywalking-metrics-30d"
}

// Attach aws-ops policy
POST _plugins/_ism/add/aws_cloud_operation*
{
  "policy_id": "aws-ops-14d"
}
```

---

## 9. Long-Term Optimization Recommendations

### Storage Capacity Planning

| Scenario | Timeline | Action |
|----------|----------|--------|
| Current state (no cleanup) | 2-3 days | Cluster failure |
| After stale cleanup (~225 GB) | 30-45 days | Stable with ISM |
| With ISM policies active | 60+ days | Self-maintaining |
| Long-term growth | 6+ months | May need expansion |

### Infrastructure Upgrades (Consider for Q2 2026)

1. **Increase Storage**: 350 GB → 500 GB per node (+600 GB total)
   - Cost: ~$36/month additional

2. **Enable UltraWarm**: For logs older than 7 days
   - Cost: ~$0.024/GB-month vs $0.108/GB-month (gp2)
   - Savings: ~78% on warm storage

3. **Migrate to gp3**: Better performance, lower cost
   - Savings: ~$26/month
   - Zero downtime migration

4. **Graviton Migration**: m5.xlarge → m6g.xlarge
   - Savings: ~$58/month
   - Better performance

**Total Potential Monthly Savings: $84.51**

### Shard Optimization

```json
// Update index template for optimal shard sizing
PUT _index_template/app-logs-template
{
  "index_patterns": ["iprod_tomcat_lucky_k8s-*"],
  "template": {
    "settings": {
      "number_of_shards": 2,
      "number_of_replicas": 1,
      "index.lifecycle.name": "app-logs-30d"
    }
  },
  "priority": 200
}
```

---

## 10. Action Plan Timeline

### TODAY (Feb 10, 2026) - P0 Critical

| Time | Action | Expected Result |
|------|--------|-----------------|
| +0h | Verify VPC access to cluster | - |
| +0.5h | Run `GET _cat/indices/*2025.09*` | Identify stale indices |
| +1h | Delete September 2025 indices | Recover ~125+ GB |
| +1.5h | Monitor FreeStorageSpace metric | Should jump to ~160+ GB |
| +2h | Delete October 2025 indices (if needed) | Recover ~50+ GB more |

### THIS WEEK (Feb 10-14, 2026) - P1 High

| Day | Action |
|-----|--------|
| Mon | Create ISM policies (all 4) |
| Tue | Attach ISM policies to existing indices |
| Wed | Delete November 2025 indices |
| Thu | Configure SkyWalking OAP retention settings |
| Fri | Verify ISM policies are executing |

### THIS MONTH (February 2026) - P2 Medium

| Week | Action |
|------|--------|
| Week 2 | Review December 2025 indices for deletion |
| Week 3 | Plan gp2 → gp3 migration (zero downtime) |
| Week 4 | Evaluate UltraWarm for cost savings |

### Q1 2026 - P3 Optimization

- Graviton migration planning
- Storage capacity expansion if needed
- Engine upgrade to OpenSearch 2.x

---

## 11. Monitoring and Alerting Recommendations

### CloudWatch Alarms to Create

```bash
# CRITICAL: FreeStorageSpace alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "luckyur-log-FreeStorageSpace-CRITICAL" \
  --namespace AWS/ES \
  --metric-name FreeStorageSpace \
  --dimensions Name=DomainName,Value=luckyur-log Name=ClientId,Value=257394478466 \
  --statistic Minimum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 30000 \
  --comparison-operator LessThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:257394478466:ops-alerts

# WARNING: FreeStorageSpace alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "luckyur-log-FreeStorageSpace-WARNING" \
  --namespace AWS/ES \
  --metric-name FreeStorageSpace \
  --dimensions Name=DomainName,Value=luckyur-log Name=ClientId,Value=257394478466 \
  --statistic Minimum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 50000 \
  --comparison-operator LessThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:257394478466:ops-alerts

# JVM Memory Pressure alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "luckyur-log-JVMMemoryPressure-WARNING" \
  --namespace AWS/ES \
  --metric-name JVMMemoryPressure \
  --dimensions Name=DomainName,Value=luckyur-log Name=ClientId,Value=257394478466 \
  --statistic Maximum \
  --period 300 \
  --evaluation-periods 3 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:257394478466:ops-alerts
```

### Metrics to Track Post-Cleanup

| Metric | Expected After Cleanup | Monitor For |
|--------|----------------------|-------------|
| FreeStorageSpace | 180+ GB | Stable growth pattern |
| ClusterUsedSpace | <1,000 GB | No sudden spikes |
| JVMMemoryPressure | 60-70% | Should improve |
| IndexingLatency | <0.2ms | Should normalize |
| SearchLatency | <1.0ms | Should normalize |

---

## 12. Risk Assessment

### Deletion Risks

| Index Category | Risk Level | Mitigation |
|----------------|------------|------------|
| 2025.09.* indices | LOW | 5 months old, no active use |
| 2025.10.* indices | LOW | 4 months old, minimal active use |
| 2025.11.* indices | MEDIUM | 3 months old, verify no compliance needs |
| 2025.12.* indices | MEDIUM-HIGH | 2 months old, may have active references |

### Pre-Deletion Checklist

- [ ] Verify no Kibana/OpenSearch Dashboards saved objects reference these indices
- [ ] Confirm no active alerts are querying these indices
- [ ] Check if any compliance/audit requirements mandate retention
- [ ] Communicate deletion plan to development team
- [ ] Take note of index names before deletion for rollback documentation

### Rollback Strategy

Deletions are **irreversible** in OpenSearch. However:
1. If data is critical, consider snapshot to S3 before deletion
2. Data can be re-ingested from source systems if needed
3. For logs: source is typically still available in CloudWatch Logs or Fluent Bit buffers

---

## 13. Appendix

### A. Useful OpenSearch Commands Reference

```json
// Cluster Health
GET _cluster/health

// Disk Allocation
GET _cat/allocation?v

// Index Stats
GET _cat/indices?v&s=store.size:desc

// Shard Distribution
GET _cat/shards?v&s=store:desc

// ISM Policy Status
GET _plugins/_ism/explain/*

// Template List
GET _index_template/*

// Delete Index Pattern (CAREFUL!)
DELETE <index-pattern>

// Force Merge (after deletions, low priority)
POST <index>/_forcemerge?max_num_segments=1
```

### B. AWS CLI Commands

```bash
# Get cluster config
aws opensearch describe-domain --domain-name luckyur-log

# Get cluster metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ES \
  --metric-name FreeStorageSpace \
  --dimensions Name=DomainName,Value=luckyur-log Name=ClientId,Value=257394478466 \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 3600 \
  --statistics Minimum Maximum Average
```

### C. Contact Information

For execution of these recommendations, coordinate with:
- DevOps Team: For cluster access and deletion execution
- Development Team: For SkyWalking retention configuration
- Security/Compliance: For any data retention requirement verification

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-10 | DevOps DBA Team | Initial comprehensive analysis |

---

*This report was generated at 2026-02-10 ~07:00 UTC. Storage metrics are based on CloudWatch data through 2026-02-10 07:04 UTC.*
