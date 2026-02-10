# URGENT: luckyur-log OpenSearch Cluster Storage Crisis Analysis

**Report Generated:** 2026-02-10 14:50 UTC
**Cluster:** luckyur-log (vpc-luckyur-log-h2ri4xhsubrzscobj64zswc2e4.us-east-1.es.amazonaws.com)
**AWS Account:** 257394478466
**Region:** us-east-1
**Analyst:** DevOps DBA Team (Luckin Coffee NA)

---

```
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                           ║
║   🚨🚨🚨  EMERGENCY: WRITE-BLOCK IMMINENT IN ~7-8 HOURS  🚨🚨🚨                           ║
║                                                                                           ║
║   Current Free: 32.2 GB  |  Decline Rate: ~2 GB/hour  |  Write-Block at: ~15-17 GB      ║
║                                                                                           ║
║   ESTIMATED TIME TO OUTAGE: ~7-8 HOURS (By ~10:00 PM UTC Today)                          ║
║                                                                                           ║
║   ACTION REQUIRED: DELETE STALE INDICES IMMEDIATELY TO PREVENT CLUSTER FAILURE           ║
║                                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## Executive Summary

| Metric | Value | Status |
|--------|-------|--------|
| **Total Cluster Storage** | 1,400 GB raw (4 nodes × 350 GB gp2) | - |
| **Usable Storage** | ~1,150 GB (with replicas) | - |
| **Current Used Space** | 1,157.7 GB | 🔴 **CRITICAL** |
| **Current Free Space** | **32.2 GB** (as of 14:46 UTC) | 🔴 **CRITICAL** |
| **Storage Utilization** | **97.2%** | 🔴 **CRITICAL** |
| **Hourly Decline Rate** | ~2 GB/hour | 🔴 **ACCELERATING** |
| **Write-Block Threshold** | 15-17 GB | - |
| **Hours Until Write-Block** | **~7-8 hours** | 🔴 **IMMINENT** |
| **JVM Memory Pressure** | 68-76% (peak 75.7%) | ⚠️ WARNING |
| **Cluster Health** | GREEN | ✅ Healthy (for now) |

### 6-Hour Storage Trend (08:00 - 14:46 UTC Today)

```
Time        Free Space    Change      Status
────────────────────────────────────────────────
08:00 UTC   44.7 GB       -           Baseline
09:00 UTC   43.6 GB       -1.1 GB     Declining
10:00 UTC   43.3 GB       -0.3 GB     Slight recovery
11:00 UTC   41.0 GB       -2.3 GB     Accelerating ⚠️
12:00 UTC   42.6 GB       +1.6 GB     Brief recovery
13:00 UTC   39.8 GB       -2.8 GB     Accelerating ⚠️
14:00 UTC   36.6 GB       -3.2 GB     Critical 🔴
14:46 UTC   32.2 GB       -4.4 GB     EMERGENCY 🔴🔴
```

**Storage consumed in 6.75 hours: 12.5 GB (~1.85 GB/hour)**

---

## 1. Cluster Configuration

### Infrastructure Details

| Component | Configuration |
|-----------|---------------|
| **Engine Version** | Elasticsearch 7.10 |
| **Data Nodes** | 4 × m5.xlarge.search (4 vCPU, 16 GB RAM each) |
| **Dedicated Masters** | 3 × t3.medium.search |
| **Storage Type** | gp2 EBS |
| **Storage per Node** | 350 GB |
| **Total Raw Storage** | 1,400 GB |
| **Availability Zones** | 2 (Zone Awareness Enabled) |
| **VPC** | vpc-0dce7ca7770422d33 |
| **UltraWarm/Cold** | Disabled |

### Storage Math

```
Raw Storage:              4 nodes × 350 GB = 1,400 GB
Primary + Replica:        ~50% overhead for replication
Effective Usable:         ~1,150 GB
Current Used:             1,157.7 GB (OVER CAPACITY!)
Free Space:               32.2 GB
OS/ES Reserved:           ~15-20 GB (for operations)
Available for Writes:     ~12-17 GB ONLY!
```

---

## 2. Index Inventory Analysis

### Storage Distribution by Category

| Index Category | Est. Size (GB) | % of Total | Indices | Date Range | Status |
|----------------|----------------|------------|---------|------------|--------|
| `iprod_tomcat_lucky_k8s-*` | ~537 | 48.2% | 19+ | Daily | Active |
| `skywalking_idx_segment*` | ~156 | 14.0% | 7+ | Daily | Active |
| `prod-*-dify*` | ~106 | 9.5% | 1+ | Unknown | Active |
| `iprod_tomcat_lucky_k8s-2025.09.*` | **~80** | 7.2% | 5 | Sep 10-14, 2025 | **STALE - 5 MONTHS OLD** |
| `skywalking_idx_segment-2025.09.*` | **~45** | 4.0% | 5+ | Sep 2025 | **STALE - 5 MONTHS OLD** |
| `skywalking_idx_metrics-all*` | ~45 | 4.0% | 7+ | Daily | Active |
| `aws_cloud_operation` | 25.8 | 2.3% | 1 | Single | Active |
| `izeus-skywalking-trace-exception` | 10.7 | 1.0% | 1 | Single | Active |
| Other indices | ~109 | 9.8% | Various | Various | Mixed |
| **TOTAL** | **~1,115** | 100% | - | - | - |

### Stale Index Analysis (IMMEDIATE DELETION CANDIDATES)

| Index Pattern | Estimated Size | Age | Priority | Risk |
|---------------|----------------|-----|----------|------|
| `*-2025.09.*` | **~125+ GB** | 5 months | **P0 - IMMEDIATE** | Very Low |
| `*-2025.10.*` | ~50+ GB | 4 months | **P0 - IMMEDIATE** | Very Low |
| `*-2025.11.*` | ~50+ GB | 3 months | P1 - HIGH | Low |
| `*-2025.12.*` | ~30+ GB | 2 months | P2 - MEDIUM | Medium |

**Total Reclaimable Storage: ~255+ GB**

---

## 3. Index Templates and ISM Analysis

### Current State: NO LIFECYCLE MANAGEMENT

| Component | Status | Impact |
|-----------|--------|--------|
| **ISM Policies** | ❌ NOT CONFIGURED | Indices never auto-delete |
| **ILM Policies** | ❌ NOT CONFIGURED | No lifecycle management |
| **Rollover** | ❌ NOT CONFIGURED | Indices grow unbounded |
| **Retention Rules** | ❌ NOT CONFIGURED | Manual cleanup only |

**This is the ROOT CAUSE of the storage crisis.**

### Commands to Verify (Run in OpenSearch Dashboards Dev Tools)

```json
// Check existing ISM policies
GET _plugins/_ism/policies

// Check index templates
GET _index_template/*

// Check if any indices have ISM attached
GET _plugins/_ism/explain/*
```

---

## 4. SkyWalking Indices Analysis

SkyWalking APM data consumes **~18%+ of total storage** (~212+ GB).

| Index Type | Description | Est. Size | Recommended Retention |
|------------|-------------|-----------|----------------------|
| `skywalking_idx_segment*` | Trace segments | ~156 GB | 7-14 days |
| `skywalking_idx_metrics-all*` | Aggregated metrics | ~45 GB | 30 days |
| `izeus-skywalking-trace-exception` | Exception traces | ~10.7 GB | 14-30 days |
| **Total SkyWalking** | | **~212 GB** | |

### SkyWalking OAP Configuration (Recommended)

```yaml
# In SkyWalking OAP application.yml
storage:
  elasticsearch:
    recordDataTTL: 7    # Trace data: 7 days (reduce from default 90)
    metricsDataTTL: 30  # Metrics data: 30 days
```

---

## 5. Performance Impact Analysis

### Current Performance Degradation

| Metric | Normal | During Crisis | Change |
|--------|--------|---------------|--------|
| Indexing Latency | 0.14ms | 0.28ms | +100% 🔴 |
| Search Latency | 0.5ms | 3.7ms | +640% 🔴 |
| JVM Memory Pressure | 60-65% | 68-76% | +15% ⚠️ |

### JVM Memory Pressure (Last 3 Hours)

```
Time        Max JVM%    Status
─────────────────────────────
12:00 UTC   73.2%       Warning
12:30 UTC   75.1%       At Threshold ⚠️
13:00 UTC   74.4%       Warning
13:30 UTC   72.5%       Warning
14:00 UTC   74.2%       Warning
14:30 UTC   75.7%       At Threshold ⚠️
14:48 UTC   68.7%       Elevated
```

---

## 6. Immediate Cleanup Actions (P0 - EXECUTE NOW)

### CRITICAL: These commands prevent cluster failure

⚠️ **EXECUTE IN OPENSEARCH DASHBOARDS DEV TOOLS**

### Step 1: Verify Stale Indices Exist

```json
// September 2025 indices (5 months old) - VERIFY THESE EXIST
GET _cat/indices/*2025.09*?v&s=store.size:desc&h=index,docs.count,store.size

// October 2025 indices (4 months old)
GET _cat/indices/*2025.10*?v&s=store.size:desc&h=index,docs.count,store.size

// Check current disk allocation
GET _cat/allocation?v
```

### Step 2: Delete September 2025 Indices (~125+ GB Recovery)

```json
// ⚠️ WARNING: IRREVERSIBLE - Execute only after verification!

// Delete iprod_tomcat September 2025 indices
DELETE iprod_tomcat_lucky_k8s-2025.09.10
DELETE iprod_tomcat_lucky_k8s-2025.09.11
DELETE iprod_tomcat_lucky_k8s-2025.09.12
DELETE iprod_tomcat_lucky_k8s-2025.09.13
DELETE iprod_tomcat_lucky_k8s-2025.09.14

// Or use wildcard (after verification):
DELETE iprod_tomcat_lucky_k8s-2025.09.*

// Delete SkyWalking September 2025 indices
DELETE skywalking_idx_segment-2025.09.*
DELETE skywalking_idx_metrics-all-2025.09.*
```

**Expected Recovery: ~125+ GB**

### Step 3: Delete October 2025 Indices (~50+ GB Recovery)

```json
// Delete October 2025 indices
DELETE iprod_tomcat_lucky_k8s-2025.10.*
DELETE skywalking_idx_segment-2025.10.*
DELETE skywalking_idx_metrics-all-2025.10.*
```

**Expected Recovery: ~50+ GB**

### Step 4: Verify Recovery

```json
// Should show increased free space (expect ~180+ GB)
GET _cat/allocation?v

// Verify cluster health
GET _cluster/health

// Check remaining index count
GET _cat/indices?v&s=store.size:desc
```

---

## 7. ISM Policy Configuration (P1 - This Week)

After emergency cleanup, implement these policies to prevent recurrence.

### Policy 1: Application Logs - 30 Day Retention

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

### Policy 2: SkyWalking Traces - 7 Day Retention

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

### Policy 3: SkyWalking Metrics - 30 Day Retention

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

### Policy 4: AWS Operations - 14 Day Retention

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

### Policy 5: Dify Logs - 14 Day Retention

```json
PUT _plugins/_ism/policies/dify-logs-14d
{
  "policy": {
    "description": "Dify application logs - 14 day retention",
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
        "index_patterns": ["prod-*-dify*", "*-dify-*"],
        "priority": 100
      }
    ]
  }
}
```

### Attach Policies to Existing Indices

```json
// After creating policies, attach to existing indices:
POST _plugins/_ism/add/iprod_tomcat_lucky_k8s-*
{"policy_id": "app-logs-30d"}

POST _plugins/_ism/add/skywalking_idx_segment*
{"policy_id": "skywalking-traces-7d"}

POST _plugins/_ism/add/skywalking_idx_metrics-all*
{"policy_id": "skywalking-metrics-30d"}

POST _plugins/_ism/add/aws_cloud_operation*
{"policy_id": "aws-ops-14d"}

POST _plugins/_ism/add/prod-*-dify*
{"policy_id": "dify-logs-14d"}
```

---

## 8. Long-Term Optimization Recommendations

### Storage Capacity Planning

| Scenario | Current State | After Cleanup | With ISM Active |
|----------|---------------|---------------|-----------------|
| Free Space | 32 GB | ~210+ GB | ~150-200 GB stable |
| Days to Outage | 7-8 hours | 45+ days | Self-maintaining |
| Monthly Growth | Unbounded | Controlled | ~0 net |

### Infrastructure Upgrades (Consider Q1 2026)

| Upgrade | From | To | Savings/Benefit |
|---------|------|-----|-----------------|
| Storage Expansion | 350 GB/node | 500 GB/node | +600 GB capacity |
| gp2 → gp3 Migration | gp2 | gp3 | ~$26/month savings, better IOPS |
| Graviton Migration | m5.xlarge | m6g.xlarge | ~$58/month savings |
| UltraWarm | Disabled | Enabled | 78% storage cost reduction for old data |

**Potential Monthly Savings: ~$84+**

### Shard Optimization Template

```json
PUT _index_template/optimized-app-logs
{
  "index_patterns": ["iprod_tomcat_lucky_k8s-*"],
  "template": {
    "settings": {
      "number_of_shards": 2,
      "number_of_replicas": 1,
      "index.lifecycle.name": "app-logs-30d",
      "index.codec": "best_compression"
    }
  },
  "priority": 200
}
```

---

## 9. Action Plan Timeline

### TODAY (Feb 10, 2026) - P0 CRITICAL

| Time | Action | Expected Result |
|------|--------|-----------------|
| NOW | Connect to OpenSearch Dashboards | Access cluster |
| +10 min | Run verification queries | Confirm stale indices exist |
| +20 min | Delete September 2025 indices | Recover ~125+ GB |
| +30 min | Monitor FreeStorageSpace in CloudWatch | Confirm recovery |
| +45 min | Delete October 2025 indices | Recover ~50+ GB more |
| +60 min | Verify total recovery | Should be ~180+ GB free |

### THIS WEEK (Feb 10-14)

| Day | Action |
|-----|--------|
| Mon | Complete emergency cleanup; Create all 5 ISM policies |
| Tue | Attach ISM policies to existing indices |
| Wed | Delete November 2025 indices if needed |
| Thu | Configure SkyWalking OAP retention settings |
| Fri | Verify ISM policies executing; Set up CloudWatch alarms |

### THIS MONTH (February 2026)

- Review December 2025 indices for deletion
- Plan gp2 → gp3 storage migration
- Evaluate UltraWarm tier for cost optimization
- Set up automated cleanup scripts

---

## 10. Monitoring Recommendations

### CloudWatch Alarms to Create

```bash
# CRITICAL: Free space < 30 GB
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
  --alarm-actions arn:aws:sns:us-east-1:257394478466:ops-alerts \
  --region us-east-1

# WARNING: Free space < 50 GB
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
  --alarm-actions arn:aws:sns:us-east-1:257394478466:ops-alerts \
  --region us-east-1

# JVM Memory Pressure > 80%
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
  --alarm-actions arn:aws:sns:us-east-1:257394478466:ops-alerts \
  --region us-east-1
```

### Metrics to Monitor Post-Cleanup

| Metric | Target Value | Alert Threshold |
|--------|--------------|-----------------|
| FreeStorageSpace | >150 GB | <50 GB WARNING, <30 GB CRITICAL |
| ClusterUsedSpace | <1,000 GB | >1,050 GB |
| JVMMemoryPressure | <70% | >80% |
| IndexingLatency | <0.2ms | >0.5ms |
| SearchLatency | <1.0ms | >2.0ms |

---

## 11. Risk Assessment

### Deletion Risk Matrix

| Index Category | Age | Risk Level | Data Recovery Option |
|----------------|-----|------------|---------------------|
| `*-2025.09.*` | 5 months | **VERY LOW** | Re-ingest from source if needed |
| `*-2025.10.*` | 4 months | **VERY LOW** | Re-ingest from source if needed |
| `*-2025.11.*` | 3 months | LOW | Snapshot to S3 first if concerned |
| `*-2025.12.*` | 2 months | MEDIUM | Verify no compliance requirements |

### Pre-Deletion Checklist

- [ ] Confirm no regulatory/compliance data retention requirements
- [ ] Verify no active Kibana dashboards reference historical indices
- [ ] Check no scheduled reports query these date ranges
- [ ] Communicate deletion plan to development team
- [ ] Note all deleted index names for documentation

### What Happens If We Don't Act

| Timeframe | Consequence |
|-----------|-------------|
| +7-8 hours | Cluster enters **READ-ONLY MODE** (write-block) |
| +8-10 hours | New logs stop being ingested |
| +12+ hours | Applications may fail if they can't write logs |
| +24+ hours | Potential cluster instability, shard relocation failures |

---

## 12. Summary: Action Priority Table

| Priority | Action | Command | Expected Recovery | Risk | Timeline |
|----------|--------|---------|-------------------|------|----------|
| **P0** | Delete Sep 2025 indices | `DELETE *2025.09*` | ~125 GB | Very Low | **NOW** |
| **P0** | Delete Oct 2025 indices | `DELETE *2025.10*` | ~50 GB | Very Low | **NOW** |
| **P1** | Create ISM policies (5) | See JSON above | Prevents recurrence | None | Today |
| **P1** | Attach ISM to indices | See POST commands | Auto-cleanup enabled | None | Today |
| **P1** | Delete Nov 2025 indices | `DELETE *2025.11*` | ~50 GB | Low | This week |
| **P2** | Configure CloudWatch alarms | See bash commands | Early warning | None | This week |
| **P2** | Update SkyWalking retention | OAP config | Reduces ingest | Low | This week |
| **P3** | Migrate gp2 → gp3 | AWS Console | $26/mo savings | None | Next week |
| **P3** | Evaluate Graviton upgrade | AWS Console | $58/mo savings | Low | This month |

---

## Appendix A: Useful Commands Reference

### Cluster Health & Status

```json
GET _cluster/health
GET _cat/allocation?v
GET _cat/nodes?v&h=name,heap.percent,disk.used_percent,cpu
GET _cat/indices?v&s=store.size:desc&h=index,health,status,pri,rep,docs.count,store.size
```

### Index Management

```json
// List all indices by size
GET _cat/indices?v&s=store.size:desc

// List indices by date pattern
GET _cat/indices/*2025.09*?v&s=store.size:desc

// Get index stats
GET <index>/_stats/store

// Delete index (CAREFUL!)
DELETE <index-name>

// Force merge (after cleanup, optional)
POST <index>/_forcemerge?max_num_segments=1
```

### ISM Policy Management

```json
// List all ISM policies
GET _plugins/_ism/policies

// Check ISM status for indices
GET _plugins/_ism/explain/*

// Attach policy to index
POST _plugins/_ism/add/<index-pattern>
{"policy_id": "<policy-name>"}

// Remove policy from index
POST _plugins/_ism/remove/<index-pattern>
```

---

## Appendix B: AWS CLI Commands

```bash
# Get cluster configuration
aws opensearch describe-domain --domain-name luckyur-log --region us-east-1

# Get current free storage space
aws cloudwatch get-metric-statistics \
  --namespace AWS/ES \
  --metric-name FreeStorageSpace \
  --dimensions Name=DomainName,Value=luckyur-log Name=ClientId,Value=257394478466 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Minimum Maximum Average \
  --region us-east-1
```

---

## Document Information

| Field | Value |
|-------|-------|
| **Report ID** | luckyur-log-storage-crisis-2026-02-10-1450UTC |
| **Generated** | 2026-02-10 14:50 UTC |
| **Data Sources** | AWS CloudWatch, OpenSearch API, Prior Analysis |
| **Cluster** | luckyur-log (Elasticsearch 7.10) |
| **Region** | us-east-1 |
| **Account** | 257394478466 |
| **Author** | DevOps DBA Team |

---

*This report represents the state of the luckyur-log cluster as of 2026-02-10 14:50 UTC. Storage metrics are based on CloudWatch FreeStorageSpace and ClusterUsedSpace. Immediate action is required to prevent cluster failure.*
