# RDS Graviton Migration Opportunity Analysis

**Date:** February 10, 2026
**Region:** us-east-1
**Total RDS Instances:** 75
**EDP Discount Applied:** 31% (0.69 multiplier)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Instances Analyzed** | 75 |
| **Already on Graviton** | 64 (85%) |
| **Eligible for Graviton Migration** | 11 (15%) |
| **Total Monthly Savings (Graviton)** | **$131.23** |
| **Total Monthly Savings (gp2→gp3)** | **$2.17** |
| **Grand Total Monthly Savings** | **$133.40** |
| **Annual Savings Potential** | **$1,600.80** |

---

## Question 1: Which RDS Instances CAN/CANNOT Be Converted to Graviton?

### Already on Graviton (64 instances) - NO ACTION NEEDED

| Instance Class | Count | Instances |
|----------------|-------|-----------|
| db.t4g.micro | 36 | aws-luckyus-fichargecontrol-rw, aws-luckyus-fitax-rw, aws-luckyus-iadmin-rw, aws-luckyus-ibillingcentersrv-rw, aws-luckyus-ibizconfigcenter-rw, aws-luckyus-iehr-rw, aws-luckyus-ifiaccounting-rw, aws-luckyus-igers-rw, aws-luckyus-ijumpserver-jumpserver-rw, aws-luckyus-ilsopdevopsdata-rw, aws-luckyus-iluckyams-rw, aws-luckyus-iluckyauthapi-rw, aws-luckyus-iluckydorisops-rw, aws-luckyus-iluckymedia-rw, aws-luckyus-iopenadmin-rw, aws-luckyus-iopenlinker-rw, aws-luckyus-iopenservice-rw, aws-luckyus-iopocp-rw, aws-luckyus-iopshopexpand-rw, aws-luckyus-ipermission-rw, aws-luckyus-ireplenishment-rw, aws-luckyus-iriskcontrolservice-rw, aws-luckyus-isalescdp-rw, aws-luckyus-isalesmembermarketing-rw, aws-luckyus-iunifiedreconcile-rw, aws-luckyus-mfranchise-rw, aws-luckyus-opempefficiency-rw, aws-luckyus-oplog-rw, aws-luckyus-opproduction-rw, aws-luckyus-opqualitycontrol-rw, aws-luckyus-opshopsale-rw, aws-luckyus-pubdm-rw, aws-luckyus-scm-asset-rw, aws-luckyus-scm-openapi-rw, aws-luckyus-scm-ordering-rw, aws-luckyus-scm-plan-rw, aws-luckyus-scm-purchase-rw, aws-luckyus-scmsrm-rw, aws-luckyus-scm-wds-rw, aws-luckyus-scm-wmssimulate-rw, aws-luckyus-dbatest-rw |
| db.t4g.medium | 16 | aws-luckyus-cdpactivity-rw, aws-luckyus-devops-rw, aws-luckyus-framework01-rw, aws-luckyus-framework02-rw, aws-luckyus-icyberdata-rw, aws-luckyus-iotplatform-rw, aws-luckyus-isalesdatamarketing-rw, aws-luckyus-isalesprivatedomain-rw, aws-luckyus-iworkflowmidlayer-rw, aws-luckyus-opshop-rw, aws-luckyus-salescrm-rw, aws-luckyus-salesorder-rw, aws-luckyus-salespayment-rw, aws-luckyus-scmcommodity-rw, aws-luckyus-scm-shopstock-rw, aws-luckyus-upush-rw, docdb-gia2 |
| db.t4g.large | 2 | aws-luckyus-ldas01-rw, aws-luckyus-ldas-rw |
| db.t4g.xlarge | 1 | aws-luckyus-salesmarketing-rw |
| db.r6g.large | 2 | docdb-gia, docdb-gia3 |

### Eligible for Graviton Migration (11 instances)

| Instance ID | Engine | Engine Version | Current Class | Target Class | Multi-AZ | Eligible | Notes |
|-------------|--------|----------------|---------------|--------------|----------|----------|-------|
| aws-luckyus-difynew-rw | PostgreSQL | 16.10 | db.r5.xlarge | db.r6g.xlarge | Yes | **YES** | PG 16.x fully supports Graviton |
| aws-luckyus-dify-rw | PostgreSQL | 16.8 | db.r5.xlarge | db.r6g.xlarge | Yes | **YES** | PG 16.x fully supports Graviton |
| aws-luckyus-pgilkmap-rw | PostgreSQL | 17.4 | db.m5.large | db.m6g.large | Yes | **YES** | PG 17.x fully supports Graviton |
| aws-luckyus-iluckyhealth-rw | MySQL | 8.0.40 | db.t3.small | db.t4g.small | Yes | **YES** | MySQL 8.0.40 > 8.0.17 |
| recovery-dbatest | MySQL | 8.0.40 | db.t3.small | db.t4g.small | Yes | **YES** | MySQL 8.0.40 > 8.0.17 |
| docdb-devops | DocumentDB | 5.0.0 | db.t3.medium | db.t4g.medium | No | **YES** | DocDB 5.0 supports Graviton |
| docdb-devops2 | DocumentDB | 5.0.0 | db.t3.medium | db.t4g.medium | No | **YES** | DocDB 5.0 supports Graviton |
| docdb-devops3 | DocumentDB | 5.0.0 | db.t3.medium | db.t4g.medium | No | **YES** | DocDB 5.0 supports Graviton |
| docdb-iot | DocumentDB | 5.0.0 | db.t3.medium | db.t4g.medium | No | **YES** | DocDB 5.0 supports Graviton |
| docdb-iot2 | DocumentDB | 5.0.0 | db.t3.medium | db.t4g.medium | No | **YES** | DocDB 5.0 supports Graviton |
| docdb-iot3 | DocumentDB | 5.0.0 | db.t3.medium | db.t4g.medium | No | **YES** | DocDB 5.0 supports Graviton |

### Instances That CANNOT Be Converted (0 instances)

All non-Graviton instances in this account are eligible for migration. No instances were found with:
- Unsupported engine versions
- x86-only dependencies
- Instance class limitations

---

## Question 2: Monthly Cost Savings Per Convertible Instance

### Pricing Methodology

- **Base Pricing:** AWS On-Demand Pricing (US East - N. Virginia)
- **EDP Discount:** 31% applied (multiplier: 0.69)
- **Monthly Hours:** 730 hours
- **Multi-AZ:** Pricing already included in Multi-AZ rates (no additional ×2 needed)

### Detailed Cost Savings Table

| Instance ID | Engine | Current Class | Target Class | Multi-AZ | Current $/hr | Target $/hr | Current $/mo (EDP) | Target $/mo (EDP) | Savings $/mo | Savings % |
|-------------|--------|---------------|--------------|----------|--------------|-------------|-------------------|-------------------|--------------|-----------|
| aws-luckyus-difynew-rw | PostgreSQL | db.r5.xlarge | db.r6g.xlarge | Yes | $1.000 | $0.899 | $503.70 | $452.67 | **$51.03** | 10.1% |
| aws-luckyus-dify-rw | PostgreSQL | db.r5.xlarge | db.r6g.xlarge | Yes | $1.000 | $0.899 | $503.70 | $452.67 | **$51.03** | 10.1% |
| aws-luckyus-pgilkmap-rw | PostgreSQL | db.m5.large | db.m6g.large | Yes | $0.356 | $0.318 | $179.27 | $160.13 | **$19.14** | 10.7% |
| aws-luckyus-iluckyhealth-rw | MySQL | db.t3.small | db.t4g.small | Yes | $0.068 | $0.065 | $34.25 | $32.74 | **$1.51** | 4.4% |
| recovery-dbatest | MySQL | db.t3.small | db.t4g.small | Yes | $0.068 | $0.065 | $34.25 | $32.74 | **$1.51** | 4.4% |
| docdb-devops | DocumentDB | db.t3.medium | db.t4g.medium | No | $0.078 | $0.0757 | $39.29 | $38.11 | **$1.18** | 3.0% |
| docdb-devops2 | DocumentDB | db.t3.medium | db.t4g.medium | No | $0.078 | $0.0757 | $39.29 | $38.11 | **$1.18** | 3.0% |
| docdb-devops3 | DocumentDB | db.t3.medium | db.t4g.medium | No | $0.078 | $0.0757 | $39.29 | $38.11 | **$1.18** | 3.0% |
| docdb-iot | DocumentDB | db.t3.medium | db.t4g.medium | No | $0.078 | $0.0757 | $39.29 | $38.11 | **$1.18** | 3.0% |
| docdb-iot2 | DocumentDB | db.t3.medium | db.t4g.medium | No | $0.078 | $0.0757 | $39.29 | $38.11 | **$1.18** | 3.0% |
| docdb-iot3 | DocumentDB | db.t3.medium | db.t4g.medium | No | $0.078 | $0.0757 | $39.29 | $38.11 | **$1.18** | 3.0% |
| **TOTAL** | | | | | | | **$1,490.91** | **$1,359.61** | **$131.30** | **8.8%** |

### Cost Calculation Breakdown

#### PostgreSQL db.r5.xlarge → db.r6g.xlarge (Multi-AZ)
```
Current: $1.00/hr × 730 hrs × 0.69 EDP = $503.70/month
Target:  $0.899/hr × 730 hrs × 0.69 EDP = $452.67/month
Savings: $51.03/month per instance (10.1% reduction)
```

#### PostgreSQL db.m5.large → db.m6g.large (Multi-AZ)
```
Current: $0.356/hr × 730 hrs × 0.69 EDP = $179.27/month
Target:  $0.318/hr × 730 hrs × 0.69 EDP = $160.13/month
Savings: $19.14/month per instance (10.7% reduction)
```

#### MySQL db.t3.small → db.t4g.small (Multi-AZ)
```
Current: $0.068/hr × 730 hrs × 0.69 EDP = $34.25/month
Target:  $0.065/hr × 730 hrs × 0.69 EDP = $32.74/month
Savings: $1.51/month per instance (4.4% reduction)
```

#### DocumentDB db.t3.medium → db.t4g.medium (Single-AZ)
```
Current: $0.078/hr × 730 hrs × 0.69 EDP = $39.29/month
Target:  $0.07566/hr × 730 hrs × 0.69 EDP = $38.11/month
Savings: $1.18/month per instance (3.0% reduction)
```

---

## Bonus: gp2 → gp3 Storage Optimization

Three instances still use gp2 storage, which can be converted to gp3 with no downtime (modify operation):

| Instance ID | Storage (GB) | Current Type | Target Type | Current $/mo (EDP) | Target $/mo (EDP) | Savings $/mo |
|-------------|--------------|--------------|-------------|-------------------|-------------------|--------------|
| aws-luckyus-devops-rw | 20 GB | gp2 | gp3 | $1.59 | $1.10 | **$0.48** |
| aws-luckyus-ldas-rw | 30 GB | gp2 | gp3 | $2.38 | $1.66 | **$0.72** |
| recovery-dbatest | 40 GB | gp2 | gp3 | $3.17 | $2.21 | **$0.97** |
| **TOTAL** | 90 GB | | | **$7.14** | **$4.97** | **$2.17** |

### gp2 → gp3 Calculation
```
gp2 rate: $0.115/GB-month × 0.69 EDP = $0.07935/GB-month
gp3 rate: $0.08/GB-month × 0.69 EDP = $0.0552/GB-month
Savings: $0.02415/GB-month
```

---

## Summary by Category

| Category | Instance Count | Total Current $/mo | Total Target $/mo | Total Savings $/mo |
|----------|----------------|-------------------|-------------------|-------------------|
| PostgreSQL (r5→r6g) | 2 | $1,007.40 | $905.34 | $102.06 |
| PostgreSQL (m5→m6g) | 1 | $179.27 | $160.13 | $19.14 |
| MySQL (t3→t4g) | 2 | $68.50 | $65.48 | $3.02 |
| DocumentDB (t3→t4g) | 6 | $235.74 | $228.66 | $7.08 |
| **Graviton TOTAL** | **11** | **$1,490.91** | **$1,359.61** | **$131.30** |
| gp2→gp3 Storage | 3 | $7.14 | $4.97 | $2.17 |
| **GRAND TOTAL** | | | | **$133.47** |

---

## Recommended Migration Priority

### Priority 1: Highest Impact (Migration Order)
| Rank | Instance | Savings/mo | Effort | Risk |
|------|----------|------------|--------|------|
| 1 | aws-luckyus-difynew-rw | $51.03 | Medium | Low |
| 2 | aws-luckyus-dify-rw | $51.03 | Medium | Low |
| 3 | aws-luckyus-pgilkmap-rw | $19.14 | Medium | Low |

### Priority 2: Lower Impact but Easy Wins
| Rank | Instance | Savings/mo | Effort | Risk |
|------|----------|------------|--------|------|
| 4-9 | docdb-devops/iot (×6) | $7.08 total | Low | Low |
| 10-11 | MySQL t3.small (×2) | $3.02 total | Low | Low |

### Priority 3: Storage Optimization (Zero Downtime)
| Rank | Instance | Savings/mo | Effort | Risk |
|------|----------|------------|--------|------|
| 12-14 | gp2→gp3 (×3) | $2.17 total | Very Low | Very Low |

---

## Migration Notes

### Pre-Migration Checklist
- [ ] Verify application compatibility with Graviton (ARM64) - typically no issues for standard database workloads
- [ ] Schedule maintenance window (Multi-AZ instances: brief failover; Single-AZ: downtime required)
- [ ] Ensure recent backup exists
- [ ] Test in staging environment if available

### Migration Process
1. **Modify DB Instance Class** via AWS Console or CLI:
   ```bash
   aws rds modify-db-instance \
     --db-instance-identifier <instance-id> \
     --db-instance-class <target-class> \
     --apply-immediately
   ```

2. **gp2→gp3 Storage Migration** (online, no downtime):
   ```bash
   aws rds modify-db-instance \
     --db-instance-identifier <instance-id> \
     --storage-type gp3 \
     --apply-immediately
   ```

---

## Conclusion

**85% of your RDS fleet (64/75 instances) is already on Graviton** - excellent work on prior optimization efforts.

The remaining 11 convertible instances represent **$131.30/month ($1,575.60/year)** in savings from Graviton migration, plus **$2.17/month ($26.04/year)** from gp2→gp3 storage conversion.

**Total Annual Savings Opportunity: $1,601.64**

The two Dify PostgreSQL instances (db.r5.xlarge) represent 78% of the total Graviton savings opportunity. These should be prioritized for migration.

---

*Report generated: February 10, 2026*
*AWS Region: us-east-1*
*Pricing source: AWS Price List API with 31% EDP discount*
