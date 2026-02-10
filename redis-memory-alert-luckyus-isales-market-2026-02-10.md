# Redis Memory Alert Investigation Report

**Alert:** Redis 内存使用率持续3分钟超过70%
**Instance:** luckyus-isales-market
**Date:** February 10, 2026
**Time of Alert:** ~09:00 UTC
**Region:** us-east-1

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Affected Instance** | `rediss://master.luckyus-isales-market.vyllrs.use1.cache.amazonaws.com:6379` |
| **Current Memory Usage** | 74.4% (1.72 GB / 2.49 GB) |
| **Peak Memory Usage** | 75.8% (1.76 GB) |
| **Pre-Incident Memory** | 57.2% (1.33 GB) |
| **Memory Increase** | +430 MB (+18.6 percentage points) |
| **Root Cause** | **Burst Write Operation - 340K+ keys written in ~10 minutes** |
| **Severity** | **Medium** - Alert triggered but not at critical levels |

---

## Root Cause Analysis

### Primary Finding: Application Burst Write Event

The memory spike was caused by a **massive burst of write operations** from an application. This is NOT a Redis issue - it's application-driven behavior.

### Evidence Timeline (Last 1 Hour)

#### 1. Connected Clients Spike
```
Time (relative)    Clients    Change
─────────────────────────────────────
-60 min            51         Baseline
-40 min            52-55      Normal
-30 min            58         Slight increase
-25 min            92         +34 clients (+59%)
-23 min            122        +64 clients (+111%)
-22 min            134        +76 clients (+133%) ← PEAK
-15 min            118        Stabilizing
Now                103        Still elevated
```

#### 2. Key Count Explosion (db0)
```
Time (relative)    Keys         Delta
─────────────────────────────────────────
-60 min            6,022,668    Baseline
-40 min            6,024,447    Normal growth
-30 min            5,988,144    Gradual expiration (normal)
-25 min            6,016,181    +28,037 keys
-23 min            6,087,321    +99,177 keys
-20 min            6,161,394    +173,250 keys
-17 min            6,262,569    +274,425 keys
-15 min            6,331,293    +343,149 keys ← PEAK
Now                6,296,289    Starting to expire
```

**Total Keys Added: ~343,000 keys in approximately 10 minutes**

#### 3. Commands Per Second (40x Spike!)
```
Time (relative)    Cmd/sec      Status
─────────────────────────────────────────
-60 min            170-280      Normal baseline
-40 min            230-260      Normal
-25 min            2,034        10x increase
-23 min            4,614        20x increase
-20 min            7,597        30x increase
-17 min            10,379       40x increase
-15 min            11,091       PEAK (48x normal)
-10 min            1,712        Declining
Now                709          Still elevated
```

#### 4. Memory Usage Pattern
```
Time (relative)    Memory %     Memory (GB)
─────────────────────────────────────────────
-60 min            57.5%        1.33 GB
-40 min            57.5%        1.33 GB
-30 min            57.2%        1.33 GB
-25 min            59.5%        1.38 GB
-20 min            67.1%        1.56 GB
-17 min            72.7%        1.69 GB
-15 min            75.8%        1.76 GB ← PEAK (Alert Triggered)
-10 min            74.9%        1.74 GB
Now                74.4%        1.72 GB
```

---

## Key Metrics Analysis

### Keys with TTL vs Without TTL

| Metric | Before Spike | At Peak | Current |
|--------|--------------|---------|---------|
| Total Keys (db0) | 5,988,144 | 6,331,293 | 6,296,289 |
| Keys with TTL | 3,479,990 | 3,799,155 | 3,761,445 |
| Keys without TTL | 2,508,154 | 2,532,138 | 2,534,844 |
| % with TTL | 58.1% | 60.0% | 59.7% |

**Finding:** The newly added keys HAVE TTL set (good practice). The keys are already starting to expire naturally.

### Current Status

| Component | Status |
|-----------|--------|
| Memory Usage | **WARNING** - 74.4% (above 70% threshold) |
| Memory Trend | **IMPROVING** - Declining from peak of 75.8% |
| Key Count | **STABILIZING** - Keys expiring naturally |
| Connected Clients | **ELEVATED** - 103 (vs baseline 51) |
| Commands/sec | **RECOVERING** - 709 (down from peak 11,091) |

---

## Diagnosis

### What Happened

1. **Application Event:** Around 25 minutes ago, an application (or batch job) connected to Redis and began a massive write operation
2. **Connection Surge:** Connected clients doubled from 51 to 134
3. **Key Insertion:** ~343,000 new keys were written in approximately 10 minutes
4. **Memory Impact:** Memory usage jumped from 57% to 76%
5. **Alert Triggered:** The 70% threshold was breached for >3 minutes, triggering the alert
6. **Natural Recovery:** Keys have TTLs and are now expiring; memory is slowly decreasing

### Likely Causes

Based on the pattern (burst write, many connections, high command rate), this is likely caused by:

1. **Scheduled Batch Job** - A marketing campaign data load, product catalog sync, or similar batch operation
2. **Cache Warming** - Application restart/deployment triggering cache population
3. **Data Sync Operation** - Synchronization from another data source
4. **Traffic Spike** - High user activity causing cache population

### NOT the Cause

- Redis configuration issue
- Memory leak
- Missing TTLs (keys DO have TTLs)
- Slow queries blocking Redis

---

## Immediate Actions (No Action Required)

The situation is **self-healing**:

1. Memory is already declining from peak (75.8% → 74.4%)
2. Keys have TTLs and are expiring naturally
3. Command rate has returned to near-normal levels
4. No intervention is needed at this time

**Continue monitoring for the next 30-60 minutes. Memory should return below 70%.**

---

## Recommended Solutions

### Short-Term (Next 24-48 Hours)

#### 1. Identify the Application/Job
```bash
# If you have access to Redis CLI, check client info
redis-cli CLIENT LIST | grep -E "name|cmd|age"

# Check application logs around the spike time (09:00 UTC)
# Look for batch jobs, deployments, or scheduled tasks
```

#### 2. Set Up Better Monitoring
Add alerts for:
- `redis_connected_clients` > 100 (early warning)
- `rate(redis_commands_processed_total[5m])` > 5000 (command rate spike)
- `rate(redis_db_keys[5m])` > 1000 (key insertion rate)

### Medium-Term (Next 1-2 Weeks)

#### 3. Optimize Batch Write Patterns
If this is a scheduled job, implement:

```python
# Example: Rate-limited batch writes
import time

def batch_write_with_throttle(redis_client, keys_data, batch_size=1000, delay=0.1):
    """Write keys in batches with throttling to prevent memory spikes."""
    pipeline = redis_client.pipeline()
    count = 0

    for key, value, ttl in keys_data:
        pipeline.setex(key, ttl, value)
        count += 1

        if count >= batch_size:
            pipeline.execute()
            pipeline = redis_client.pipeline()
            count = 0
            time.sleep(delay)  # Throttle between batches

    if count > 0:
        pipeline.execute()
```

#### 4. Consider Connection Pooling
If applications are creating too many connections:
- Implement connection pooling in application code
- Set `maxclients` appropriately in Redis configuration
- Use a Redis proxy (like Envoy) if needed

### Long-Term Recommendations

#### 5. Increase Memory Capacity
Current capacity (2.49 GB) is close to operational limits. Consider:

| Option | Current | Recommended | Monthly Cost Impact |
|--------|---------|-------------|---------------------|
| Upgrade node type | cache.t3.medium (2.49 GB) | cache.r6g.large (13.07 GB) | +$60-80/month |
| Add read replicas | 1 node | 2 nodes | +$40/month |

#### 6. Implement Memory Management Policies
```redis
# Set maxmemory-policy in Redis config (ElastiCache parameter group)
maxmemory-policy volatile-lru

# This evicts keys with TTL using LRU when memory is full
```

#### 7. Key Expiration Optimization
- Review keys without TTL (currently 2.53M keys or 40%)
- Ensure all cache keys have appropriate TTLs
- Consider shorter TTLs for high-volume data

---

## Monitoring Dashboard Queries

### Memory Usage Ratio (Alert Query)
```promql
100 * redis_memory_used_bytes{instance=~".*luckyus-isales-market.*"}
    / redis_memory_max_bytes{instance=~".*luckyus-isales-market.*"}
```

### Key Growth Rate (Early Warning)
```promql
rate(redis_db_keys{instance=~".*luckyus-isales-market.*", db="db0"}[5m]) * 60
```

### Command Rate Spike Detection
```promql
rate(redis_commands_processed_total{instance=~".*luckyus-isales-market.*"}[5m])
```

### Connected Clients Trend
```promql
redis_connected_clients{instance=~".*luckyus-isales-market.*"}
```

---

## Summary

| Question | Answer |
|----------|--------|
| **Is this an emergency?** | No - Memory is high but stable and declining |
| **Is immediate action needed?** | No - Situation is self-healing |
| **What caused it?** | Application burst write (~343K keys in 10 minutes) |
| **Will it happen again?** | Possibly - Identify and optimize the source job |
| **When will it resolve?** | Within 30-60 minutes as keys expire |

---

## Action Items Checklist

### Immediate (No Action)
- [ ] Monitor memory usage for next 60 minutes
- [ ] Verify memory returns below 70%

### This Week
- [ ] Identify the application/job that caused the spike
- [ ] Review application logs from 09:00 UTC
- [ ] Add command rate and client count alerts

### This Month
- [ ] Implement batch write throttling in applications
- [ ] Review and add TTLs to keys without expiration
- [ ] Consider ElastiCache node upgrade if issues recur

---

*Report generated: February 10, 2026*
*Data source: Prometheus (prometheus_redis datasource)*
*Instance: luckyus-isales-market (AWS ElastiCache)*
