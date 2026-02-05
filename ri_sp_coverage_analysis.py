#!/usr/bin/env python3
"""
Reserved Instance and Savings Plans Coverage Analysis
Analyzes RI/SP coverage and provides purchase recommendations

Generated: 2026-02-05
Region: us-east-1
"""

import csv
import json
from datetime import datetime, timedelta

# =============================================================================
# ACTIVE RESERVED INSTANCES DATA
# =============================================================================

EC2_RIS = [
    {"instance_type": "c6i.large", "count": 129, "hourly_rate": 0.05623, "platform": "Linux/UNIX", "expiration": "2026-08-28"},
    {"instance_type": "c6i.xlarge", "count": 26, "hourly_rate": 0.11246, "platform": "Linux/UNIX", "expiration": "2026-08-28"},
    {"instance_type": "c6i.xlarge", "count": 3, "hourly_rate": 0.29646, "platform": "Windows", "expiration": "2026-08-28"},
    {"instance_type": "c6i.2xlarge", "count": 7, "hourly_rate": 0.22491, "platform": "Linux/UNIX", "expiration": "2026-08-28"},
    {"instance_type": "c6i.4xlarge", "count": 1, "hourly_rate": 0.44982, "platform": "Linux/UNIX", "expiration": "2026-08-28"},
    {"instance_type": "c5.large", "count": 1, "hourly_rate": 0.054, "platform": "Linux/UNIX", "expiration": "2026-08-28"},
    {"instance_type": "m6i.4xlarge", "count": 7, "hourly_rate": 0.50803, "platform": "Linux/UNIX", "expiration": "2026-08-27"},
    {"instance_type": "m6i.8xlarge", "count": 13, "hourly_rate": 1.01606, "platform": "Linux/UNIX", "expiration": "2026-08-27"},
    {"instance_type": "m6a.large", "count": 3, "hourly_rate": 0.05715, "platform": "Linux/UNIX", "expiration": "2026-08-27"},
    {"instance_type": "m6a.xlarge", "count": 2, "hourly_rate": 0.11431, "platform": "Linux/UNIX", "expiration": "2026-08-27"},
    {"instance_type": "m5.xlarge", "count": 5, "hourly_rate": 0.121, "platform": "Linux/UNIX", "expiration": "2026-08-27"},
    {"instance_type": "m4.large", "count": 1, "hourly_rate": 0.062, "platform": "Linux/UNIX", "expiration": "2026-08-28"},
    {"instance_type": "m4.xlarge", "count": 1, "hourly_rate": 0.1239, "platform": "Linux/UNIX", "expiration": "2026-08-27"},
    {"instance_type": "r6i.2xlarge", "count": 2, "hourly_rate": 0.3334, "platform": "Linux/UNIX", "expiration": "2026-08-28"},
    {"instance_type": "r6i.4xlarge", "count": 1, "hourly_rate": 0.66679, "platform": "Linux/UNIX", "expiration": "2026-08-27"},
]

RDS_RIS = [
    {"instance_class": "db.t4g.medium", "count": 1, "hourly_rate": 0.093, "engine": "mysql", "multi_az": True, "expiration": "2026-08-27", "state": "active"},
    # Retired RIs - NOT providing coverage anymore:
    # {"instance_class": "db.t4g.medium", "count": 13, "state": "retired"},
    # {"instance_class": "db.m5.large", "count": 1, "state": "retired"},
    # {"instance_class": "db.r5.xlarge", "count": 1, "state": "retired"},
    # etc...
]

ELASTICACHE_RIS = [
    {"node_type": "cache.m6g.large", "count": 2, "hourly_rate": 0.102, "engine": "redis", "expiration": "2026-08-27", "state": "active"},
]

OPENSEARCH_RIS = [
    {"instance_type": "m5.large.search", "count": 8, "hourly_rate": 0.098, "expiration": "2026-08-27", "state": "active"},
    # Retired:
    # {"instance_type": "m5.xlarge.search", "count": 4, "state": "retired"},
    # {"instance_type": "m7g.large.search", "count": 3, "state": "retired"},
    # {"instance_type": "r6g.large.search", "count": 2, "state": "retired"},
]

# =============================================================================
# COST DATA FROM COST EXPLORER (January 2026)
# =============================================================================

COST_DATA = {
    "ec2": {
        "total": 26693.06,
        "ri_covered": 24131.45,
        "on_demand": 2561.61,
        "on_demand_breakdown": {
            "c6i.2xlarge": 1264.80,
            "c6i.xlarge": 642.74,
            "c6i.4xlarge": 505.92,
            "m5.xlarge": 102.03,
            "t3.large": 44.21,
            "other": 1.90,
        }
    },
    "rds": {
        "total": 5527.28,
        "ri_covered": 69.19,
        "on_demand": 5458.09,
        "on_demand_breakdown": {
            "db.r5.xlarge": 1488.00,
            "db.t4g.medium": 1439.64,
            "db.t4g.micro": 900.31,
            "db.t4g.xlarge": 384.65,
            "db.t4g.large": 383.90,
            "db.m5.large": 264.86,
            "db.t3.small": 80.10,
            "other": 516.62,
        }
    },
    "elasticache": {
        "total": 2313.84,
        "ri_covered": 151.78,
        "on_demand": 2162.06,
        "on_demand_breakdown": {
            "cache.t4g.micro": 1535.62,
            "cache.t4g.small": 357.12,
            "cache.t4g.medium": 193.44,
            "cache.t3.micro": 75.89,
        }
    },
    "opensearch": {
        "total": 2646.52,
        "ri_covered": 583.30,
        "on_demand": 2063.22,
    },
    "total": {
        "all_services": 49644.91,
        "ri_covered": 24935.72,
        "on_demand": 24709.19,
        "savings_plans": 0,
    }
}

# RI Utilization from Cost Explorer
RI_UTILIZATION = {
    "utilization_percentage": 99.997,
    "purchased_hours": 150288,
    "total_actual_hours": 150283.53,
    "unused_hours": 4.47,
    "on_demand_cost_of_ri_hours": 36318.12,
    "net_ri_savings": 12186.66,
    "total_amortized_fee": 24131.45,
}


def calculate_coverage():
    """Calculate RI coverage percentages for each service."""
    coverage = {}
    for service, data in COST_DATA.items():
        if service == "total":
            continue
        if data["total"] > 0:
            coverage[service] = {
                "total": data["total"],
                "ri_covered": data["ri_covered"],
                "on_demand": data["on_demand"],
                "coverage_pct": (data["ri_covered"] / data["total"]) * 100,
                "gap_pct": (data["on_demand"] / data["total"]) * 100,
            }
    return coverage


def estimate_ri_savings(on_demand_cost, discount_rate=0.30):
    """Estimate potential savings from purchasing RIs."""
    # Typical RI savings: 30-40% for 1-year No Upfront
    return on_demand_cost * discount_rate


def generate_recommendations():
    """Generate RI purchase recommendations."""
    recommendations = []

    # EC2 - already 90% covered, but some gaps
    if COST_DATA["ec2"]["on_demand"] > 100:
        for instance_type, cost in COST_DATA["ec2"]["on_demand_breakdown"].items():
            if cost > 100 and instance_type != "other":
                potential_savings = estimate_ri_savings(cost)
                recommendations.append({
                    "service": "EC2",
                    "instance_type": instance_type,
                    "current_on_demand_cost": cost,
                    "estimated_ri_cost": cost * 0.70,
                    "potential_savings": potential_savings,
                    "priority": "MEDIUM" if cost > 500 else "LOW",
                    "note": "Consider after rightsizing"
                })

    # RDS - major gap at 98.7% on-demand
    for instance_class, cost in COST_DATA["rds"]["on_demand_breakdown"].items():
        if cost > 200 and instance_class != "other":
            potential_savings = estimate_ri_savings(cost)
            priority = "HIGH" if cost > 1000 else "MEDIUM"
            recommendations.append({
                "service": "RDS",
                "instance_type": instance_class,
                "current_on_demand_cost": cost,
                "estimated_ri_cost": cost * 0.70,
                "potential_savings": potential_savings,
                "priority": priority,
                "note": "Most RDS RIs have EXPIRED - urgent renewal needed"
            })

    # ElastiCache - 93% on-demand
    for node_type, cost in COST_DATA["elasticache"]["on_demand_breakdown"].items():
        if cost > 150:
            potential_savings = estimate_ri_savings(cost)
            recommendations.append({
                "service": "ElastiCache",
                "instance_type": node_type,
                "current_on_demand_cost": cost,
                "estimated_ri_cost": cost * 0.70,
                "potential_savings": potential_savings,
                "priority": "HIGH" if cost > 1000 else "MEDIUM",
                "note": "Low RI coverage - significant savings opportunity"
            })

    # OpenSearch - 78% on-demand
    recommendations.append({
        "service": "OpenSearch",
        "instance_type": "m5/m6g instances",
        "current_on_demand_cost": COST_DATA["opensearch"]["on_demand"],
        "estimated_ri_cost": COST_DATA["opensearch"]["on_demand"] * 0.70,
        "potential_savings": estimate_ri_savings(COST_DATA["opensearch"]["on_demand"]),
        "priority": "HIGH",
        "note": "Most OpenSearch RIs have EXPIRED - renewal needed"
    })

    return sorted(recommendations, key=lambda x: x["potential_savings"], reverse=True)


def generate_csv(filename):
    """Generate CSV report of current RI inventory."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "service", "instance_type", "count", "hourly_rate", "monthly_cost",
            "platform_engine", "offering_type", "expiration", "state", "days_until_expiry"
        ])

        today = datetime.now()

        # EC2 RIs
        for ri in EC2_RIS:
            exp_date = datetime.strptime(ri["expiration"], "%Y-%m-%d")
            days_left = (exp_date - today).days
            monthly = ri["count"] * ri["hourly_rate"] * 730
            writer.writerow([
                "EC2", ri["instance_type"], ri["count"], ri["hourly_rate"],
                f"${monthly:.2f}", ri["platform"], "No Upfront", ri["expiration"],
                "active", days_left
            ])

        # RDS RIs
        for ri in RDS_RIS:
            exp_date = datetime.strptime(ri["expiration"], "%Y-%m-%d")
            days_left = (exp_date - today).days
            monthly = ri["count"] * ri["hourly_rate"] * 730
            writer.writerow([
                "RDS", ri["instance_class"], ri["count"], ri["hourly_rate"],
                f"${monthly:.2f}", ri["engine"], "No Upfront", ri["expiration"],
                ri["state"], days_left
            ])

        # ElastiCache RIs
        for ri in ELASTICACHE_RIS:
            exp_date = datetime.strptime(ri["expiration"], "%Y-%m-%d")
            days_left = (exp_date - today).days
            monthly = ri["count"] * ri["hourly_rate"] * 730
            writer.writerow([
                "ElastiCache", ri["node_type"], ri["count"], ri["hourly_rate"],
                f"${monthly:.2f}", ri["engine"], "No Upfront", ri["expiration"],
                ri["state"], days_left
            ])

        # OpenSearch RIs
        for ri in OPENSEARCH_RIS:
            exp_date = datetime.strptime(ri["expiration"], "%Y-%m-%d")
            days_left = (exp_date - today).days
            monthly = ri["count"] * ri["hourly_rate"] * 730
            writer.writerow([
                "OpenSearch", ri["instance_type"], ri["count"], ri["hourly_rate"],
                f"${monthly:.2f}", "N/A", "No Upfront", ri["expiration"],
                ri["state"], days_left
            ])


def generate_markdown_report(filename):
    """Generate comprehensive markdown report."""
    coverage = calculate_coverage()
    recommendations = generate_recommendations()

    total_potential_savings = sum(r["potential_savings"] for r in recommendations)

    report = f"""# Reserved Instance & Savings Plans Coverage Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Region:** us-east-1
**Analysis Period:** January 2026

---

## Executive Summary

### Critical Finding: SIGNIFICANT RI COVERAGE GAPS

Your organization has **no active Savings Plans** and multiple **expired Reserved Instances** resulting in substantial unnecessary spend.

| Metric | Value |
|--------|-------|
| Total Monthly Spend (Jan 2026) | **$49,644.91** |
| RI Covered | $24,935.72 (50.2%) |
| On-Demand (Uncovered) | **$24,709.19 (49.8%)** |
| Savings Plans | **$0 (0%)** |
| **Potential Monthly Savings** | **${total_potential_savings:,.2f}** |
| **Potential Annual Savings** | **${total_potential_savings * 12:,.2f}** |

### ⚠️ URGENT: Expired RIs Detected

Multiple Reserved Instances have **EXPIRED** and are now running at full On-Demand rates:
- **RDS:** Most RIs expired - now paying 98.7% On-Demand
- **OpenSearch:** 3 of 4 RI reservations expired
- **ElastiCache:** Only 2 nodes covered out of ~50+ deployed

---

## Coverage by Service

| Service | Total Spend | RI Covered | On-Demand | Coverage % | Status |
|---------|-------------|------------|-----------|------------|--------|
| EC2 | ${coverage['ec2']['total']:,.2f} | ${coverage['ec2']['ri_covered']:,.2f} | ${coverage['ec2']['on_demand']:,.2f} | {coverage['ec2']['coverage_pct']:.1f}% | ✅ Good |
| RDS | ${coverage['rds']['total']:,.2f} | ${coverage['rds']['ri_covered']:,.2f} | ${coverage['rds']['on_demand']:,.2f} | {coverage['rds']['coverage_pct']:.1f}% | 🔴 Critical |
| ElastiCache | ${coverage['elasticache']['total']:,.2f} | ${coverage['elasticache']['ri_covered']:,.2f} | ${coverage['elasticache']['on_demand']:,.2f} | {coverage['elasticache']['coverage_pct']:.1f}% | 🔴 Critical |
| OpenSearch | ${coverage['opensearch']['total']:,.2f} | ${coverage['opensearch']['ri_covered']:,.2f} | ${coverage['opensearch']['on_demand']:,.2f} | {coverage['opensearch']['coverage_pct']:.1f}% | 🟡 Poor |

---

## Current EC2 Reserved Instances

**Status: ✅ Well Covered (90.4%)**

| Instance Type | Count | Hourly Rate | Monthly Cost | Platform | Expiration |
|---------------|-------|-------------|--------------|----------|------------|
"""

    for ri in EC2_RIS:
        monthly = ri["count"] * ri["hourly_rate"] * 730
        report += f"| {ri['instance_type']} | {ri['count']} | ${ri['hourly_rate']:.5f} | ${monthly:,.2f} | {ri['platform']} | {ri['expiration']} |\n"

    report += f"""
**Total EC2 RI Commitment:** ${sum(ri['count'] * ri['hourly_rate'] * 730 for ri in EC2_RIS):,.2f}/month

### EC2 On-Demand Gap Analysis

Instances currently running On-Demand (not covered by RI):

| Instance Type | Monthly On-Demand Cost | Action |
|---------------|------------------------|--------|
"""

    for itype, cost in sorted(COST_DATA["ec2"]["on_demand_breakdown"].items(), key=lambda x: x[1], reverse=True):
        if itype != "other":
            action = "Consider RI after rightsizing" if cost > 100 else "Low priority"
            report += f"| {itype} | ${cost:,.2f} | {action} |\n"

    report += f"""
---

## Current RDS Reserved Instances

**Status: 🔴 CRITICAL - Most RIs EXPIRED**

### Active RDS RIs

| Instance Class | Count | Engine | Multi-AZ | Monthly Cost | Expiration |
|---------------|-------|--------|----------|--------------|------------|
"""

    for ri in RDS_RIS:
        monthly = ri["count"] * ri["hourly_rate"] * 730
        report += f"| {ri['instance_class']} | {ri['count']} | {ri['engine']} | {ri['multi_az']} | ${monthly:,.2f} | {ri['expiration']} |\n"

    report += f"""
**Active RDS RI Coverage:** Only 1 db.t4g.medium (Multi-AZ)

### RDS On-Demand Gap Analysis (URGENT)

| Instance Class | Monthly On-Demand Cost | Priority | Note |
|---------------|------------------------|----------|------|
"""

    for iclass, cost in sorted(COST_DATA["rds"]["on_demand_breakdown"].items(), key=lambda x: x[1], reverse=True):
        if iclass != "other":
            priority = "🔴 HIGH" if cost > 1000 else "🟡 MEDIUM"
            report += f"| {iclass} | ${cost:,.2f} | {priority} | RI expired - renew immediately |\n"

    report += f"""
---

## Current ElastiCache Reserved Instances

**Status: 🔴 CRITICAL - Very Low Coverage (6.6%)**

### Active ElastiCache RIs

| Node Type | Count | Engine | Monthly Cost | Expiration |
|-----------|-------|--------|--------------|------------|
"""

    for ri in ELASTICACHE_RIS:
        monthly = ri["count"] * ri["hourly_rate"] * 730
        report += f"| {ri['node_type']} | {ri['count']} | {ri['engine']} | ${monthly:,.2f} | {ri['expiration']} |\n"

    report += f"""
### ElastiCache On-Demand Gap Analysis

| Node Type | Monthly On-Demand Cost | Priority |
|-----------|------------------------|----------|
"""

    for ntype, cost in sorted(COST_DATA["elasticache"]["on_demand_breakdown"].items(), key=lambda x: x[1], reverse=True):
        priority = "🔴 HIGH" if cost > 1000 else "🟡 MEDIUM"
        report += f"| {ntype} | ${cost:,.2f} | {priority} |\n"

    report += f"""
---

## Current OpenSearch Reserved Instances

**Status: 🟡 Poor Coverage - Most RIs EXPIRED (22%)**

### Active OpenSearch RIs

| Instance Type | Count | Monthly Cost | Expiration |
|--------------|-------|--------------|------------|
"""

    for ri in OPENSEARCH_RIS:
        monthly = ri["count"] * ri["hourly_rate"] * 730
        report += f"| {ri['instance_type']} | {ri['count']} | ${monthly:,.2f} | {ri['expiration']} |\n"

    report += f"""
**OpenSearch On-Demand Spend:** ${COST_DATA['opensearch']['on_demand']:,.2f}/month

---

## Savings Plans Status

**Status: ❌ NO ACTIVE SAVINGS PLANS**

You currently have **no Compute Savings Plans or EC2 Instance Savings Plans**.

### Savings Plans vs Reserved Instances

| Feature | Savings Plans | Reserved Instances |
|---------|---------------|-------------------|
| Flexibility | ✅ Any instance family/size | ❌ Fixed instance type |
| Cross-region | ✅ Yes | ❌ No |
| Cross-service | ✅ EC2 + Fargate + Lambda | ❌ EC2 only |
| Discount | ~30% (Compute SP) | ~30-40% |
| Commitment | $ per hour | Instance count |

**Recommendation:** Consider Compute Savings Plans for maximum flexibility, especially given your infrastructure optimization initiatives (Graviton migration, rightsizing).

---

## RI Utilization Analysis

Your **existing** EC2 RIs are being utilized excellently:

| Metric | Value |
|--------|-------|
| Utilization Rate | **{RI_UTILIZATION['utilization_percentage']:.2f}%** |
| Purchased Hours | {RI_UTILIZATION['purchased_hours']:,} |
| Actual Hours Used | {RI_UTILIZATION['total_actual_hours']:,.2f} |
| Unused Hours | {RI_UTILIZATION['unused_hours']:.2f} |
| Net RI Savings | ${RI_UTILIZATION['net_ri_savings']:,.2f} |

This indicates your EC2 RI purchases are correctly sized. The issue is **missing RI coverage for RDS, ElastiCache, and OpenSearch**.

---

## Purchase Recommendations

### 🚨 CRITICAL: Sequence Matters!

**ALWAYS rightsize BEFORE purchasing new RIs/Savings Plans!**

If you purchase RIs based on current instance types and then rightsize, your RIs may not match your new instances, resulting in wasted spend.

### Recommended Sequence

```
1. Complete Graviton migrations (RDS, OpenSearch, MSK)
2. Complete rightsizing analysis
3. Wait 30-60 days to establish new usage patterns
4. Purchase RIs/Savings Plans based on optimized infrastructure
```

### High-Priority RI Recommendations (Post-Optimization)

| Priority | Service | Instance Type | On-Demand Cost | Est. RI Savings | Annual Savings |
|----------|---------|---------------|----------------|-----------------|----------------|
"""

    for i, rec in enumerate(recommendations[:10], 1):
        annual = rec["potential_savings"] * 12
        report += f"| {rec['priority']} | {rec['service']} | {rec['instance_type']} | ${rec['current_on_demand_cost']:,.2f} | ${rec['potential_savings']:,.2f}/mo | ${annual:,.2f}/yr |\n"

    total_annual = total_potential_savings * 12

    report += f"""
**Total Potential Savings:** ${total_potential_savings:,.2f}/month (${total_annual:,.2f}/year)

---

## Savings Plans Recommendation

Given your:
1. **Active optimization initiatives** (Graviton, rightsizing, gp3)
2. **Multi-service infrastructure** (EC2, RDS, ElastiCache, OpenSearch, MSK)
3. **Need for flexibility** during migration

### Recommended Approach

| Phase | Timeline | Action |
|-------|----------|--------|
| Phase 1 | Now | Complete all Graviton migrations |
| Phase 2 | +30 days | Complete rightsizing |
| Phase 3 | +60 days | Purchase Compute Savings Plan (covers ~70% of steady-state EC2) |
| Phase 4 | +60 days | Purchase RDS RIs for stable instances |
| Phase 5 | +90 days | Evaluate ElastiCache/OpenSearch RIs |

### Why Compute Savings Plans?

After rightsizing and Graviton migration, your instance mix will change significantly. A **Compute Savings Plan** provides:

- **Flexibility:** Applies to ANY EC2 instance type, including Graviton
- **Fargate coverage:** If you expand to containers
- **Lambda coverage:** If you use serverless
- **No re-purchase needed** when changing instance types

---

## RI Expiration Calendar

### Upcoming Expirations (Next 12 Months)

| Service | Instance Type | Count | Expiration | Days Left | Action |
|---------|---------------|-------|------------|-----------|--------|
"""

    today = datetime.now()
    all_ris = []

    for ri in EC2_RIS:
        exp_date = datetime.strptime(ri["expiration"], "%Y-%m-%d")
        days_left = (exp_date - today).days
        all_ris.append(("EC2", ri["instance_type"], ri["count"], ri["expiration"], days_left))

    for ri in RDS_RIS:
        exp_date = datetime.strptime(ri["expiration"], "%Y-%m-%d")
        days_left = (exp_date - today).days
        all_ris.append(("RDS", ri["instance_class"], ri["count"], ri["expiration"], days_left))

    for ri in ELASTICACHE_RIS:
        exp_date = datetime.strptime(ri["expiration"], "%Y-%m-%d")
        days_left = (exp_date - today).days
        all_ris.append(("ElastiCache", ri["node_type"], ri["count"], ri["expiration"], days_left))

    for ri in OPENSEARCH_RIS:
        exp_date = datetime.strptime(ri["expiration"], "%Y-%m-%d")
        days_left = (exp_date - today).days
        all_ris.append(("OpenSearch", ri["instance_type"], ri["count"], ri["expiration"], days_left))

    # Sort by expiration date
    all_ris.sort(key=lambda x: x[4])

    for service, itype, count, exp_date, days_left in all_ris:
        action = "Plan renewal (post-optimization)" if days_left > 90 else "⚠️ Expiring soon"
        report += f"| {service} | {itype} | {count} | {exp_date} | {days_left} | {action} |\n"

    report += f"""
---

## Cost Impact Summary

### Current State (January 2026)

| Category | Monthly Cost | % of Total |
|----------|-------------|------------|
| RI-Covered Spend | ${COST_DATA['total']['ri_covered']:,.2f} | 50.2% |
| On-Demand Spend | ${COST_DATA['total']['on_demand']:,.2f} | 49.8% |
| Savings Plans | $0.00 | 0.0% |
| **Total** | **${COST_DATA['total']['all_services']:,.2f}** | 100% |

### Projected State (After RI/SP Optimization)

| Category | Monthly Cost | % of Total | Change |
|----------|-------------|------------|--------|
| RI/SP-Covered Spend | ~${COST_DATA['total']['all_services'] * 0.85:,.2f} | ~85% | +35% |
| On-Demand Spend | ~${COST_DATA['total']['all_services'] * 0.15:,.2f} | ~15% | -35% |
| **Total** | **~${COST_DATA['total']['all_services'] - total_potential_savings:,.2f}** | 100% | -${total_potential_savings:,.2f} |

### Combined Savings Opportunity

| Optimization | Monthly Savings | Annual Savings |
|--------------|-----------------|----------------|
| Graviton Migration (EC2) | Already covered by existing RIs | - |
| Graviton Migration (RDS) | $78.57 | $942.84 |
| Graviton Migration (OpenSearch) | $146.89 | $1,762.68 |
| Graviton Migration (MSK) | $219.40 | $2,632.79 |
| **RI/SP Coverage** | **${total_potential_savings:,.2f}** | **${total_annual:,.2f}** |
| **Total** | **${total_potential_savings + 444.86:,.2f}** | **${total_annual + 5338.31:,.2f}** |

---

## Immediate Action Items

### 🔴 Week 1: Assessment

- [ ] Review this analysis with Finance team
- [ ] Confirm rightsizing and Graviton migration timelines
- [ ] Identify instances that will NOT change (stable candidates for immediate RI)

### 🟡 Week 2-4: Optimization Execution

- [ ] Complete Graviton migrations (RDS → r6g, OpenSearch → m6g, MSK → m7g)
- [ ] Complete EC2 rightsizing
- [ ] Wait for usage patterns to stabilize

### 🟢 Week 5-8: RI/SP Purchases

- [ ] Purchase Compute Savings Plan (~$15/hour commitment)
- [ ] Purchase RDS RIs for stable instances
- [ ] Evaluate ElastiCache Reserved Nodes
- [ ] Evaluate OpenSearch Reserved Instances

---

## Files Generated

- CSV Report: `/app/ri_sp_coverage_inventory.csv`
- Analysis Script: `/app/ri_sp_coverage_analysis.py`
- This Report: `/app/ri_sp_coverage_report.md`
"""

    with open(filename, 'w') as f:
        f.write(report)


def main():
    print("RI/SP Coverage Analysis")
    print("=" * 50)

    # Generate reports
    generate_csv("/app/ri_sp_coverage_inventory.csv")
    generate_markdown_report("/app/ri_sp_coverage_report.md")

    # Summary
    coverage = calculate_coverage()
    recommendations = generate_recommendations()
    total_potential_savings = sum(r["potential_savings"] for r in recommendations)

    print(f"\nCoverage Summary:")
    for service, data in coverage.items():
        print(f"  {service}: {data['coverage_pct']:.1f}% covered, {data['gap_pct']:.1f}% on-demand")

    print(f"\nTotal potential RI/SP savings: ${total_potential_savings:,.2f}/month")
    print(f"Annual potential savings: ${total_potential_savings * 12:,.2f}")

    print("\nReports generated:")
    print("  - /app/ri_sp_coverage_inventory.csv")
    print("  - /app/ri_sp_coverage_report.md")


if __name__ == "__main__":
    main()
