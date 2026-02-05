#!/usr/bin/env python3
"""
OpenSearch Domain Optimization Analysis Script
Analyzes x86 instances and gp2 storage for migration opportunities
"""

import csv
from datetime import datetime

# OpenSearch domain data from AWS
domains = [
    {
        "DomainName": "luckylfe-log",
        "EngineVersion": "Elasticsearch_7.10",
        "DataInstanceType": "m5.large.search",
        "DataInstanceCount": 4,
        "MasterInstanceType": "t3.medium.search",
        "MasterInstanceCount": 3,
        "ZoneAwarenessEnabled": True,
        "StorageType": "gp2",
        "StorageSize": 80,  # per node
        "WarmEnabled": False,
        "ColdStorageEnabled": False,
        "AvgCPU": 8.2,
        "MaxCPU": 43,
        "AvgJVMPressure": 45.3,
        "MaxJVMPressure": 75.5,
        "FreeStorageGB": 14.1,  # min per node
        "TotalStorageGB": 80 * 4,  # total allocated
    },
    {
        "DomainName": "luckycommon",
        "EngineVersion": "Elasticsearch_6.8",
        "DataInstanceType": "m5.large.search",
        "DataInstanceCount": 4,
        "MasterInstanceType": "t3.small.search",
        "MasterInstanceCount": 3,
        "ZoneAwarenessEnabled": True,
        "StorageType": "gp3",
        "StorageSize": 100,  # per node
        "WarmEnabled": False,
        "ColdStorageEnabled": False,
        "AvgCPU": 12.4,
        "MaxCPU": 77,
        "AvgJVMPressure": 44.3,
        "MaxJVMPressure": 75.7,
        "FreeStorageGB": 36.3,  # min per node
        "TotalStorageGB": 100 * 4,
    },
    {
        "DomainName": "luckyur-log",
        "EngineVersion": "Elasticsearch_7.10",
        "DataInstanceType": "m5.xlarge.search",
        "DataInstanceCount": 4,
        "MasterInstanceType": "t3.medium.search",
        "MasterInstanceCount": 3,
        "ZoneAwarenessEnabled": True,
        "StorageType": "gp2",
        "StorageSize": 350,  # per node
        "WarmEnabled": False,
        "ColdStorageEnabled": False,
        "AvgCPU": 16.5,
        "MaxCPU": 90,
        "AvgJVMPressure": 59.1,
        "MaxJVMPressure": 76.3,
        "FreeStorageGB": 39.7,  # min per node
        "TotalStorageGB": 350 * 4,
    },
    {
        "DomainName": "luckyus-opensearch-dify",
        "EngineVersion": "OpenSearch_2.15",
        "DataInstanceType": "r6g.large.search",
        "DataInstanceCount": 2,
        "MasterInstanceType": "m7g.large.search",
        "MasterInstanceCount": 3,
        "ZoneAwarenessEnabled": True,
        "StorageType": "gp3",
        "StorageSize": 30,  # per node
        "WarmEnabled": False,
        "ColdStorageEnabled": False,
        "AvgCPU": 8.3,
        "MaxCPU": 38,
        "AvgJVMPressure": 35.3,
        "MaxJVMPressure": 65,
        "FreeStorageGB": 23.5,  # min per node
        "TotalStorageGB": 30 * 2,
    },
]

# x86 to Graviton mapping for OpenSearch
x86_to_graviton = {
    # t3 series -> t3 (no Graviton equivalent for t3 search)
    "t3.small.search": "t3.small.search",  # no change, t3 has no Graviton equivalent
    "t3.medium.search": "t3.medium.search",  # no change
    # m5 series -> m6g series
    "m5.large.search": "m6g.large.search",
    "m5.xlarge.search": "m6g.xlarge.search",
    "m5.2xlarge.search": "m6g.2xlarge.search",
    "m5.4xlarge.search": "m6g.4xlarge.search",
    # m6i series -> m6g series
    "m6i.large.search": "m6g.large.search",
    "m6i.xlarge.search": "m6g.xlarge.search",
    # r5 series -> r6g series
    "r5.large.search": "r6g.large.search",
    "r5.xlarge.search": "r6g.xlarge.search",
    "r5.2xlarge.search": "r6g.2xlarge.search",
    # r6i series -> r6g series
    "r6i.large.search": "r6g.large.search",
    "r6i.xlarge.search": "r6g.xlarge.search",
}

# AWS On-Demand pricing for OpenSearch us-east-1 (hourly rates)
x86_hourly_pricing = {
    "t3.small.search": 0.036,
    "t3.medium.search": 0.073,
    "m5.large.search": 0.142,
    "m5.xlarge.search": 0.284,
    "m5.2xlarge.search": 0.568,
    "m5.4xlarge.search": 1.136,
    "m6i.large.search": 0.149,
    "m6i.xlarge.search": 0.298,
    "r5.large.search": 0.186,
    "r5.xlarge.search": 0.372,
    "r5.2xlarge.search": 0.744,
    "r6i.large.search": 0.195,
    "r6i.xlarge.search": 0.390,
}

graviton_hourly_pricing = {
    "t3.small.search": 0.036,  # no Graviton, same price
    "t3.medium.search": 0.073,  # no Graviton, same price
    "m6g.large.search": 0.128,
    "m6g.xlarge.search": 0.255,
    "m6g.2xlarge.search": 0.511,
    "m6g.4xlarge.search": 1.022,
    "m7g.large.search": 0.134,
    "m7g.xlarge.search": 0.268,
    "r6g.large.search": 0.167,
    "r6g.xlarge.search": 0.335,
    "r6g.2xlarge.search": 0.669,
    "r7g.large.search": 0.176,
    "r7g.xlarge.search": 0.352,
}

# Storage pricing per GB/month
gp2_price_per_gb = 0.135  # $0.135/GB-month for gp2
gp3_price_per_gb = 0.108  # $0.108/GB-month for gp3 (baseline)

# EDP discount
EDP_DISCOUNT = 0.31

def is_x86_instance(instance_type):
    """Check if instance is x86 (not Graviton)"""
    graviton_markers = ['6g.', '7g.']
    return not any(marker in instance_type for marker in graviton_markers)

def get_graviton_equivalent(instance_type):
    """Get Graviton equivalent for x86 instance"""
    return x86_to_graviton.get(instance_type, instance_type)

def calculate_instance_monthly_cost(instance_type, count, is_graviton=False):
    """Calculate monthly cost for instances"""
    pricing = graviton_hourly_pricing if is_graviton else x86_hourly_pricing
    hourly_rate = pricing.get(instance_type, 0)
    monthly_cost = hourly_rate * 730 * count
    return monthly_cost * (1 - EDP_DISCOUNT)

def calculate_storage_monthly_cost(storage_type, size_per_node, node_count):
    """Calculate monthly storage cost"""
    total_gb = size_per_node * node_count
    price = gp3_price_per_gb if storage_type == "gp3" else gp2_price_per_gb
    monthly_cost = total_gb * price
    return monthly_cost * (1 - EDP_DISCOUNT)

def analyze_domain(domain):
    """Analyze a single domain for optimization opportunities"""
    result = {
        "domain_name": domain["DomainName"],
        "engine_version": domain["EngineVersion"],
        "current_data_instance": domain["DataInstanceType"],
        "data_instance_count": domain["DataInstanceCount"],
        "current_master_instance": domain["MasterInstanceType"],
        "master_instance_count": domain["MasterInstanceCount"],
        "current_storage_type": domain["StorageType"],
        "storage_size_per_node": domain["StorageSize"],
        "total_storage_gb": domain["TotalStorageGB"],
        "warm_enabled": domain["WarmEnabled"],
        "cold_enabled": domain["ColdStorageEnabled"],
        "avg_cpu": domain["AvgCPU"],
        "max_cpu": domain["MaxCPU"],
        "avg_jvm": domain["AvgJVMPressure"],
        "max_jvm": domain["MaxJVMPressure"],
    }

    # Current costs
    current_data_cost = calculate_instance_monthly_cost(
        domain["DataInstanceType"], domain["DataInstanceCount"], is_graviton=False
    )
    current_master_cost = calculate_instance_monthly_cost(
        domain["MasterInstanceType"], domain["MasterInstanceCount"], is_graviton=False
    )
    current_storage_cost = calculate_storage_monthly_cost(
        domain["StorageType"], domain["StorageSize"], domain["DataInstanceCount"]
    )

    # Check if already on Graviton
    data_is_x86 = is_x86_instance(domain["DataInstanceType"])
    master_is_x86 = is_x86_instance(domain["MasterInstanceType"])

    # Graviton recommendations
    if data_is_x86:
        graviton_data = get_graviton_equivalent(domain["DataInstanceType"])
        projected_data_cost = calculate_instance_monthly_cost(
            graviton_data, domain["DataInstanceCount"], is_graviton=True
        )
    else:
        graviton_data = domain["DataInstanceType"]
        projected_data_cost = current_data_cost

    if master_is_x86:
        graviton_master = get_graviton_equivalent(domain["MasterInstanceType"])
        # t3 has no Graviton equivalent
        if graviton_master == domain["MasterInstanceType"]:
            projected_master_cost = current_master_cost
        else:
            projected_master_cost = calculate_instance_monthly_cost(
                graviton_master, domain["MasterInstanceCount"], is_graviton=True
            )
    else:
        graviton_master = domain["MasterInstanceType"]
        projected_master_cost = current_master_cost

    # Storage recommendation
    if domain["StorageType"] == "gp2":
        projected_storage_cost = calculate_storage_monthly_cost(
            "gp3", domain["StorageSize"], domain["DataInstanceCount"]
        )
        storage_recommendation = "gp3"
    else:
        projected_storage_cost = current_storage_cost
        storage_recommendation = domain["StorageType"]

    result["graviton_data_instance"] = graviton_data
    result["graviton_master_instance"] = graviton_master
    result["recommended_storage"] = storage_recommendation

    result["current_data_cost"] = round(current_data_cost, 2)
    result["current_master_cost"] = round(current_master_cost, 2)
    result["current_storage_cost"] = round(current_storage_cost, 2)
    result["current_total_cost"] = round(current_data_cost + current_master_cost + current_storage_cost, 2)

    result["projected_data_cost"] = round(projected_data_cost, 2)
    result["projected_master_cost"] = round(projected_master_cost, 2)
    result["projected_storage_cost"] = round(projected_storage_cost, 2)
    result["projected_total_cost"] = round(projected_data_cost + projected_master_cost + projected_storage_cost, 2)

    result["data_savings"] = round(current_data_cost - projected_data_cost, 2)
    result["master_savings"] = round(current_master_cost - projected_master_cost, 2)
    result["storage_savings"] = round(current_storage_cost - projected_storage_cost, 2)
    result["total_savings"] = round(result["data_savings"] + result["master_savings"] + result["storage_savings"], 2)

    # Determine optimization type
    optimizations = []
    if data_is_x86 and graviton_data != domain["DataInstanceType"]:
        optimizations.append("Graviton data nodes")
    if master_is_x86 and graviton_master != domain["MasterInstanceType"]:
        optimizations.append("Graviton master nodes")
    if domain["StorageType"] == "gp2":
        optimizations.append("gp2→gp3 storage")
    if not optimizations:
        optimizations.append("Already optimized")

    result["optimizations"] = ", ".join(optimizations)
    result["data_is_x86"] = data_is_x86
    result["master_is_x86"] = master_is_x86

    return result

def main():
    results = [analyze_domain(d) for d in domains]

    # Write CSV
    csv_file = "/app/opensearch_optimization_candidates.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "domain_name", "engine_version",
            "current_data_instance", "graviton_data_instance", "data_node_count",
            "current_master_instance", "graviton_master_instance", "master_node_count",
            "current_storage", "recommended_storage", "storage_gb_per_node",
            "current_monthly_cost", "projected_monthly_cost", "monthly_savings",
            "optimizations"
        ])

        for r in sorted(results, key=lambda x: -x["total_savings"]):
            writer.writerow([
                r["domain_name"],
                r["engine_version"],
                r["current_data_instance"],
                r["graviton_data_instance"],
                r["data_instance_count"],
                r["current_master_instance"],
                r["graviton_master_instance"],
                r["master_instance_count"],
                r["current_storage_type"],
                r["recommended_storage"],
                r["storage_size_per_node"],
                f"${r['current_total_cost']:.2f}",
                f"${r['projected_total_cost']:.2f}",
                f"${r['total_savings']:.2f}",
                r["optimizations"]
            ])

    # Print summary report
    print("=" * 100)
    print("OPENSEARCH DOMAIN OPTIMIZATION ANALYSIS REPORT")
    print("=" * 100)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"EDP Discount Applied: {EDP_DISCOUNT*100}%")
    print()

    print("DOMAIN INVENTORY")
    print("-" * 100)
    print(f"{'Domain':<30} {'Engine':<20} {'Data Nodes':<25} {'Master Nodes':<20} {'Storage'}")
    print("-" * 100)
    for d in domains:
        print(f"{d['DomainName']:<30} {d['EngineVersion']:<20} "
              f"{d['DataInstanceCount']}x {d['DataInstanceType']:<17} "
              f"{d['MasterInstanceCount']}x {d['MasterInstanceType']:<13} "
              f"{d['StorageType']} {d['StorageSize']}GB")
    print()

    # Optimization candidates
    candidates = [r for r in results if r["total_savings"] > 0]
    already_optimized = [r for r in results if r["total_savings"] == 0]

    total_current = sum(r["current_total_cost"] for r in results)
    total_projected = sum(r["projected_total_cost"] for r in results)
    total_savings = sum(r["total_savings"] for r in results)

    print("SUMMARY STATISTICS")
    print("-" * 50)
    print(f"Total Domains: {len(domains)}")
    print(f"Domains with Optimization Opportunities: {len(candidates)}")
    print(f"Already Optimized Domains: {len(already_optimized)}")
    print()

    print("COST IMPACT")
    print("-" * 50)
    print(f"Current Monthly Cost:    ${total_current:.2f}")
    print(f"Projected Monthly Cost:  ${total_projected:.2f}")
    print(f"Monthly Savings:         ${total_savings:.2f}")
    print(f"Annual Savings:          ${total_savings * 12:.2f}")
    print()

    print("SAVINGS BREAKDOWN BY CATEGORY")
    print("-" * 50)
    data_savings = sum(r["data_savings"] for r in results)
    master_savings = sum(r["master_savings"] for r in results)
    storage_savings = sum(r["storage_savings"] for r in results)
    print(f"Graviton Data Nodes:     ${data_savings:.2f}/month")
    print(f"Graviton Master Nodes:   ${master_savings:.2f}/month (t3 has no Graviton equivalent)")
    print(f"gp2 → gp3 Storage:       ${storage_savings:.2f}/month")
    print()

    print("OPTIMIZATION CANDIDATES (sorted by savings)")
    print("-" * 100)
    print(f"{'Domain':<30} {'Current Cost':<15} {'Projected':<15} {'Savings/mo':<15} {'Optimizations'}")
    print("-" * 100)

    for r in sorted(results, key=lambda x: -x["total_savings"]):
        print(f"{r['domain_name']:<30} ${r['current_total_cost']:<14.2f} "
              f"${r['projected_total_cost']:<14.2f} ${r['total_savings']:<14.2f} {r['optimizations']}")
    print()

    print("CLOUDWATCH METRICS (7-day average)")
    print("-" * 100)
    print(f"{'Domain':<30} {'Avg CPU %':<12} {'Max CPU %':<12} {'Avg JVM %':<12} {'Max JVM %'}")
    print("-" * 100)
    for r in results:
        print(f"{r['domain_name']:<30} {r['avg_cpu']:<12.1f} {r['max_cpu']:<12.0f} "
              f"{r['avg_jvm']:<12.1f} {r['max_jvm']:<12.1f}")
    print()

    if already_optimized:
        print("ALREADY OPTIMIZED DOMAINS")
        print("-" * 50)
        for r in already_optimized:
            print(f"  {r['domain_name']}: {r['graviton_data_instance']} (data), "
                  f"{r['graviton_master_instance']} (master), {r['recommended_storage']} storage")
    print()

    print("MIGRATION RECOMMENDATIONS")
    print("-" * 100)
    for r in sorted(results, key=lambda x: -x["total_savings"]):
        if r["total_savings"] > 0:
            print(f"\n{r['domain_name']} (${r['total_savings']:.2f}/month savings):")
            if r["data_is_x86"] and r["graviton_data_instance"] != r["current_data_instance"]:
                print(f"  1. Migrate data nodes: {r['current_data_instance']} → {r['graviton_data_instance']}")
                print(f"     Savings: ${r['data_savings']:.2f}/month")
            if r["current_storage_type"] == "gp2":
                print(f"  2. Upgrade storage: {r['current_storage_type']} → {r['recommended_storage']}")
                print(f"     Savings: ${r['storage_savings']:.2f}/month")

    print()
    print(f"\nCSV file written to: {csv_file}")

    return results

if __name__ == "__main__":
    main()
