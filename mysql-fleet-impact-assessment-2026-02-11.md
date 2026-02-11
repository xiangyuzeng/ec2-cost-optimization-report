# Fleet Impact Assessment: MySQL Restart Incident 2026-02-11

**Assessment Date:** 2026-02-11
**Incident Window:** 14:59 - 15:15 UTC
**Namespace:** custom-scrape-iprod-us
**Region:** us-east-1

---

## Executive Summary

**FINDING: This was NOT a fleet-wide restart event.**

Only **1 instance** (`aws-luckyus-isalescdp-rw`) actually restarted during the incident window. The initial Prometheus query using `changes()` was misleading - it counts all value changes in the uptime metric (normal increments), not actual restarts.

**Critical Risk Identified:** 41 out of 64 RDS instances are running on `db.t4g.micro`, the same undersized instance type that caused this incident. These instances are at HIGH RISK of similar memory exhaustion failures.

---

## Affected Instances Summary

### Instances That Actually Restarted

| Instance | Restart Time (UTC) | Downtime | Current Status | Restart Reason |
|----------|-------------------|----------|----------------|----------------|
| aws-luckyus-isalescdp-rw | 15:14:38 | ~34 seconds | HEALTHY | Memory exhaustion → Multi-AZ failover |

**Total Affected: 1 instance**

---

## Verification Methods Used

### 1. Prometheus `resets()` Function (Accurate)
```promql
resets(mysql_global_status_uptime{namespace="custom-scrape-iprod-us"}[6h]) > 0
```
**Result:** Only `aws-luckyus-isalescdp-rw` returned a value of 1 (one reset)

### 2. Low Uptime Check
```promql
mysql_global_status_uptime{namespace="custom-scrape-iprod-us"} < 10000
```
**Result:** Only `aws-luckyus-isalescdp-rw` with uptime 6,966 seconds (~1.9 hours)

### 3. AWS RDS Events (Last 24 Hours)
```bash
aws rds describe-events --source-type db-instance --event-categories "failover" --duration 1440
```
**Result:** Only `aws-luckyus-isalescdp-rw` had failover events

### 4. Why `changes()` Was Misleading
The original query `changes(mysql_global_status_uptime[3h]) > 0` returned 59 instances because:
- `changes()` counts ALL value changes, not just resets
- Uptime increments every second, so `changes()` ≈ scrape_count × (scrape_interval)
- This does NOT indicate a restart

---

## Current Fleet Status

### All MySQL Exporters - HEALTHY
```promql
up{namespace="custom-scrape-iprod-us", job=~"db-.*"} == 0
```
**Result:** Empty (all exporters are UP)

```promql
mysql_up{namespace="custom-scrape-iprod-us"} == 0
```
**Result:** Empty (all MySQL connections are UP)

### Fleet Statistics
| Metric | Count |
|--------|-------|
| Total MySQL instances monitored | 59 |
| Instances with restart in last 6h | 1 |
| Exporters currently down | 0 |
| MySQL connections currently down | 0 |

---

## Full Fleet Inventory with Risk Assessment

### HIGH RISK: db.t4g.micro Instances (41 instances)

These instances have the same memory constraints as `aws-luckyus-isalescdp-rw` and are at risk of similar failures:

| # | Instance | Type | Multi-AZ | Current Uptime | Risk |
|---|----------|------|----------|----------------|------|
| 1 | aws-luckyus-isalescdp-rw | db.t4g.micro | Yes | **6,966 sec** (RESTARTED) | **CRITICAL** |
| 2 | aws-luckyus-dbatest-rw | db.t4g.micro | Yes | 8,304,588 sec (96 days) | HIGH |
| 3 | aws-luckyus-fichargecontrol-rw | db.t4g.micro | Yes | 29,485,067 sec (341 days) | HIGH |
| 4 | aws-luckyus-fitax-rw | db.t4g.micro | Yes | 9,860,031 sec (114 days) | HIGH |
| 5 | aws-luckyus-iadmin-rw | db.t4g.micro | Yes | 29,485,303 sec (341 days) | HIGH |
| 6 | aws-luckyus-ibillingcentersrv-rw | db.t4g.micro | Yes | 29,485,388 sec (341 days) | HIGH |
| 7 | aws-luckyus-ibizconfigcenter-rw | db.t4g.micro | Yes | 29,485,507 sec (341 days) | HIGH |
| 8 | aws-luckyus-iehr-rw | db.t4g.micro | Yes | 29,485,799 sec (341 days) | HIGH |
| 9 | aws-luckyus-ifiaccounting-rw | db.t4g.micro | Yes | 29,482,790 sec (341 days) | HIGH |
| 10 | aws-luckyus-igers-rw | db.t4g.micro | Yes | 29,485,589 sec (341 days) | HIGH |
| 11 | aws-luckyus-ijumpserver-jumpserver-rw | db.t4g.micro | Yes | 25,333,665 sec (293 days) | HIGH |
| 12 | aws-luckyus-ilsopdevopsdata-rw | db.t4g.micro | Yes | N/A | HIGH |
| 13 | aws-luckyus-iluckyams-rw | db.t4g.micro | Yes | 7,990,440 sec (92 days) | HIGH |
| 14 | aws-luckyus-iluckyauthapi-rw | db.t4g.micro | Yes | 29,256,411 sec (338 days) | HIGH |
| 15 | aws-luckyus-iluckydorisops-rw | db.t4g.micro | Yes | 25,522,124 sec (295 days) | HIGH |
| 16 | aws-luckyus-iluckymedia-rw | db.t4g.micro | Yes | 29,230,305 sec (338 days) | HIGH |
| 17 | aws-luckyus-iopenadmin-rw | db.t4g.micro | Yes | 29,501,622 sec (341 days) | HIGH |
| 18 | aws-luckyus-iopenlinker-rw | db.t4g.micro | Yes | N/A | HIGH |
| 19 | aws-luckyus-iopenservice-rw | db.t4g.micro | Yes | 29,083,350 sec (336 days) | HIGH |
| 20 | aws-luckyus-iopocp-rw | db.t4g.micro | Yes | 29,501,221 sec (341 days) | HIGH |
| 21 | aws-luckyus-iopshopexpand-rw | db.t4g.micro | Yes | 29,498,141 sec (341 days) | HIGH |
| 22 | aws-luckyus-ipermission-rw | db.t4g.micro | Yes | 29,497,533 sec (341 days) | HIGH |
| 23 | aws-luckyus-ireplenishment-rw | db.t4g.micro | Yes | 26,730,512 sec (309 days) | HIGH |
| 24 | aws-luckyus-iriskcontrolservice-rw | db.t4g.micro | Yes | 22,417,233 sec (259 days) | HIGH |
| 25 | aws-luckyus-isalesmembermarketing-rw | db.t4g.micro | Yes | 25,617,186 sec (296 days) | HIGH |
| 26 | aws-luckyus-iunifiedreconcile-rw | db.t4g.micro | Yes | 29,221,342 sec (338 days) | HIGH |
| 27 | aws-luckyus-mfranchise-rw | db.t4g.micro | Yes | 29,496,805 sec (341 days) | HIGH |
| 28 | aws-luckyus-opempefficiency-rw | db.t4g.micro | Yes | 29,496,647 sec (341 days) | HIGH |
| 29 | aws-luckyus-oplog-rw | db.t4g.micro | Yes | 29,496,505 sec (341 days) | HIGH |
| 30 | aws-luckyus-opproduction-rw | db.t4g.micro | Yes | 29,492,299 sec (341 days) | HIGH |
| 31 | aws-luckyus-opqualitycontrol-rw | db.t4g.micro | Yes | 29,489,802 sec (341 days) | HIGH |
| 32 | aws-luckyus-opshopsale-rw | db.t4g.micro | Yes | 29,486,980 sec (341 days) | HIGH |
| 33 | aws-luckyus-pubdm-rw | db.t4g.micro | Yes | 29,486,829 sec (341 days) | HIGH |
| 34 | aws-luckyus-scm-asset-rw | db.t4g.micro | Yes | 29,501,096 sec (341 days) | HIGH |
| 35 | aws-luckyus-scm-openapi-rw | db.t4g.micro | Yes | 29,500,932 sec (341 days) | HIGH |
| 36 | aws-luckyus-scm-ordering-rw | db.t4g.micro | Yes | 29,500,723 sec (341 days) | HIGH |
| 37 | aws-luckyus-scm-plan-rw | db.t4g.micro | Yes | 29,500,626 sec (341 days) | HIGH |
| 38 | aws-luckyus-scm-purchase-rw | db.t4g.micro | Yes | 29,500,477 sec (341 days) | HIGH |
| 39 | aws-luckyus-scmsrm-rw | db.t4g.micro | Yes | 29,499,767 sec (341 days) | HIGH |
| 40 | aws-luckyus-scm-wds-rw | db.t4g.micro | Yes | 29,500,210 sec (341 days) | HIGH |
| 41 | aws-luckyus-scm-wmssimulate-rw | db.t4g.micro | Yes | 29,500,040 sec (341 days) | HIGH |

### LOW RISK: db.t4g.medium and Larger Instances (23 instances)

| # | Instance | Type | Multi-AZ | Risk |
|---|----------|------|----------|------|
| 1 | aws-luckyus-cdpactivity-rw | db.t4g.medium | Yes | Low |
| 2 | aws-luckyus-devops-rw | db.t4g.medium | Yes | Low |
| 3 | aws-luckyus-framework01-rw | db.t4g.medium | Yes | Low |
| 4 | aws-luckyus-framework02-rw | db.t4g.medium | Yes | Low |
| 5 | aws-luckyus-icyberdata-rw | db.t4g.medium | Yes | Low |
| 6 | aws-luckyus-iotplatform-rw | db.t4g.medium | Yes | Low |
| 7 | aws-luckyus-isalesdatamarketing-rw | db.t4g.medium | Yes | Low |
| 8 | aws-luckyus-isalesprivatedomain-rw | db.t4g.medium | Yes | Low |
| 9 | aws-luckyus-iworkflowmidlayer-rw | db.t4g.medium | Yes | Low |
| 10 | aws-luckyus-opshop-rw | db.t4g.medium | Yes | Low |
| 11 | aws-luckyus-salescrm-rw | db.t4g.medium | Yes | Low |
| 12 | aws-luckyus-salesorder-rw | db.t4g.medium | Yes | Low |
| 13 | aws-luckyus-salespayment-rw | db.t4g.medium | Yes | Low |
| 14 | aws-luckyus-scmcommodity-rw | db.t4g.medium | Yes | Low |
| 15 | aws-luckyus-scm-shopstock-rw | db.t4g.medium | Yes | Low |
| 16 | aws-luckyus-upush-rw | db.t4g.medium | Yes | Low |
| 17 | aws-luckyus-iluckyhealth-rw | db.t3.small | Yes | Low |
| 18 | aws-luckyus-ldas-rw | db.t4g.large | Yes | Low |
| 19 | aws-luckyus-ldas01-rw | db.t4g.large | Yes | Low |
| 20 | aws-luckyus-salesmarketing-rw | db.t4g.xlarge | Yes | Low |
| 21 | aws-luckyus-difynew-rw | db.r5.xlarge | Yes | Low (PostgreSQL) |
| 22 | aws-luckyus-dify-rw | db.r5.xlarge | Yes | Low (PostgreSQL) |
| 23 | aws-luckyus-pgilkmap-rw | db.m5.large | Yes | Low (PostgreSQL) |

---

## Application Impact Assessment

### During Incident Window (15:14:38 - 15:15:12 UTC)

| Impact Area | Assessment |
|-------------|------------|
| Database Connections | Dropped to 0 for 34 seconds on isalescdp |
| Monitoring Gap | ~16 minutes (exporter scrape timeouts before/during failover) |
| Data Loss | None (Multi-AZ failover preserves data) |
| Other Instances | NOT affected |

### Application Error Check
- **CloudWatch Slow Query Logs:** No queries logged during incident (expected - MySQL unavailable)
- **Fleet-wide Impact:** None - only isalescdp was affected

---

## AWS RDS Events (Last 24 Hours)

### Failover Events
| Time (UTC) | Instance | Event |
|------------|----------|-------|
| 15:14:38 | aws-luckyus-isalescdp-rw | Multi-AZ instance failover started |
| 15:15:08 | aws-luckyus-isalescdp-rw | DB instance restarted |
| 15:15:12 | aws-luckyus-isalescdp-rw | Multi-AZ instance failover completed |

### Other Critical Events
| Time (UTC) | Instance | Event |
|------------|----------|-------|
| 15:15:12 | aws-luckyus-isalescdp-rw | The RDS Multi-AZ primary instance is busy and unresponsive |
| 15:19:46 | aws-luckyus-isalescdp-rw | Memory critically low - innodb_buffer_pool_size auto-reduced to 128MB |

---

## Risk Summary

| Risk Level | Instance Type | Count | % of Fleet |
|------------|---------------|-------|------------|
| **CRITICAL** | db.t4g.micro (failed) | 1 | 1.6% |
| **HIGH** | db.t4g.micro | 40 | 62.5% |
| **LOW** | db.t4g.medium+ | 23 | 35.9% |
| **Total** | | 64 | 100% |

**64% of the MySQL fleet is running on undersized db.t4g.micro instances.**

---

## Recommendations

### Immediate Actions (P1)

1. **Upgrade High-Traffic db.t4g.micro Instances**
   - Priority 1: `aws-luckyus-isalescdp-rw` (already experiencing failures)
   - Priority 2: `aws-luckyus-isalesmembermarketing-rw` (same workload type)
   - Target: db.t4g.small (2GB RAM) minimum

2. **Implement Memory Monitoring Across Fleet**
   ```bash
   # Create CloudWatch alarm for all db.t4g.micro instances
   for instance in $(aws rds describe-db-instances --query "DBInstances[?DBInstanceClass=='db.t4g.micro'].DBInstanceIdentifier" --output text); do
     aws cloudwatch put-metric-alarm \
       --alarm-name "RDS-${instance}-LowMemory" \
       --metric-name FreeableMemory \
       --namespace AWS/RDS \
       --dimensions Name=DBInstanceIdentifier,Value=${instance} \
       --threshold 100000000 \
       --comparison-operator LessThanThreshold \
       --evaluation-periods 3 \
       --period 300 \
       --statistic Average
   done
   ```

### Short-Term Actions (P2)

3. **Right-Size Assessment**
   - Review connection counts and memory usage for all db.t4g.micro instances
   - Identify candidates for upgrade based on workload patterns
   - Create upgrade schedule prioritized by business criticality

4. **Fix Prometheus Alert Query**
   - Current: `changes(mysql_global_status_uptime[3h]) > 0` (INCORRECT)
   - Recommended: `resets(mysql_global_status_uptime[1h]) > 0` (CORRECT)

### Long-Term Actions (P3)

5. **Establish Instance Sizing Guidelines**
   - Minimum: db.t4g.small for production workloads
   - Reserve db.t4g.micro for development/testing only
   - Implement automated right-sizing recommendations

6. **Create Fleet-Wide Dashboard**
   - Memory utilization by instance
   - Connection counts
   - Uptime tracking with restart detection

---

## Prometheus Queries for Ongoing Monitoring

```promql
# Detect actual restarts (correct method)
resets(mysql_global_status_uptime{namespace="custom-scrape-iprod-us"}[1h]) > 0

# Low memory warning (< 100MB free)
mysql_global_status_innodb_buffer_pool_bytes_total{namespace="custom-scrape-iprod-us"}
  - mysql_global_status_innodb_buffer_pool_bytes_data{namespace="custom-scrape-iprod-us"} < 100000000

# High connection count
mysql_global_status_threads_connected{namespace="custom-scrape-iprod-us"} > 80

# Exporter health
up{namespace="custom-scrape-iprod-us", job=~"db-.*"} == 0
```

---

## Conclusion

This incident was **isolated to a single instance** (`aws-luckyus-isalescdp-rw`) due to memory exhaustion on an undersized db.t4g.micro instance. However, **64% of the MySQL fleet shares the same risk profile**.

**Key Findings:**
1. NOT a fleet-wide event - only 1 instance restarted
2. Root cause: Memory exhaustion → automated Multi-AZ failover
3. 41 instances at HIGH RISK of similar failure
4. All exporters have fully recovered

**Priority Action:** Upgrade high-risk db.t4g.micro instances before similar failures occur.

---

**Report Generated:** 2026-02-11
**Analyst:** Claude Code DBA Assistant
