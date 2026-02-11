# ElastiCache Redis Monitoring Analysis

**Date**: 2026-02-11
**Grafana**: https://iumbgrafana.luckincoffee.us
**Target Clusters**: luckyus-iopenlinker, luckyus-iopenlinkeradmin, luckyus-ilopamanager
**Region**: us-east-1

---

## Executive Summary

**CRITICAL MONITORING GAP IDENTIFIED**

| Cluster | Prometheus Metrics | Grafana Dashboard | Grafana Alerts | AWS SNS |
|---------|-------------------|-------------------|----------------|---------|
| luckyus-iopenlinker | ✅ **YES** | ❌ **NO** | ❌ **NO** | ✅ Active |
| luckyus-iopenlinkeradmin | ❌ **NO** | ❌ **NO** | ❌ **NO** | ✅ Active |
| luckyus-ilopamanager | ❌ **NO** | ❌ **NO** | ❌ **NO** | ✅ Active |

**Finding**: 2 of 3 clusters have **NO Prometheus monitoring** at all. All 3 clusters lack Grafana dashboards and alert rules.

---

## 1. Grafana Dashboard Analysis

### Search Results

| Search Query | Results Found |
|--------------|---------------|
| `elasticache` | 0 |
| `redis` | 0 |
| `cache` | 0 |

### All Dashboards in Grafana

| Dashboard | Type | Redis Coverage |
|-----------|------|----------------|
| DBA Infrastructure Monitoring | MySQL/RDS | ❌ No |
| Database Health Monitoring | MySQL | ❌ No |
| MySQL Enterprise Monitoring | MySQL | ❌ No |
| Enterprise RDS Health | MySQL/Postgres | ❌ No |
| NA Weekly Slow SQL Governance | MySQL | ❌ No |
| AWS OpenSearch Storage Monitoring | OpenSearch | ❌ No |
| Node System Overview | Infrastructure | ❌ No |
| InnoDB Deep Monitoring | MySQL | ❌ No |

**Conclusion**: **NO Redis/ElastiCache dashboards exist** in Grafana.

---

## 2. Prometheus Metrics Analysis

### Datasource Configuration

| Datasource | UID | Purpose |
|------------|-----|---------|
| prometheus_redis | ff6p0gjt24phce | Redis metrics (exists!) |
| UMBQuerier-Luckin | df8o21agxtkw0d | MySQL/General |
| prometheus | ff7hkeec6c9a8e | General |

### Target Cluster Metrics Availability

#### luckyus-iopenlinker ✅ MONITORED

```
Instance: rediss://master.luckyus-iopenlinker.vyllrs.use1.cache.amazonaws.com:6379
Job: aws-redis-job
```

| Metric | Current Value | Status |
|--------|---------------|--------|
| Memory Used | 21.4 MB | ✅ Normal |
| Connected Clients | 10 | ✅ Stable |
| Evicted Keys | 0 | ✅ Healthy |
| DB Keys (db0) | 895 | ✅ Active |
| Commands/sec | 0.56 - 0.83 | ✅ Normal |
| Keyspace Hits | 14,117,644 | - |
| Keyspace Misses | 1,057,372 | - |
| **Hit Rate** | **93.0%** | ✅ Excellent |

**24-Hour Memory Trend**:
```
Time (UTC)    Memory (MB)
-----------   -----------
07:30         22.2
11:30         22.2
15:30         21.8
19:30         21.9
23:30         21.8
03:30         21.6
07:30         21.4
```
Memory stable, slight decrease over 24h (normal).

#### luckyus-iopenlinkeradmin ❌ NOT MONITORED

```
Instance: rediss://master.luckyus-iopenlinkeradmin .vyllrs.use1.cache.amazonaws.com:6379
                                                 ^
                                           NOTE: Space in instance name!
```

**Problem**: Instance label contains a **trailing space**, causing metric queries to fail.

| Query | Result |
|-------|--------|
| `redis_memory_used_bytes{instance=~".*iopenlinkeradmin.*"}` | Empty |
| `redis_connected_clients{instance=~".*iopenlinkeradmin.*"}` | Empty |

**Root Cause**: Prometheus scrape configuration has malformed instance label.

#### luckyus-ilopamanager ❌ NOT MONITORED

```
Instance: NOT FOUND in prometheus_redis datasource
```

| Query | Result |
|-------|--------|
| `redis_memory_used_bytes{instance=~".*ilopamanager.*"}` | Empty |

**Root Cause**: Cluster not configured in Prometheus scrape targets.

---

## 3. Alert Rules Analysis

### Current Redis-Related Alerts

| Search | Results |
|--------|---------|
| `elasticache` | 0 alerts |
| `redis` | 0 alerts |
| `iopenlinker` | 0 alerts |
| `ilopamanager` | 0 alerts |

### Existing Alert Rules (All MySQL)

| Alert | Target | Relevance |
|-------|--------|-----------|
| Slow Query Spike - High Rate | MySQL | ❌ Not Redis |
| Slow Query Critical | MySQL | ❌ Not Redis |
| Slow Query Weekly Increase | MySQL | ❌ Not Redis |

**Conclusion**: **NO Redis alert rules exist** in Grafana.

---

## 4. Monitoring Coverage Summary

### Current State

| Monitoring Layer | luckyus-iopenlinker | luckyus-iopenlinkeradmin | luckyus-ilopamanager |
|-----------------|---------------------|--------------------------|----------------------|
| **Prometheus Scraping** | ✅ Working | ⚠️ Misconfigured | ❌ Missing |
| **Grafana Dashboard** | ❌ None | ❌ None | ❌ None |
| **Grafana Alerts** | ❌ None | ❌ None | ❌ None |
| **AWS SNS Notifications** | ✅ Active | ✅ Active | ✅ Active |
| **CloudWatch Metrics** | ✅ (via AWS) | ✅ (via AWS) | ✅ (via AWS) |

### What We're Missing

Without Grafana monitoring, we **cannot** detect:
- Memory pressure before OOM
- Connection spikes
- High eviction rates
- Cache hit rate degradation
- Replication lag
- Command latency increases

We **only** receive:
- Backup completion notifications (daily)
- Failover events (rare)
- Maintenance notifications

---

## 5. Health Status (luckyus-iopenlinker only)

### Current Metrics (as of 2026-02-11 07:50 UTC)

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Memory Used | 21.4 MB | - | ✅ Normal |
| Memory Max | cache.t4g.micro = 512 MB | - | - |
| **Memory Utilization** | **4.2%** | < 80% | ✅ Healthy |
| Connected Clients | 10 | < 65,000 | ✅ Normal |
| Evicted Keys | 0 | 0 | ✅ Perfect |
| Commands/sec | 0.57 | - | ✅ Low load |
| **Hit Rate** | **93.0%** | > 90% | ✅ Excellent |
| DB Keys | 895 | - | ✅ Active |

**Assessment**: Cluster is healthy but underutilized.

---

## 6. Recommendations

### Immediate Actions (Priority 1)

#### 6.1 Fix Prometheus Scrape Configuration

**luckyus-iopenlinkeradmin** - Fix trailing space in instance label:

```yaml
# In prometheus scrape config, change:
- targets:
  - "rediss://master.luckyus-iopenlinkeradmin .vyllrs.use1.cache.amazonaws.com:6379"
# To:
  - "rediss://master.luckyus-iopenlinkeradmin.vyllrs.use1.cache.amazonaws.com:6379"
```

#### 6.2 Add Missing Prometheus Target

**luckyus-ilopamanager** - Add to scrape config:

```yaml
- targets:
  - "rediss://master.luckyus-ilopamanager.vyllrs.use1.cache.amazonaws.com:6379"
```

### Short-term Actions (Priority 2)

#### 6.3 Create Redis Monitoring Dashboard

Create a new dashboard in Grafana with these panels:

```
Dashboard: ElastiCache Redis Monitoring
Datasource: prometheus_redis (ff6p0gjt24phce)

Panels:
1. Memory Usage (%) - redis_memory_used_bytes / redis_memory_max_bytes
2. Connected Clients - redis_connected_clients
3. Commands/sec - rate(redis_commands_processed_total[5m])
4. Hit Rate (%) - redis_keyspace_hits_total / (hits + misses)
5. Evicted Keys - redis_evicted_keys_total
6. Network I/O - redis_net_input_bytes_total, redis_net_output_bytes_total
7. Blocked Clients - redis_blocked_clients
8. Keys by DB - redis_db_keys
```

#### 6.4 Create Redis Alert Rules

```yaml
# High Memory Usage
- alert: RedisHighMemoryUsage
  expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.8
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Redis memory usage > 80%"

# Low Hit Rate
- alert: RedisLowHitRate
  expr: |
    redis_keyspace_hits_total /
    (redis_keyspace_hits_total + redis_keyspace_misses_total) < 0.9
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Redis hit rate below 90%"

# Evictions Occurring
- alert: RedisEvictions
  expr: increase(redis_evicted_keys_total[5m]) > 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Redis evicting keys - memory pressure"

# Too Many Connections
- alert: RedisTooManyConnections
  expr: redis_connected_clients > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Redis connection count high"
```

### Long-term Actions (Priority 3)

#### 6.5 Standardize Redis Monitoring

- Monitor ALL ElastiCache clusters (77 total in account)
- Create unified dashboard with cluster selector variable
- Implement consistent alerting across all Redis instances
- Document monitoring standards

---

## 7. Prometheus Metrics Reference

### Available Redis Metrics

```
redis_memory_used_bytes
redis_connected_clients
redis_evicted_keys_total
redis_keyspace_hits_total
redis_keyspace_misses_total
redis_commands_processed_total
redis_db_keys
redis_blocked_clients
redis_connected_slaves
redis_cpu_sys_seconds_total
redis_cpu_user_seconds_total
redis_net_input_bytes_total
redis_net_output_bytes_total
```

### Sample Queries

```promql
# Memory utilization
redis_memory_used_bytes{instance=~".*luckyus-iopenlinker.*"} / 1024 / 1024

# Hit rate
redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total) * 100

# Commands per second
rate(redis_commands_processed_total[5m])

# Connected clients trend
redis_connected_clients{job="aws-redis-job"}
```

---

## 8. Comparison: AWS SNS vs Grafana Monitoring

| Capability | AWS SNS Only | Grafana + Prometheus |
|------------|--------------|---------------------|
| Backup notifications | ✅ | N/A |
| Failover alerts | ✅ | ✅ (faster) |
| Memory pressure | ❌ | ✅ |
| Connection spikes | ❌ | ✅ |
| Cache hit rate | ❌ | ✅ |
| Eviction alerts | ❌ | ✅ |
| Historical trends | ❌ | ✅ |
| Custom thresholds | ❌ | ✅ |
| Multi-cluster view | ❌ | ✅ |

**Conclusion**: AWS SNS provides operational notifications but NOT performance monitoring. Grafana/Prometheus is essential for proactive alerting.

---

## Appendix: Raw Data

### Monitored Instances in prometheus_redis

Total instances: 76 (from label values query)

Target clusters status:
- `luckyus-iopenlinker` → Found as `rediss://master.luckyus-iopenlinker.vyllrs.use1.cache.amazonaws.com:6379`
- `luckyus-iopenlinkeradmin` → Found but with space: `rediss://master.luckyus-iopenlinkeradmin .vyllrs...` (broken)
- `luckyus-ilopamanager` → NOT FOUND

### luckyus-iopenlinker 24h Memory Data

```json
[
  {"timestamp": "2026-02-10T07:30", "bytes": 22218208},
  {"timestamp": "2026-02-10T11:30", "bytes": 22178688},
  {"timestamp": "2026-02-10T15:30", "bytes": 21794960},
  {"timestamp": "2026-02-10T19:30", "bytes": 21855640},
  {"timestamp": "2026-02-10T23:30", "bytes": 21817432},
  {"timestamp": "2026-02-11T03:30", "bytes": 21562840},
  {"timestamp": "2026-02-11T07:30", "bytes": 21357920}
]
```

### luckyus-iopenlinker Hit Rate Calculation

```
Keyspace Hits:   14,117,644
Keyspace Misses:  1,057,372
Total:           15,175,016
Hit Rate:        14,117,644 / 15,175,016 = 93.03%
```
