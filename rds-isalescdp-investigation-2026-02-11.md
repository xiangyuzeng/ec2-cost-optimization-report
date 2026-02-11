# RDS Instance Investigation: aws-luckyus-isalescdp-rw

**Date**: 2026-02-11
**AWS Account**: 257394478466
**Region**: us-east-1

## Summary

The instance `aws-luckyus-isalescdp-rw` is a **standalone RDS MySQL instance**, not an Aurora cluster.

## Instance Details

```json
{
    "InstanceID": "aws-luckyus-isalescdp-rw",
    "Engine": "mysql",
    "EngineVersion": "8.0.40",
    "Class": "db.t4g.micro",
    "Status": "available",
    "Endpoint": "aws-luckyus-isalescdp-rw.cxwu08m2qypw.us-east-1.rds.amazonaws.com",
    "Port": 3306,
    "AZ": "us-east-1a",
    "MultiAZ": true,
    "StorageType": "gp3",
    "AllocatedStorage": 40,
    "MaxAllocatedStorage": 1000,
    "IOPS": 3000,
    "StorageEncrypted": true,
    "VpcId": "vpc-0dce7ca7770422d33",
    "PubliclyAccessible": false,
    "BackupRetentionPeriod": 7,
    "DeletionProtection": true
}
```

## Configuration Summary

| Property | Value |
|----------|-------|
| **Engine** | MySQL 8.0.40 |
| **Instance Class** | db.t4g.micro |
| **Status** | available |
| **Multi-AZ** | Yes (High Availability) |
| **Storage Type** | gp3 |
| **Allocated Storage** | 40 GB |
| **Max Allocated Storage** | 1000 GB (auto-scaling enabled) |
| **IOPS** | 3000 |
| **Encrypted** | Yes |
| **Publicly Accessible** | No |
| **Backup Retention** | 7 days |
| **Deletion Protection** | Enabled |

## Connectivity

- **Endpoint**: `aws-luckyus-isalescdp-rw.cxwu08m2qypw.us-east-1.rds.amazonaws.com`
- **Port**: 3306
- **VPC**: vpc-0dce7ca7770422d33
- **Availability Zone**: us-east-1a (with Multi-AZ standby)

## Notes

1. **Not a Cluster**: This is a standalone RDS instance, not an Aurora cluster. Use `describe-db-instances` instead of `describe-db-clusters`.

2. **Multi-AZ Enabled**: The instance has a synchronous standby replica in another AZ for automatic failover.

3. **Storage Auto-scaling**: Configured to automatically scale from 40 GB up to 1000 GB.

4. **Instance Size**: db.t4g.micro is a burstable instance type - suitable for development/low-traffic workloads. Monitor CPU credits if usage increases.
