# Root Cause Analysis: RDS MySQL Restart - aws-luckyus-isalescdp-rw

**Incident ID:** INC-2026-0211-MYSQL-EXPORTER
**Analysis Date:** 2026-02-11
**RDS Instance:** aws-luckyus-isalescdp-rw
**Instance Type:** db.t4g.micro
**Region:** us-east-1

---

## Executive Summary

**ROOT CAUSE: AUTOMATED MULTI-AZ FAILOVER DUE TO MEMORY EXHAUSTION**

The RDS MySQL instance `aws-luckyus-isalescdp-rw` experienced an **automated Multi-AZ failover** at 15:14:38 UTC on 2026-02-11. The failover was triggered because the **primary instance became unresponsive due to memory pressure**. This was NOT a planned maintenance, manual action, or AWS infrastructure event.

---

## Incident Classification

| Question | Answer |
|----------|--------|
| **Was this planned AWS maintenance?** | **NO** - Maintenance window is Saturday 04:52-05:22 UTC; incident occurred Tuesday 15:14 UTC |
| **Was this a manual reboot?** | **NO** - CloudTrail shows no RebootDBInstance events |
| **Was this a manual failover?** | **NO** - CloudTrail shows no FailoverDBCluster events |
| **Was this an AWS infrastructure event?** | **NO** - This was instance-specific resource exhaustion |
| **Was this an automated failover?** | **YES** - RDS automated Multi-AZ failover due to unresponsive primary |
| **What triggered the failover?** | **MEMORY EXHAUSTION** - Primary instance became "busy and unresponsive" |

---

## Evidence from AWS RDS Events

| Timestamp (UTC) | Event | Category |
|-----------------|-------|----------|
| 15:14:38.411 | Multi-AZ instance failover started | failover |
| 15:15:08.090 | DB instance restarted | availability |
| 15:15:12.406 | **The RDS Multi-AZ primary instance is busy and unresponsive** | - |
| 15:15:12.406 | Multi-AZ instance failover completed | failover |
| 15:19:46.086 | **A database workload is causing the system to run critically low on memory. RDS automatically set innodb_buffer_pool_size to 134217728 (128MB)** | notification |

---

## CloudTrail Analysis

**Query:** RebootDBInstance events from 14:00-16:00 UTC
```json
{
    "Events": []
}
```

**Query:** FailoverDBCluster events from 14:00-16:00 UTC
```json
{
    "Events": []
}
```

**Conclusion:** No manual actions were taken. This was an automated AWS response to an unhealthy primary instance.

---

## CloudWatch Metrics Analysis

### CPU Utilization
| Time (UTC) | CPU % | Notes |
|------------|-------|-------|
| 14:30-14:55 | 10-14% | Normal operation |
| 15:13 | 2.9% | Dropping - instance becoming unresponsive |
| 15:14 | 2.9% | Failover initiated |
| 15:15 | 24.6% | Recovery starting |
| 15:16 | 33.5% | Post-failover spike |
| 15:17-18 | 38-39% | Peak recovery load |
| 15:20+ | 14-24% | Stabilizing |

### Database Connections
| Time (UTC) | Connections | Notes |
|------------|-------------|-------|
| 14:30-14:44 | 60-104 | Normal load, peak at 104 |
| 15:14 | **0** | All connections dropped during failover |
| 15:15 | 44 | Connections re-establishing |
| 15:16-15:29 | 44-63 | Recovered, slightly lower than pre-incident |

### Freeable Memory
| Time (UTC) | Memory (MB) | Notes |
|------------|-------------|-------|
| 14:00-15:13 | 87-104 MB | Low but stable |
| 15:14 | 247 MB | Spike after failover to standby |
| 15:15+ | 87-106 MB | Returned to previous levels |

---

## Root Cause: Memory Exhaustion on Undersized Instance

### Instance Specifications
```
Instance Type:    db.t4g.micro
vCPUs:            2
Memory:           ~1 GB
Multi-AZ:         Yes
Engine:           MySQL 8.0.40
```

### Problem Analysis

1. **Undersized Instance:** db.t4g.micro has only ~1GB RAM, severely limited for production workloads
2. **High Connection Load:** 60-104 concurrent connections consuming memory
3. **Low Free Memory:** Only 87-104 MB free (less than 10% of total)
4. **Memory Pressure Event:** Workload spike caused memory exhaustion
5. **Primary Unresponsive:** MySQL became "busy and unresponsive"
6. **Automated Failover:** AWS Multi-AZ failover triggered to standby
7. **Buffer Pool Reduction:** RDS automatically reduced `innodb_buffer_pool_size` from default to 128MB to prevent recurrence

### Memory Configuration Change by AWS
```
Parameter:        innodb_buffer_pool_size
New Value:        134217728 (128 MB)
Reason:           "database workload is causing the system to run critically low on memory"
Applied:          Automatically by RDS
```

---

## Timeline Summary

```
14:30:00 UTC  Normal operation, 84 connections, 13.6% CPU, ~100MB free memory
14:42:00 UTC  Connections peak at 104
14:44:00 UTC  Connections at 102, memory pressure building
15:13:00 UTC  CPU drops to 2.9%, primary becoming unresponsive
15:14:00 UTC  Connections drop to 0
15:14:38 UTC  Multi-AZ failover STARTED
15:15:08 UTC  DB instance restarted (on standby)
15:15:12 UTC  Primary confirmed "busy and unresponsive"
15:15:12 UTC  Multi-AZ failover COMPLETED
15:15:00 UTC  mysqld_exporter reconnects, monitoring resumes
15:16:00 UTC  CPU spike to 33.5% during recovery
15:19:46 UTC  RDS auto-reduces buffer pool to 128MB
15:20:00+    System stabilized
```

**Total Downtime:** ~1 minute (15:14:38 to 15:15:12)
**Monitoring Gap:** ~16 minutes (14:59 to 15:15) - exporter timeouts before and during failover

---

## Instance Comparison: Is This Undersized?

| Instance Type | Memory | Current | Recommended |
|---------------|--------|---------|-------------|
| db.t4g.micro | 1 GB | **Current** | Too small for 100+ connections |
| db.t4g.small | 2 GB | - | Minimum for this workload |
| db.t4g.medium | 4 GB | - | Recommended for headroom |

### Memory Calculation
```
MySQL base memory:                     ~200 MB
innodb_buffer_pool_size (reduced):      128 MB
Per-connection overhead (~100 conn):   ~200 MB (2MB each estimate)
Other MySQL processes:                 ~100 MB
OS and system:                         ~200 MB
-------------------------------------------
Estimated Total Usage:                 ~828 MB
Instance Total Memory:                ~1024 MB
Available Free:                        ~196 MB theoretical
Observed Free:                         ~100 MB actual
```

The instance is **operating at capacity** with minimal safety margin.

---

## Recommendations

### Immediate Actions (P1)

1. **Upgrade Instance Size**
   ```bash
   aws rds modify-db-instance \
     --db-instance-identifier aws-luckyus-isalescdp-rw \
     --db-instance-class db.t4g.small \
     --apply-immediately
   ```
   - Upgrade from db.t4g.micro (1GB) to db.t4g.small (2GB) minimum
   - Recommended: db.t4g.medium (4GB) for production workload

2. **Set Up Memory Alarms**
   ```bash
   aws cloudwatch put-metric-alarm \
     --alarm-name "RDS-isalescdp-LowMemory" \
     --metric-name FreeableMemory \
     --namespace AWS/RDS \
     --dimensions Name=DBInstanceIdentifier,Value=aws-luckyus-isalescdp-rw \
     --threshold 150000000 \
     --comparison-operator LessThanThreshold \
     --evaluation-periods 3 \
     --period 300 \
     --statistic Average \
     --alarm-actions <sns-topic-arn>
   ```

3. **Review Connection Pooling**
   - Current: 60-104 connections observed
   - Optimize application connection pools to reduce idle connections
   - Consider connection limits at application level

### Short-Term Actions (P2)

4. **Apply Pending OS Update**
   ```json
   {
     "Action": "system-update",
     "Description": "New Operating System update is available"
   }
   ```
   - Schedule during maintenance window (Saturday 04:52-05:22 UTC)

5. **Tune InnoDB Buffer Pool**
   - After upgrade, increase `innodb_buffer_pool_size` appropriately
   - Current auto-set: 128MB (too small for performance)
   - Target: 50-70% of available memory on larger instance

6. **Implement Query Optimization**
   - Review slow query logs for memory-intensive queries
   - Add appropriate indexes
   - Optimize high-connection workloads

### Long-Term Actions (P3)

7. **Right-Size All Production Databases**
   - Audit all db.t4g.micro instances in production
   - Evaluate memory headroom across fleet
   - Create sizing guidelines

8. **Implement Predictive Alerting**
   - Alert on memory trending downward before exhaustion
   - Monitor connection count growth patterns

---

## Fleet Impact Assessment

This was a **single-instance failure** due to resource constraints on `aws-luckyus-isalescdp-rw`. The earlier investigation showed uptime changes across multiple instances, but the RDS Events confirm this specific instance had a unique memory exhaustion event.

**Other isales RDS instances for reference:**
| Instance | Type | Multi-AZ | Risk |
|----------|------|----------|------|
| aws-luckyus-isalescdp-rw | db.t4g.micro | Yes | **HIGH** - Caused this incident |
| aws-luckyus-isalesdatamarketing-rw | db.t4g.medium | Yes | Low |
| aws-luckyus-isalesmembermarketing-rw | db.t4g.micro | Yes | **HIGH** - Same risk profile |
| aws-luckyus-isalesprivatedomain-rw | db.t4g.medium | Yes | Low |

**Recommendation:** Also upgrade `aws-luckyus-isalesmembermarketing-rw` from db.t4g.micro to prevent similar incidents.

---

## Conclusion

The MySQL exporter alert was caused by an **automated Multi-AZ failover** triggered by **memory exhaustion** on an **undersized db.t4g.micro instance**.

- **Who initiated it?** AWS RDS automated failover system (not human)
- **Why?** Primary instance became unresponsive due to memory pressure
- **What AWS did?** Automatically failed over to standby and reduced buffer pool size
- **Duration?** ~1 minute failover, ~16 minutes monitoring gap
- **Prevention?** Upgrade to db.t4g.small or db.t4g.medium

---

## Appendix: AWS CLI Commands Used

```bash
# Check RDS events
aws rds describe-events --source-identifier aws-luckyus-isalescdp-rw --source-type db-instance --duration 1440

# Check failover events
aws rds describe-events --source-type db-instance --event-categories failover --duration 1440

# Check for manual reboot in CloudTrail
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=RebootDBInstance --start-time 2026-02-11T14:00:00Z --end-time 2026-02-11T16:00:00Z

# Check for manual failover in CloudTrail
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=FailoverDBCluster --start-time 2026-02-11T14:00:00Z --end-time 2026-02-11T16:00:00Z

# Check instance details
aws rds describe-db-instances --db-instance-identifier aws-luckyus-isalescdp-rw

# Check pending maintenance
aws rds describe-pending-maintenance-actions --resource-identifier arn:aws:rds:us-east-1:257394478466:db:aws-luckyus-isalescdp-rw

# Check memory metrics
aws cloudwatch get-metric-statistics --namespace AWS/RDS --metric-name FreeableMemory --dimensions Name=DBInstanceIdentifier,Value=aws-luckyus-isalescdp-rw --start-time 2026-02-11T14:00:00Z --end-time 2026-02-11T16:00:00Z --period 60 --statistics Average

# Check CPU metrics
aws cloudwatch get-metric-statistics --namespace AWS/RDS --metric-name CPUUtilization --dimensions Name=DBInstanceIdentifier,Value=aws-luckyus-isalescdp-rw --start-time 2026-02-11T14:30:00Z --end-time 2026-02-11T15:30:00Z --period 60 --statistics Maximum

# Check connection metrics
aws cloudwatch get-metric-statistics --namespace AWS/RDS --metric-name DatabaseConnections --dimensions Name=DBInstanceIdentifier,Value=aws-luckyus-isalescdp-rw --start-time 2026-02-11T14:30:00Z --end-time 2026-02-11T15:30:00Z --period 60 --statistics Maximum
```

---

**Report Generated:** 2026-02-11
**Analyst:** Claude Code DBA Assistant
**Classification:** Internal - Operations
