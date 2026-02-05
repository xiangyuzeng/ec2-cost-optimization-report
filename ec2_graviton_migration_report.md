# EC2 Graviton Migration Analysis

**Generated:** 2026-02-05
**Region:** us-east-1
**EDP Discount Applied:** 31%

---

## Executive Summary

### Migration Opportunity: 228 Linux Instances → Graviton

Your EC2 fleet has **228 x86 Linux instances** that are candidates for Graviton migration, plus **3 Windows instances** that are not eligible.

| Metric | Value |
|--------|-------|
| Total x86 Linux Instances | 228 |
| Windows Instances (Not Eligible) | 3 |
| **Current Monthly Cost** | **$25,711.37** |
| **Projected Graviton Cost** | **$21,914.02** |
| **Monthly Savings** | **$3,797.34** |
| **Annual Savings** | **$45,568.13** |

### Savings Breakdown by Category

| Effort Level | Instance Count | Monthly Savings | % of Total |
|--------------|----------------|-----------------|------------|
| EASY | 208 | $1,882.48 | 49.6% |
| MEDIUM | 20 | $1,914.87 | 50.4% |
| NOT_ELIGIBLE | 3 | $0.00 | 0% |

---

## Migration Readiness Matrix

### EASY Migration (208 instances) - $1,882.48/month savings

These instances can migrate with minimal effort:
- Amazon Linux 2 AMI with ARM64 equivalent available
- Stateless applications or standard Java services
- No x86-specific dependencies detected

| Instance Type | Graviton Type | Count | Current Cost | Graviton Cost | Savings/mo |
|---------------|---------------|-------|--------------|---------------|------------|
| c6i.large | c7g.large | 144 | $6,165.29 | $5,258.63 | $906.66 |
| c6i.xlarge | c7g.xlarge | 42 | $3,596.42 | $3,067.53 | $528.89 |
| c6i.2xlarge | c7g.2xlarge | 5 | $856.29 | $730.36 | $125.93 |
| m5.xlarge | m7g.xlarge | 6 | $580.26 | $493.22 | $87.04 |
| r6i.2xlarge | r7g.2xlarge | 2 | $507.73 | $431.57 | $76.16 |
| r6i.4xlarge | r7g.4xlarge | 1 | $507.73 | $431.57 | $76.16 |
| c6i.4xlarge | c7g.4xlarge | 1 | $342.52 | $292.15 | $50.37 |
| m6a.xlarge | m7g.xlarge | 2 | $174.08 | $164.41 | $9.67 |
| t3.large | t4g.large | 1 | $41.91 | $33.85 | $8.06 |
| m6a.large | m7g.large | 3 | $130.56 | $123.31 | $7.25 |
| c5.large | c7g.large | 1 | $42.81 | $36.52 | $6.30 |

### MEDIUM Migration (20 instances) - $1,914.87/month savings

These instances require additional planning:
- EKS node groups need ARM64 container image verification
- Custom AMIs need rebuild for ARM64
- Some application testing required

| Instance Type | Graviton Type | Count | Current Cost | Graviton Cost | Savings/mo | Notes |
|---------------|---------------|-------|--------------|---------------|------------|-------|
| m6i.8xlarge | m7g.8xlarge | 13 | $10,057.88 | $8,549.20 | $1,508.68 | Requires ARM64 container images, launch template update |
| m6i.4xlarge | m7g.4xlarge | 7 | $2,707.89 | $2,301.71 | $406.18 | Requires ARM64 container images, launch template update |

### NOT ELIGIBLE (3 instances)

| Instance Type | Count | Monthly Cost | Reason |
|---------------|-------|--------------|--------|
| c6i.xlarge | 3 | $256.89 | Windows not supported on Graviton |

---

## Instance Type Migration Mapping

| Current (x86) | Target (Graviton) | Price Reduction | Notes |
|---------------|-------------------|-----------------|-------|
| c6i.large | c7g.large | 14.7% | Compute optimized |
| c6i.xlarge | c7g.xlarge | 14.7% | Compute optimized |
| c6i.2xlarge | c7g.2xlarge | 14.7% | Compute optimized |
| c6i.4xlarge | c7g.4xlarge | 14.7% | Compute optimized |
| c5.large | c7g.large | 14.7% | Previous gen → current Graviton |
| m6i.4xlarge | m7g.4xlarge | 15.0% | General purpose |
| m6i.8xlarge | m7g.8xlarge | 15.0% | General purpose |
| m6a.large | m7g.large | 5.6% | Already AMD, smaller delta |
| m6a.xlarge | m7g.xlarge | 5.6% | Already AMD, smaller delta |
| m5.xlarge | m7g.xlarge | 15.0% | Previous gen → current Graviton |
| r6i.2xlarge | r7g.2xlarge | 15.0% | Memory optimized |
| r6i.4xlarge | r7g.4xlarge | 15.0% | Memory optimized |
| t3.large | t4g.large | 19.2% | Burstable |

---

## AMI Migration Strategy

| Current AMI | Count | ARM64 Strategy | Effort |
|-------------|-------|----------------|--------|
| Amazon Linux 2 | 190 | Use AWS ARM64 AMI directly | EASY |
| EKS AL2023 x86_64 | 20 | Update nodegroup to ARM64 AMI type | MEDIUM |
| Custom base-image | 8 | Rebuild image for ARM64 | HARD |
| EMR 5.36 | 5 | AWS provides ARM64 EMR nodes | MEDIUM |
| Amazon Linux 2023 | 3 | Use AWS ARM64 AMI directly | EASY |
| Windows | 3 | Not eligible | N/A |

---

## EKS Graviton Migration

### Current EKS Node Groups

| Cluster | Node Group | Instance Type | Count | Graviton Target |
|---------|------------|---------------|-------|-----------------|
| prod-native-eks-us | eksNativeNodegroup | m6i.4xlarge | 7 | m7g.4xlarge |
| prod-worker01-eks-us | eksnodegroupworker | m6i.8xlarge | 13 | m7g.8xlarge |
| prod-worker01-eks-us | nodegroup | m6i.4xlarge | ~4 | m7g.4xlarge |

### EKS Migration Steps

1. **Verify Container Image ARM64 Support**
   ```bash
   # Check if images are multi-arch
   docker manifest inspect <image>:tag

   # Or use crane
   crane manifest <image>:tag | jq '.manifests[].platform'
   ```

2. **Create ARM64 Node Group** (parallel to existing)
   ```bash
   aws eks create-nodegroup \
       --cluster-name prod-worker01-eks-us \
       --nodegroup-name eksnodegroupworker-arm64 \
       --instance-types m7g.8xlarge \
       --ami-type AL2023_ARM_64_STANDARD \
       --scaling-config minSize=1,maxSize=13,desiredSize=1
   ```

3. **Add Node Selectors/Tolerations**
   ```yaml
   # For workloads that must stay on x86
   nodeSelector:
     kubernetes.io/arch: amd64

   # For workloads ready for ARM64
   nodeSelector:
     kubernetes.io/arch: arm64
   ```

4. **Gradual Migration**
   - Start with stateless workloads
   - Monitor performance
   - Scale up ARM64, scale down x86

---

## Application Migration Categories

### Java Applications (EASY)

Java applications run natively on ARM64 with no code changes:
- **Instances:** nacos, springboot services, dubbo
- **Action:** Update AMI, restart
- **Risk:** LOW

### Monitoring Stack (EASY)

All major monitoring tools support ARM64:
- **Grafana:** ARM64 images available
- **Prometheus/Alertmanager:** ARM64 images available
- **SkyWalking:** ARM64 images available
- **Action:** Update AMI or container images
- **Risk:** LOW

### Infrastructure Services (EASY)

- **DNS servers:** BIND supports ARM64
- **Jump servers:** No architecture dependency
- **DevOps tools:** Most support ARM64
- **Action:** Update AMI
- **Risk:** LOW

### Stateful Services (MEDIUM)

Coordination services need careful migration:
- **etcd:** ARM64 supported
- **ZooKeeper:** ARM64 supported
- **Consul:** ARM64 supported
- **Action:** Rolling upgrade with testing
- **Risk:** MEDIUM

---

## Phased Migration Plan

### Phase 1: Quick Wins (Week 1-2) - $564.74/month

Migrate the easiest instances first:

| Priority | Instance Type | Count | Target | Savings |
|----------|---------------|-------|--------|---------|
| 1 | c6i.large (stateless) | 50 | c7g.large | ~$220/mo |
| 2 | m5.xlarge | 6 | m7g.xlarge | ~$13/mo |
| 3 | t3.large | 1 | t4g.large | ~$0.80/mo |

**Steps:**
1. Create ARM64 AMI (or use AWS provided)
2. Test on 1-2 instances
3. Update launch configurations
4. Replace instances via rolling deployment

### Phase 2: Bulk Migration (Week 3-4) - $1,317.73/month

Migrate remaining standalone instances:

| Priority | Instance Type | Count | Target | Savings |
|----------|---------------|-------|--------|---------|
| 1 | c6i.large (remaining) | 94 | c7g.large | ~$412/mo |
| 2 | c6i.xlarge | 42 | c7g.xlarge | ~$150/mo |
| 3 | c6i.2xlarge | 5 | c7g.2xlarge | ~$19/mo |

### Phase 3: EKS Migration (Week 5-8) - $1,914.87/month

Migrate EKS node groups:

| Priority | Cluster | Node Group | Savings |
|----------|---------|------------|---------|
| 1 | prod-worker01-eks-us | eksnodegroupworker | ~$290/mo |
| 2 | prod-native-eks-us | eksNativeNodegroup | ~$58/mo |

**Steps:**
1. Audit container images for ARM64 support
2. Create parallel ARM64 node group
3. Migrate workloads with node selectors
4. Decommission x86 nodes

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Application incompatibility | LOW | HIGH | Test in staging first |
| Performance regression | LOW | MEDIUM | Benchmark critical paths |
| Container image not ARM64 | MEDIUM | MEDIUM | Use multi-arch images |
| Rollback required | LOW | LOW | Keep x86 ASG/nodes available |

---

## Validation Against AWS Recommendations

### AWS Cost Optimization Hub Estimate: $733/month

Our detailed analysis shows: **$3,797.34/month**

| Source | Monthly Savings | Notes |
|--------|-----------------|-------|
| AWS Recommendation | $733 | May not include all instances |
| Our Analysis | $3,797.34 | Full inventory analysis |
| **Variance** | $3,064.34 | +418.1% |

The variance may be due to:
- AWS recommendation covers subset of instances
- Different pricing assumptions
- EDP discount application differences
- Instance coverage scope

---

## Cost Summary

### Current x86 Costs (with 31% EDP)

| Instance Type | Count | Monthly Cost |
|---------------|-------|--------------|
| m6i.8xlarge | 13 | $10,057.88 |
| c6i.large | 144 | $6,165.29 |
| c6i.xlarge | 42 | $3,596.42 |
| m6i.4xlarge | 7 | $2,707.89 |
| c6i.2xlarge | 5 | $856.29 |
| m5.xlarge | 6 | $580.26 |
| r6i.2xlarge | 2 | $507.73 |
| r6i.4xlarge | 1 | $507.73 |
| c6i.4xlarge | 1 | $342.52 |
| c6i.xlarge | 3 | $256.89 |
| m6a.xlarge | 2 | $174.08 |
| m6a.large | 3 | $130.56 |
| c5.large | 1 | $42.81 |
| t3.large | 1 | $41.91 |
| **Total** | **231** | **$25,711.37** |

### Projected Graviton Costs (with 31% EDP)

| Instance Type | Graviton Type | Count | Monthly Cost | Savings |
|---------------|---------------|-------|--------------|---------|
| m6i.8xlarge | m7g.8xlarge | 13 | $8,549.20 | $1,508.68 |
| c6i.large | c7g.large | 144 | $5,258.63 | $906.66 |
| c6i.xlarge | c7g.xlarge | 42 | $3,067.53 | $528.89 |
| m6i.4xlarge | m7g.4xlarge | 7 | $2,301.71 | $406.18 |
| c6i.2xlarge | c7g.2xlarge | 5 | $730.36 | $125.93 |
| m5.xlarge | m7g.xlarge | 6 | $493.22 | $87.04 |
| r6i.2xlarge | r7g.2xlarge | 2 | $431.57 | $76.16 |
| r6i.4xlarge | r7g.4xlarge | 1 | $431.57 | $76.16 |
| c6i.4xlarge | c7g.4xlarge | 1 | $292.15 | $50.37 |
| m6a.xlarge | m7g.xlarge | 2 | $164.41 | $9.67 |
| t3.large | t4g.large | 1 | $33.85 | $8.06 |
| m6a.large | m7g.large | 3 | $123.31 | $7.25 |
| c5.large | c7g.large | 1 | $36.52 | $6.30 |
| c6i.xlarge | N/A | 3 | $256.89 | $0.00 |
| **Total** | | **231** | **$22,170.91** | **$3,797.34** |

---

## Combined Savings with Other Optimizations

| Optimization | Monthly Savings | Annual Savings |
|--------------|-----------------|----------------|
| EC2 Graviton Migration | $3,797.34 | $45,568.13 |
| RDS Graviton Migration | $78.57 | $942.84 |
| OpenSearch Optimization | $146.89 | $1,762.68 |
| MSK Graviton Migration | $219.40 | $2,632.79 |
| RI/SP Coverage | $3,457.87 | $41,494.50 |
| **Total Optimization Potential** | **$7,700.07** | **$92,400.89** |

---

## Pre-Migration Checklist

- [ ] Audit all applications for x86-specific dependencies
- [ ] Verify ARM64 AMI availability
- [ ] Test critical applications on Graviton instances
- [ ] Update CI/CD pipelines for multi-arch builds
- [ ] Verify container images are multi-arch
- [ ] Update monitoring dashboards
- [ ] Create rollback procedures
- [ ] Schedule maintenance windows
- [ ] Notify stakeholders

---

## Files Generated

- CSV Report: `/app/ec2_graviton_migration_candidates.csv`
- Analysis Script: `/app/ec2_graviton_migration_analysis.py`
- This Report: `/app/ec2_graviton_migration_report.md`
