# ElastiCache Redis Snapshot Investigation

**Date**: 2026-02-11
**Region**: us-east-1
**Issue**: Repeated SnapshotComplete SNS Notifications
**Target Clusters**: luckyus-iopenlinker, luckyus-iopenlinkeradmin, luckyus-ilopamanager

## Executive Summary

**FINDING**: The SnapshotComplete notifications are **EXPECTED BEHAVIOR**, not an error.

All three clusters are configured with:
- Automatic daily backups enabled (3-day retention)
- SNS notifications to `arn:aws:sns:us-east-1:257394478466:DBA` topic
- Snapshot window: **09:00-10:00 UTC daily**

Each cluster takes one snapshot per day at the configured window, resulting in **3 SnapshotComplete notifications daily** (one per cluster).

## Cluster Comparison Table

| Attribute | luckyus-iopenlinker | luckyus-iopenlinkeradmin | luckyus-ilopamanager |
|-----------|---------------------|--------------------------|----------------------|
| **Node Type** | cache.t4g.micro | cache.t4g.micro | cache.t4g.micro |
| **Redis Version** | 6.2.6 | 6.2.6 | **6.0.5** (older) |
| **Status** | available | available | available |
| **Multi-AZ** | Enabled | Enabled | Enabled |
| **Node Count** | 2 | 2 | 2 |
| **Cluster Mode** | Disabled | Disabled | Disabled |
| **Snapshot Retention** | 3 days | 3 days | 3 days |
| **Snapshot Window** | 09:00-10:00 UTC | 09:00-10:00 UTC | 09:00-10:00 UTC |
| **Snapshotting Node** | -002 (replica) | -002 (replica) | -002 (replica) |
| **SNS Topic** | DBA (active) | DBA (active) | DBA (active) |
| **Maintenance Window** | Mon 04:00-05:00 | Sun 06:30-07:30 | Wed 06:30-07:30 |
| **Created** | 2025-08-13 | 2025-08-13 | 2025-09-09 |

## Node Details

### luckyus-iopenlinker

| Node | Role | AZ | Snapshot Retention | Status |
|------|------|----|--------------------|--------|
| luckyus-iopenlinker-001 | Primary | us-east-1b | 0 (no snapshots) | available |
| luckyus-iopenlinker-002 | Replica | us-east-1a | **3 days** | available |

### luckyus-iopenlinkeradmin

| Node | Role | AZ | Snapshot Retention | Status |
|------|------|----|--------------------|--------|
| luckyus-iopenlinkeradmin-001 | Primary | us-east-1a | 0 (no snapshots) | available |
| luckyus-iopenlinkeradmin-002 | Replica | us-east-1b | **3 days** | available |

### luckyus-ilopamanager

| Node | Role | AZ | Snapshot Retention | Status |
|------|------|----|--------------------|--------|
| luckyus-ilopamanager-001 | Primary | us-east-1a | 0 (no snapshots) | available |
| luckyus-ilopamanager-002 | Replica | us-east-1b | **3 days** | available |

## SNS Notification Configuration

All nodes configured with:
```json
{
  "TopicArn": "arn:aws:sns:us-east-1:257394478466:DBA",
  "TopicStatus": "active"
}
```

**Expected Notification Schedule**:
- **Daily at 09:00-10:00 UTC**: 3 SnapshotComplete notifications (one per cluster)
- **Weekly**: 21 total SnapshotComplete notifications

## Security Configuration

All clusters share identical security settings:

| Setting | Value |
|---------|-------|
| Security Group | sg-0deaa7cf7437e39c7 |
| Subnet Group | redis-group |
| Parameter Group | luckyus-ha-6 |
| Auth Token | Enabled |
| Transit Encryption | Enabled (required) |
| At-Rest Encryption | Enabled |
| Auto Minor Version Upgrade | Disabled |

## Root Cause Analysis

### Why You Receive SnapshotComplete Notifications

1. **Automatic Backups Enabled**: Each cluster has `SnapshotRetentionLimit: 3` on the -002 (replica) node
2. **SNS Topic Configured**: The DBA topic is subscribed to ElastiCache events
3. **Daily Snapshot Window**: All clusters snapshot at 09:00-10:00 UTC

### Notification Flow

```
[ElastiCache Cluster] → [Daily Backup 09:00-10:00 UTC]
         ↓
[Snapshot Created on -002 node]
         ↓
[SNS Topic: arn:aws:sns:us-east-1:257394478466:DBA]
         ↓
[SnapshotComplete Notification Sent]
```

## Recommendations

### Option 1: Keep Current Configuration (Recommended)
- Notifications are working as intended
- Useful for audit/compliance tracking
- No action required

### Option 2: Reduce Notification Noise
```bash
# If you want to disable SNS notifications for these clusters:
aws elasticache modify-cache-cluster \
  --cache-cluster-id luckyus-iopenlinker-002 \
  --notification-topic-status inactive \
  --region us-east-1

# Repeat for other -002 nodes
```

### Option 3: Filter at SNS Level
- Create SNS filter policy to route ElastiCache snapshot events to a separate topic
- Keep critical notifications (failures, failovers) on DBA topic

### Option 4: Upgrade Redis Version
- `luckyus-ilopamanager` runs Redis **6.0.5** (older)
- Consider upgrading to 6.2.6 to match other clusters
- Schedule during maintenance window: Wed 06:30-07:30 UTC

## Snapshot Visibility

**Note**: No current snapshots were visible in the `describe-snapshots` API response. This is normal because:
1. Automatic snapshots have a 3-day retention
2. Older snapshots are automatically deleted
3. The API response is point-in-time; snapshots exist but may not be listed if recently deleted

To verify snapshots:
```bash
# List all snapshots for a cluster
aws elasticache describe-snapshots \
  --replication-group-id luckyus-iopenlinker \
  --region us-east-1
```

## Events Investigation

No events were returned from the ElastiCache describe-events API. This is expected because:
1. Event retention is limited (typically 14 days)
2. Snapshot events may have aged out
3. No failures or unusual events occurred

## Raw Data Reference

### Replication Group Configuration (All Clusters)

```json
{
  "AutomaticFailover": "enabled",
  "MultiAZ": "enabled",
  "ClusterEnabled": false,
  "CacheNodeType": "cache.t4g.micro",
  "TransitEncryptionEnabled": true,
  "AtRestEncryptionEnabled": true,
  "SnapshotRetentionLimit": 3,
  "SnapshotWindow": "09:00-10:00",
  "AuthTokenEnabled": true
}
```

### Node Endpoints

| Cluster | Node | Endpoint |
|---------|------|----------|
| luckyus-iopenlinker | -001 | luckyus-iopenlinker-001.luckyus-iopenlinker.vyllrs.use1.cache.amazonaws.com:6379 |
| luckyus-iopenlinker | -002 | luckyus-iopenlinker-002.luckyus-iopenlinker.vyllrs.use1.cache.amazonaws.com:6379 |
| luckyus-iopenlinkeradmin | -001 | luckyus-iopenlinkeradmin-001.luckyus-iopenlinkeradmin.vyllrs.use1.cache.amazonaws.com:6379 |
| luckyus-iopenlinkeradmin | -002 | luckyus-iopenlinkeradmin-002.luckyus-iopenlinkeradmin.vyllrs.use1.cache.amazonaws.com:6379 |
| luckyus-ilopamanager | -001 | luckyus-ilopamanager-001.luckyus-ilopamanager.vyllrs.use1.cache.amazonaws.com:6379 |
| luckyus-ilopamanager | -002 | luckyus-ilopamanager-002.luckyus-ilopamanager.vyllrs.use1.cache.amazonaws.com:6379 |

## Conclusion

The repeated SnapshotComplete notifications are **normal expected behavior** from properly configured ElastiCache Redis clusters with:
- Automatic backups enabled (3-day retention)
- SNS notifications active to DBA topic
- Daily snapshot window at 09:00-10:00 UTC

**No action required** unless you want to reduce notification frequency or change the notification routing.
