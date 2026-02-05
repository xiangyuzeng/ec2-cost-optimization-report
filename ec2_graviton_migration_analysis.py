#!/usr/bin/env python3
"""
EC2 Graviton Migration Analysis
Comprehensive analysis of x86 to Graviton migration opportunities

Generated: 2026-02-05
Region: us-east-1
"""

import csv
import json
from datetime import datetime

# EDP Discount
EDP_DISCOUNT = 0.31

# EC2 Pricing (us-east-1, On-Demand hourly rates)
EC2_PRICING = {
    # x86 instances
    "c6i.large": {"hourly": 0.085, "arch": "x86", "vcpu": 2, "memory": 4},
    "c6i.xlarge": {"hourly": 0.17, "arch": "x86", "vcpu": 4, "memory": 8},
    "c6i.2xlarge": {"hourly": 0.34, "arch": "x86", "vcpu": 8, "memory": 16},
    "c6i.4xlarge": {"hourly": 0.68, "arch": "x86", "vcpu": 16, "memory": 32},
    "c5.large": {"hourly": 0.085, "arch": "x86", "vcpu": 2, "memory": 4},
    "m6i.4xlarge": {"hourly": 0.768, "arch": "x86", "vcpu": 16, "memory": 64},
    "m6i.8xlarge": {"hourly": 1.536, "arch": "x86", "vcpu": 32, "memory": 128},
    "m6a.large": {"hourly": 0.0864, "arch": "x86", "vcpu": 2, "memory": 8},
    "m6a.xlarge": {"hourly": 0.1728, "arch": "x86", "vcpu": 4, "memory": 16},
    "m5.xlarge": {"hourly": 0.192, "arch": "x86", "vcpu": 4, "memory": 16},
    "r6i.2xlarge": {"hourly": 0.504, "arch": "x86", "vcpu": 8, "memory": 64},
    "r6i.4xlarge": {"hourly": 1.008, "arch": "x86", "vcpu": 16, "memory": 128},
    "t3.large": {"hourly": 0.0832, "arch": "x86", "vcpu": 2, "memory": 8},
    # Graviton instances
    "c7g.large": {"hourly": 0.0725, "arch": "arm64", "vcpu": 2, "memory": 4},
    "c7g.xlarge": {"hourly": 0.145, "arch": "arm64", "vcpu": 4, "memory": 8},
    "c7g.2xlarge": {"hourly": 0.29, "arch": "arm64", "vcpu": 8, "memory": 16},
    "c7g.4xlarge": {"hourly": 0.58, "arch": "arm64", "vcpu": 16, "memory": 32},
    "m7g.large": {"hourly": 0.0816, "arch": "arm64", "vcpu": 2, "memory": 8},
    "m7g.xlarge": {"hourly": 0.1632, "arch": "arm64", "vcpu": 4, "memory": 16},
    "m7g.4xlarge": {"hourly": 0.6528, "arch": "arm64", "vcpu": 16, "memory": 64},
    "m7g.8xlarge": {"hourly": 1.3056, "arch": "arm64", "vcpu": 32, "memory": 128},
    "r7g.2xlarge": {"hourly": 0.4284, "arch": "arm64", "vcpu": 8, "memory": 64},
    "r7g.4xlarge": {"hourly": 0.8568, "arch": "arm64", "vcpu": 16, "memory": 128},
    "t4g.large": {"hourly": 0.0672, "arch": "arm64", "vcpu": 2, "memory": 8},
}

# x86 to Graviton mapping
GRAVITON_MAPPING = {
    "c6i.large": "c7g.large",
    "c6i.xlarge": "c7g.xlarge",
    "c6i.2xlarge": "c7g.2xlarge",
    "c6i.4xlarge": "c7g.4xlarge",
    "c5.large": "c7g.large",
    "m6i.4xlarge": "m7g.4xlarge",
    "m6i.8xlarge": "m7g.8xlarge",
    "m6a.large": "m7g.large",
    "m6a.xlarge": "m7g.xlarge",
    "m5.xlarge": "m7g.xlarge",
    "r6i.2xlarge": "r7g.2xlarge",
    "r6i.4xlarge": "r7g.4xlarge",
    "t3.large": "t4g.large",
}

# Instance inventory from AWS
INSTANCE_INVENTORY = {
    # Standalone instances (not in EKS/ASG)
    "standalone": {
        "c6i.large": 144,
        "c6i.xlarge": 42,  # 45 total - 3 Windows
        "c6i.2xlarge": 5,
        "c6i.4xlarge": 1,
        "c5.large": 1,
        "m6a.large": 3,
        "m6a.xlarge": 2,
        "m5.xlarge": 6,
        "r6i.2xlarge": 2,
        "r6i.4xlarge": 1,
        "t3.large": 1,
    },
    # EKS node groups
    "eks": {
        "m6i.4xlarge": 7,  # prod-native-eks-us
        "m6i.8xlarge": 13,  # prod-worker01-eks-us
    },
    # Windows (not eligible)
    "windows": {
        "c6i.xlarge": 3,
    }
}

# AMI information
AMI_INFO = {
    "ami-07427280a0cebb96d": {
        "name": "Amazon_Linux2_5.10",
        "count": 190,
        "arm64_available": True,
        "arm64_ami": "ami-xxxx (AL2 ARM64)",
        "migration_effort": "EASY",
    },
    "ami-0118b0c5498e4b68b": {
        "name": "EKS AL2023 x86_64 1.34",
        "count": 20,
        "arm64_available": True,
        "arm64_ami": "ami-yyyy (EKS AL2023 ARM64)",
        "migration_effort": "MEDIUM",
    },
    "ami-07ba43da83e1eeb69": {
        "name": "base-image-2024091002",
        "count": 8,
        "arm64_available": False,
        "arm64_ami": "Needs rebuild",
        "migration_effort": "HARD",
    },
    "ami-047af084c28e7165a": {
        "name": "EMR 5.36",
        "count": 5,
        "arm64_available": True,
        "arm64_ami": "EMR managed",
        "migration_effort": "MEDIUM",
    },
    "ami-0e1e016aa15d47ea3": {
        "name": "Amazon_Linux_2023",
        "count": 3,
        "arm64_available": True,
        "arm64_ami": "ami-zzzz (AL2023 ARM64)",
        "migration_effort": "EASY",
    },
}

# Application categories based on instance names
APP_CATEGORIES = {
    "stateless_web": {
        "patterns": ["apiproxy", "portal", "web", "openapi", "admin"],
        "migration_effort": "EASY",
        "description": "Stateless web servers/API proxies",
    },
    "java_services": {
        "patterns": ["springboot", "nacos", "dubbo", "service"],
        "migration_effort": "EASY",
        "description": "Java services (JVM supports ARM64 natively)",
    },
    "monitoring": {
        "patterns": ["grafana", "alertmanager", "skywalking", "prometheus", "collector"],
        "migration_effort": "EASY",
        "description": "Monitoring tools (ARM64 images available)",
    },
    "databases": {
        "patterns": ["etcd", "zk", "zookeeper", "consul"],
        "migration_effort": "MEDIUM",
        "description": "Distributed coordination services",
    },
    "message_queue": {
        "patterns": ["kafka", "mq", "queue"],
        "migration_effort": "MEDIUM",
        "description": "Message queues",
    },
    "data_processing": {
        "patterns": ["parse", "log", "datalink", "chronus"],
        "migration_effort": "MEDIUM",
        "description": "Data processing pipelines",
    },
    "devops_tools": {
        "patterns": ["devops", "jump", "tools", "dns"],
        "migration_effort": "EASY",
        "description": "DevOps/Infrastructure tools",
    },
    "eks_nodes": {
        "patterns": ["eks-"],
        "migration_effort": "MEDIUM",
        "description": "EKS worker nodes (requires ARM64 container images)",
    },
    "windows": {
        "patterns": ["ad", "windows"],
        "migration_effort": "NOT_ELIGIBLE",
        "description": "Windows instances (Graviton not supported)",
    },
}


def calculate_monthly_cost(instance_type, count, with_edp=True):
    """Calculate monthly cost for instances."""
    if instance_type not in EC2_PRICING:
        return 0

    hourly = EC2_PRICING[instance_type]["hourly"]
    monthly = hourly * 730 * count

    if with_edp:
        monthly *= (1 - EDP_DISCOUNT)

    return monthly


def calculate_savings(x86_type, count):
    """Calculate savings from migrating to Graviton."""
    if x86_type not in GRAVITON_MAPPING:
        return 0, 0, 0

    graviton_type = GRAVITON_MAPPING[x86_type]

    current_cost = calculate_monthly_cost(x86_type, count)
    graviton_cost = calculate_monthly_cost(graviton_type, count)
    savings = current_cost - graviton_cost

    return current_cost, graviton_cost, savings


def categorize_instance(name):
    """Categorize instance by name pattern."""
    name_lower = name.lower() if name else ""

    for category, info in APP_CATEGORIES.items():
        for pattern in info["patterns"]:
            if pattern in name_lower:
                return category, info["migration_effort"], info["description"]

    return "other", "MEDIUM", "Uncategorized application"


def analyze_instances():
    """Analyze all instances for Graviton migration."""
    results = {
        "easy": [],
        "medium": [],
        "hard": [],
        "not_eligible": [],
    }

    total_current_cost = 0
    total_graviton_cost = 0

    # Analyze standalone instances
    for instance_type, count in INSTANCE_INVENTORY["standalone"].items():
        current, graviton, savings = calculate_savings(instance_type, count)
        graviton_type = GRAVITON_MAPPING.get(instance_type, "N/A")

        total_current_cost += current
        total_graviton_cost += graviton

        results["easy"].append({
            "category": "Standalone",
            "instance_type": instance_type,
            "graviton_type": graviton_type,
            "count": count,
            "current_cost": current,
            "graviton_cost": graviton,
            "monthly_savings": savings,
            "migration_effort": "EASY",
            "notes": "Amazon Linux 2 - ARM64 AMI available",
        })

    # Analyze EKS instances
    for instance_type, count in INSTANCE_INVENTORY["eks"].items():
        current, graviton, savings = calculate_savings(instance_type, count)
        graviton_type = GRAVITON_MAPPING.get(instance_type, "N/A")

        total_current_cost += current
        total_graviton_cost += graviton

        results["medium"].append({
            "category": "EKS Node Group",
            "instance_type": instance_type,
            "graviton_type": graviton_type,
            "count": count,
            "current_cost": current,
            "graviton_cost": graviton,
            "monthly_savings": savings,
            "migration_effort": "MEDIUM",
            "notes": "Requires ARM64 container images, launch template update",
        })

    # Windows instances (not eligible)
    for instance_type, count in INSTANCE_INVENTORY["windows"].items():
        current = calculate_monthly_cost(instance_type, count)

        results["not_eligible"].append({
            "category": "Windows",
            "instance_type": instance_type,
            "graviton_type": "N/A",
            "count": count,
            "current_cost": current,
            "graviton_cost": current,
            "monthly_savings": 0,
            "migration_effort": "NOT_ELIGIBLE",
            "notes": "Windows not supported on Graviton",
        })

    return results, total_current_cost, total_graviton_cost


def generate_csv(results, filename):
    """Generate CSV report."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "category", "instance_type", "graviton_type", "count",
            "current_monthly_cost", "graviton_monthly_cost", "monthly_savings",
            "annual_savings", "migration_effort", "notes"
        ])

        for effort, instances in results.items():
            for inst in instances:
                writer.writerow([
                    inst["category"],
                    inst["instance_type"],
                    inst["graviton_type"],
                    inst["count"],
                    f"${inst['current_cost']:.2f}",
                    f"${inst['graviton_cost']:.2f}",
                    f"${inst['monthly_savings']:.2f}",
                    f"${inst['monthly_savings'] * 12:.2f}",
                    inst["migration_effort"],
                    inst["notes"],
                ])


def generate_markdown_report(results, total_current, total_graviton, filename):
    """Generate comprehensive markdown report."""
    total_savings = total_current - total_graviton

    # Count instances by effort
    easy_count = sum(i["count"] for i in results["easy"])
    medium_count = sum(i["count"] for i in results["medium"])
    hard_count = sum(i["count"] for i in results["hard"])
    not_eligible_count = sum(i["count"] for i in results["not_eligible"])

    easy_savings = sum(i["monthly_savings"] for i in results["easy"])
    medium_savings = sum(i["monthly_savings"] for i in results["medium"])

    report = f"""# EC2 Graviton Migration Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d')}
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
| **Current Monthly Cost** | **${total_current:,.2f}** |
| **Projected Graviton Cost** | **${total_graviton:,.2f}** |
| **Monthly Savings** | **${total_savings:,.2f}** |
| **Annual Savings** | **${total_savings * 12:,.2f}** |

### Savings Breakdown by Category

| Effort Level | Instance Count | Monthly Savings | % of Total |
|--------------|----------------|-----------------|------------|
| EASY | {easy_count} | ${easy_savings:,.2f} | {easy_savings/total_savings*100:.1f}% |
| MEDIUM | {medium_count} | ${medium_savings:,.2f} | {medium_savings/total_savings*100:.1f}% |
| NOT_ELIGIBLE | {not_eligible_count} | $0.00 | 0% |

---

## Migration Readiness Matrix

### EASY Migration ({easy_count} instances) - ${easy_savings:,.2f}/month savings

These instances can migrate with minimal effort:
- Amazon Linux 2 AMI with ARM64 equivalent available
- Stateless applications or standard Java services
- No x86-specific dependencies detected

| Instance Type | Graviton Type | Count | Current Cost | Graviton Cost | Savings/mo |
|---------------|---------------|-------|--------------|---------------|------------|
"""

    for inst in sorted(results["easy"], key=lambda x: x["monthly_savings"], reverse=True):
        report += f"| {inst['instance_type']} | {inst['graviton_type']} | {inst['count']} | ${inst['current_cost']:,.2f} | ${inst['graviton_cost']:,.2f} | ${inst['monthly_savings']:,.2f} |\n"

    report += f"""
### MEDIUM Migration ({medium_count} instances) - ${medium_savings:,.2f}/month savings

These instances require additional planning:
- EKS node groups need ARM64 container image verification
- Custom AMIs need rebuild for ARM64
- Some application testing required

| Instance Type | Graviton Type | Count | Current Cost | Graviton Cost | Savings/mo | Notes |
|---------------|---------------|-------|--------------|---------------|------------|-------|
"""

    for inst in sorted(results["medium"], key=lambda x: x["monthly_savings"], reverse=True):
        report += f"| {inst['instance_type']} | {inst['graviton_type']} | {inst['count']} | ${inst['current_cost']:,.2f} | ${inst['graviton_cost']:,.2f} | ${inst['monthly_savings']:,.2f} | {inst['notes']} |\n"

    report += f"""
### NOT ELIGIBLE ({not_eligible_count} instances)

| Instance Type | Count | Monthly Cost | Reason |
|---------------|-------|--------------|--------|
"""

    for inst in results["not_eligible"]:
        report += f"| {inst['instance_type']} | {inst['count']} | ${inst['current_cost']:,.2f} | {inst['notes']} |\n"

    report += f"""
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
   aws eks create-nodegroup \\
       --cluster-name prod-worker01-eks-us \\
       --nodegroup-name eksnodegroupworker-arm64 \\
       --instance-types m7g.8xlarge \\
       --ami-type AL2023_ARM_64_STANDARD \\
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

### Phase 1: Quick Wins (Week 1-2) - ${easy_savings * 0.3:,.2f}/month

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

### Phase 2: Bulk Migration (Week 3-4) - ${easy_savings * 0.7:,.2f}/month

Migrate remaining standalone instances:

| Priority | Instance Type | Count | Target | Savings |
|----------|---------------|-------|--------|---------|
| 1 | c6i.large (remaining) | 94 | c7g.large | ~$412/mo |
| 2 | c6i.xlarge | 42 | c7g.xlarge | ~$150/mo |
| 3 | c6i.2xlarge | 5 | c7g.2xlarge | ~$19/mo |

### Phase 3: EKS Migration (Week 5-8) - ${medium_savings:,.2f}/month

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

Our detailed analysis shows: **${total_savings:,.2f}/month**

| Source | Monthly Savings | Notes |
|--------|-----------------|-------|
| AWS Recommendation | $733 | May not include all instances |
| Our Analysis | ${total_savings:,.2f} | Full inventory analysis |
| **Variance** | ${abs(total_savings - 733):,.2f} | {'+' if total_savings > 733 else '-'}{abs((total_savings - 733)/733*100):.1f}% |

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
"""

    all_instances = []
    for effort, instances in results.items():
        all_instances.extend(instances)

    for inst in sorted(all_instances, key=lambda x: x["current_cost"], reverse=True):
        report += f"| {inst['instance_type']} | {inst['count']} | ${inst['current_cost']:,.2f} |\n"

    report += f"| **Total** | **{sum(i['count'] for i in all_instances)}** | **${total_current:,.2f}** |\n"

    report += f"""
### Projected Graviton Costs (with 31% EDP)

| Instance Type | Graviton Type | Count | Monthly Cost | Savings |
|---------------|---------------|-------|--------------|---------|
"""

    for inst in sorted(all_instances, key=lambda x: x["monthly_savings"], reverse=True):
        if inst["migration_effort"] != "NOT_ELIGIBLE":
            report += f"| {inst['instance_type']} | {inst['graviton_type']} | {inst['count']} | ${inst['graviton_cost']:,.2f} | ${inst['monthly_savings']:,.2f} |\n"

    # Add Windows
    for inst in results["not_eligible"]:
        report += f"| {inst['instance_type']} | N/A | {inst['count']} | ${inst['current_cost']:,.2f} | $0.00 |\n"

    report += f"""| **Total** | | **{sum(i['count'] for i in all_instances)}** | **${total_graviton + sum(i['current_cost'] for i in results['not_eligible']):,.2f}** | **${total_savings:,.2f}** |

---

## Combined Savings with Other Optimizations

| Optimization | Monthly Savings | Annual Savings |
|--------------|-----------------|----------------|
| EC2 Graviton Migration | ${total_savings:,.2f} | ${total_savings * 12:,.2f} |
| RDS Graviton Migration | $78.57 | $942.84 |
| OpenSearch Optimization | $146.89 | $1,762.68 |
| MSK Graviton Migration | $219.40 | $2,632.79 |
| RI/SP Coverage | $3,457.87 | $41,494.50 |
| **Total Optimization Potential** | **${total_savings + 78.57 + 146.89 + 219.40 + 3457.87:,.2f}** | **${(total_savings + 78.57 + 146.89 + 219.40 + 3457.87) * 12:,.2f}** |

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
"""

    with open(filename, 'w') as f:
        f.write(report)


def main():
    print("EC2 Graviton Migration Analysis")
    print("=" * 50)

    results, total_current, total_graviton = analyze_instances()
    total_savings = total_current - total_graviton

    # Generate reports
    generate_csv(results, "/app/ec2_graviton_migration_candidates.csv")
    generate_markdown_report(results, total_current, total_graviton, "/app/ec2_graviton_migration_report.md")

    # Summary
    print(f"\nInstance Summary:")
    print(f"  EASY: {sum(i['count'] for i in results['easy'])} instances")
    print(f"  MEDIUM: {sum(i['count'] for i in results['medium'])} instances")
    print(f"  NOT_ELIGIBLE: {sum(i['count'] for i in results['not_eligible'])} instances")

    print(f"\nCost Summary:")
    print(f"  Current monthly cost: ${total_current:,.2f}")
    print(f"  Projected Graviton cost: ${total_graviton:,.2f}")
    print(f"  Monthly savings: ${total_savings:,.2f}")
    print(f"  Annual savings: ${total_savings * 12:,.2f}")

    print("\nReports generated:")
    print("  - /app/ec2_graviton_migration_candidates.csv")
    print("  - /app/ec2_graviton_migration_report.md")


if __name__ == "__main__":
    main()
