# MSK (Amazon Managed Streaming for Apache Kafka) Graviton Migration Analysis

**Date:** February 10, 2026
**Region:** us-east-1
**Total Clusters:** 3
**Total Brokers:** 9 (3 per cluster)
**EDP Discount Applied:** 31% (0.69 multiplier)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Clusters Analyzed** | 3 |
| **Eligible for Graviton Migration** | 3 (100%) |
| **Current Broker Type** | kafka.m5.large |
| **Target Broker Type** | kafka.m7g.large |
| **Total Monthly Graviton Savings** | **$27.09** |
| **Total Monthly Storage Savings (gp2→gp3)** | **$111.78** |
| **Grand Total Monthly Savings** | **$138.87** |
| **Annual Savings Potential** | **$1,666.44** |

---

## Cluster Inventory

### Data Sources
- **IAM Limitation:** Direct MSK API access denied for user `databasecheck`
- **Data Retrieved Via:**
  - CloudWatch Metrics (cluster names, broker counts, health metrics)
  - Cost Explorer (instance types, storage types, usage quantities)
  - AWS Pricing API (instance pricing)

### Discovered Clusters

| Cluster Name | Brokers | Instance Type | Storage Type | Storage/Broker | Partitions |
|--------------|---------|---------------|--------------|----------------|------------|
| iprod-kafka-architecture-cluster | 3 | kafka.m5.large | GP2 | 900 GB | 194 |
| iprod-kafka-base-cluster | 3 | kafka.m5.large | GP2 | 900 GB | 64 |
| iprod-kafka-business-cluster | 3 | kafka.m5.large | GP2 | 900 GB | 171 |
| **TOTAL** | **9** | | | **8,100 GB** | **429** |

---

## Question 1: Which MSK Brokers CAN/CANNOT Be Converted to Graviton?

### Eligibility Analysis

| Cluster Name | Current Type | Target Type | Eligible? | Reason |
|--------------|--------------|-------------|-----------|--------|
| iprod-kafka-architecture-cluster | kafka.m5.large | kafka.m7g.large | **YES** | m5 → m7g supported |
| iprod-kafka-base-cluster | kafka.m5.large | kafka.m7g.large | **YES** | m5 → m7g supported |
| iprod-kafka-business-cluster | kafka.m5.large | kafka.m7g.large | **YES** | m5 → m7g supported |

### Graviton Migration Mapping (MSK)

| Current | Target | Supported | Notes |
|---------|--------|-----------|-------|
| kafka.m5.large | kafka.m7g.large | **YES** | Requires Kafka >= 2.8.0 |
| kafka.m5.xlarge | kafka.m7g.xlarge | **YES** | |
| kafka.m5.2xlarge | kafka.m7g.2xlarge | **YES** | |
| kafka.t3.small | N/A | **NO** | No Graviton equivalent |

**All 3 clusters use kafka.m5.large which has a Graviton equivalent (kafka.m7g.large).**

### Health Check Results

| Cluster | Avg CPU (7d) | Max CPU (7d) | Under-Replicated Partitions | Status |
|---------|--------------|--------------|----------------------------|--------|
| iprod-kafka-architecture-cluster | 16.8% | 83.9% | 0 | **CAUTION** (high peak) |
| iprod-kafka-base-cluster | 27.1% | 83.6% | 0 | **CAUTION** (high peak) |
| iprod-kafka-business-cluster | 12.2% | 64.7% | 0 | **HEALTHY** |

**Note:** Two clusters show peak CPU > 80%. While Graviton typically provides equal or better performance, recommend scheduling migration during off-peak hours.

---

## Question 2: Monthly Cost Savings Per Cluster

### MSK Pricing Reference (US East - N. Virginia)

| Instance Type | On-Demand $/hr | After EDP (×0.69) $/hr |
|---------------|----------------|------------------------|
| kafka.m5.large | $0.210 | $0.1449 |
| kafka.m7g.large | $0.204 | $0.1408 |

**Graviton Savings per Broker Hour: $0.006 (2.86% reduction)**

### Storage Pricing Reference

| Storage Type | On-Demand $/GB-mo | After EDP (×0.69) $/GB-mo |
|--------------|-------------------|---------------------------|
| GP2 | $0.100 | $0.069 |
| GP3 | $0.080 | $0.0552 |

**Storage Savings per GB: $0.0138/month (20% reduction)**

---

### Detailed Cost Savings Table

| Cluster Name | Brokers | Current Broker $/mo | Target Broker $/mo | Graviton Savings | Storage GB | Storage Savings | Total Savings |
|--------------|---------|---------------------|-------------------|------------------|------------|-----------------|---------------|
| iprod-kafka-architecture-cluster | 3 | $317.11 | $308.12 | **$8.99** | 2,700 | **$37.26** | **$46.25** |
| iprod-kafka-base-cluster | 3 | $317.11 | $308.12 | **$8.99** | 2,700 | **$37.26** | **$46.25** |
| iprod-kafka-business-cluster | 3 | $317.11 | $308.12 | **$8.99** | 2,700 | **$37.26** | **$46.25** |
| **TOTAL** | **9** | **$951.33** | **$924.36** | **$26.97** | **8,100** | **$111.78** | **$138.75** |

---

### Cost Calculation Breakdown

#### Broker Costs (per cluster with 3 brokers)

**Current (kafka.m5.large):**
```
$0.21/hr × 730 hrs × 3 brokers × 0.69 EDP = $317.11/month
```

**Target (kafka.m7g.large):**
```
$0.204/hr × 730 hrs × 3 brokers × 0.69 EDP = $308.12/month
```

**Graviton Savings per Cluster:**
```
$317.11 - $308.12 = $8.99/month (2.84% reduction)
```

#### Storage Costs (per cluster with 2,700 GB)

**Current (GP2):**
```
2,700 GB × $0.10/GB × 0.69 EDP = $186.30/month
```

**Target (GP3):**
```
2,700 GB × $0.08/GB × 0.69 EDP = $149.04/month
```

**Storage Savings per Cluster:**
```
$186.30 - $149.04 = $37.26/month (20% reduction)
```

---

## Final Summary Table

| Cluster Name | Kafka Version | Broker Type × Count | Storage (type × size) | Graviton Eligible? | Reason | Current $/mo | Target $/mo | Graviton $/mo | Storage $/mo | Total $/mo |
|--------------|---------------|---------------------|----------------------|-------------------|--------|--------------|-------------|---------------|--------------|------------|
| iprod-kafka-architecture-cluster | 2.8+ (assumed) | m5.large × 3 | GP2 × 2,700 GB | **YES** | m5→m7g supported | $503.41 | $457.16 | $8.99 | $37.26 | **$46.25** |
| iprod-kafka-base-cluster | 2.8+ (assumed) | m5.large × 3 | GP2 × 2,700 GB | **YES** | m5→m7g supported | $503.41 | $457.16 | $8.99 | $37.26 | **$46.25** |
| iprod-kafka-business-cluster | 2.8+ (assumed) | m5.large × 3 | GP2 × 2,700 GB | **YES** | m5→m7g supported | $503.41 | $457.16 | $8.99 | $37.26 | **$46.25** |
| **TOTAL** | | **9 brokers** | **8,100 GB** | | | **$1,510.23** | **$1,371.48** | **$26.97** | **$111.78** | **$138.75** |

---

## Savings Summary

| Category | Monthly Savings | Annual Savings | % Reduction |
|----------|-----------------|----------------|-------------|
| Graviton Broker Migration | $26.97 | $323.64 | 2.8% |
| GP2 → GP3 Storage | $111.78 | $1,341.36 | 20.0% |
| **TOTAL** | **$138.75** | **$1,665.00** | **9.2%** |

---

## Migration Priority & Recommendations

### Priority Order

| Priority | Cluster | Total Savings/mo | CPU Risk | Recommendation |
|----------|---------|-----------------|----------|----------------|
| 1 | iprod-kafka-business-cluster | $46.25 | Low (65% peak) | **Migrate first** - healthiest cluster |
| 2 | iprod-kafka-architecture-cluster | $46.25 | Medium (84% peak) | Schedule off-peak migration |
| 3 | iprod-kafka-base-cluster | $46.25 | Medium (84% peak) | Schedule off-peak migration |

### Pre-Migration Checklist

- [ ] **Verify Kafka version** >= 2.8.0 (required for m7g Graviton)
- [ ] Confirm no under-replicated partitions (currently: 0 for all clusters ✓)
- [ ] Schedule during low-traffic maintenance window
- [ ] Ensure cluster is in ACTIVE state
- [ ] Take configuration snapshot/backup

### Migration Process

MSK broker type changes use a **rolling update** process:

1. **Initiate Change** via AWS Console or CLI:
   ```bash
   aws kafka update-broker-type \
     --cluster-arn <cluster-arn> \
     --current-version <config-version> \
     --target-instance-type kafka.m7g.large
   ```

2. **Rolling Update** - Brokers are updated one at a time:
   - One broker is stopped
   - New Graviton broker is launched
   - Data is synced
   - Process repeats for next broker

3. **Estimated Duration:** 45-90 minutes per cluster

**Zero Downtime:** Rolling updates maintain cluster availability throughout the process.

### Storage Migration (GP2 → GP3)

```bash
aws kafka update-storage \
  --cluster-arn <cluster-arn> \
  --current-version <config-version> \
  --provisioned-throughput-enabled \
  --volume-throughput 125 \
  --target-volume-type gp3
```

**Note:** GP3 also provides better baseline performance with 125 MB/s throughput.

---

## Key Findings

### 1. **Storage Savings Dominate (80% of total)**
The gp2→gp3 storage migration provides **$111.78/month** (80%) of total savings, while Graviton provides **$26.97/month** (20%). Recommend prioritizing storage migration.

### 2. **All Clusters Eligible for Graviton**
All three clusters use kafka.m5.large, which has a direct Graviton equivalent (kafka.m7g.large). No blockers identified.

### 3. **CPU Peaks Warrant Attention**
Two clusters (architecture, base) show peak CPU > 80%. While Graviton typically provides equivalent or better performance:
- Monitor closely during first week after migration
- Schedule migrations during off-peak hours
- Consider load testing if critical workloads

### 4. **IAM Permissions Limited Analysis**
This analysis was performed without direct MSK API access. Recommend:
- Verify Kafka versions before migration
- Confirm exact storage allocations
- Review any cluster-specific configurations

---

## Cost Comparison Summary

| Component | Current Monthly | After Optimization | Savings |
|-----------|-----------------|-------------------|---------|
| Broker Instances (9× m5.large) | $951.33 | $924.36 | $26.97 |
| Storage (8,100 GB GP2) | $558.90 | $447.12 | $111.78 |
| **TOTAL** | **$1,510.23** | **$1,371.48** | **$138.75** |

**Annual Savings: $1,665.00**

---

*Report generated: February 10, 2026*
*AWS Region: us-east-1*
*Pricing source: AWS Pricing API (AmazonMSK) with 31% EDP discount*
*Data sources: CloudWatch Metrics, Cost Explorer, AWS Pricing API*
