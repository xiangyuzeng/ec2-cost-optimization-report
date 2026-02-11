# RDS Events Report: aws-luckyus-isalescdp-rw

**Date**: 2026-02-11
**Time Range**: 00:00 - 12:00 UTC
**Instance**: aws-luckyus-isalescdp-rw
**Region**: us-east-1

## Summary

Only **backup events** were recorded for this instance. No configuration changes, failovers, or maintenance events occurred.

## Events Timeline

| Time (UTC) | Category | Event |
|------------|----------|-------|
| 03:51:27 | backup | Backing up DB instance |
| 03:57:31 | backup | Finished DB Instance backup |

**Backup Duration**: ~6 minutes

## Correlation with Performance Spike

| Event | Time | Relation to Spike |
|-------|------|-------------------|
| Backup Started | 03:51 UTC | **1 hour before spike** |
| Backup Finished | 03:57 UTC | **1 hour before spike** |
| Performance Spike | 05:00-05:30 UTC | **Not caused by backup** |

**Conclusion**: The automated RDS backup completed **well before** the slow query spike at 05:00 UTC. The backup is **NOT the root cause**.

## Event Categories Checked

- ✅ backup - Found (normal automated backup)
- ✅ configuration change - None
- ✅ failover - None
- ✅ failure - None
- ✅ maintenance - None
- ✅ notification - None
- ✅ recovery - None
- ✅ restoration - None

## Root Cause Confirmation

The absence of RDS infrastructure events during 05:00-05:30 UTC confirms that:

1. **No AWS-side issues** caused the spike
2. **No failover or maintenance** occurred
3. **The spike was application-driven** (data cleanup jobs)

This aligns with our MySQL investigation findings:
- DELETE operations on `t_user_event` and `t_user_event_track` tables
- Application-triggered cleanup (no MySQL scheduled events)
- Missing index on `create_time` column

## Raw AWS Response

```json
{
    "Events": [
        {
            "SourceIdentifier": "aws-luckyus-isalescdp-rw",
            "SourceType": "db-instance",
            "Message": "Backing up DB instance",
            "EventCategories": ["backup"],
            "Date": "2026-02-11T03:51:27.999000+00:00",
            "SourceArn": "arn:aws:rds:us-east-1:257394478466:db:aws-luckyus-isalescdp-rw"
        },
        {
            "SourceIdentifier": "aws-luckyus-isalescdp-rw",
            "SourceType": "db-instance",
            "Message": "Finished DB Instance backup",
            "EventCategories": ["backup"],
            "Date": "2026-02-11T03:57:31.546000+00:00",
            "SourceArn": "arn:aws:rds:us-east-1:257394478466:db:aws-luckyus-isalescdp-rw"
        }
    ]
}
```

## Command Reference

```bash
# Note: This is a standalone instance, not a cluster
# Use --source-type db-instance (not db-cluster)

aws rds describe-events \
  --source-identifier aws-luckyus-isalescdp-rw \
  --source-type db-instance \
  --start-time 2026-02-11T00:00:00Z \
  --end-time 2026-02-11T12:00:00Z \
  --region us-east-1
```
