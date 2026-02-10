# EMERGENCY CLEANUP - Quick Reference Guide

**Cluster**: luckyur-log
**Status**: 🔴 CRITICAL - Only ~35 GB free, minimum dropped to 21.6 GB
**Time to Outage**: 2-3 days without action

---

## STEP 1: Connect to OpenSearch Dashboards

Access via VPC endpoint or OpenSearch Dashboards URL.

---

## STEP 2: Verify Current State (Copy-Paste Commands)

Run these in Dev Tools:

```json
// Check cluster health
GET _cluster/health

// Check disk allocation
GET _cat/allocation?v

// See all indices sorted by size
GET _cat/indices?v&s=store.size:desc&h=index,docs.count,store.size
```

---

## STEP 3: Identify Stale Indices (VERIFY BEFORE DELETE)

```json
// September 2025 indices (5 months old)
GET _cat/indices/*2025.09*?v&s=store.size:desc&h=index,docs.count,store.size

// October 2025 indices (4 months old)
GET _cat/indices/*2025.10*?v&s=store.size:desc&h=index,docs.count,store.size

// November 2025 indices (3 months old)
GET _cat/indices/*2025.11*?v&s=store.size:desc&h=index,docs.count,store.size
```

---

## STEP 4: Execute Deletions (P0 - IMMEDIATE)

### Delete September 2025 Indices (~125+ GB recovery)

```json
// ⚠️ WARNING: IRREVERSIBLE - Verify indices are correct first!

DELETE iprod_tomcat_lucky_k8s-2025.09.*
DELETE skywalking_idx_segment-2025.09.*
DELETE skywalking_idx_metrics-all-2025.09.*
```

### Delete October 2025 Indices (~50+ GB recovery)

```json
DELETE iprod_tomcat_lucky_k8s-2025.10.*
DELETE skywalking_idx_segment-2025.10.*
DELETE skywalking_idx_metrics-all-2025.10.*
```

---

## STEP 5: Verify Recovery

```json
// Should show increased free space
GET _cat/allocation?v

// Check cluster health
GET _cluster/health
```

---

## STEP 6: Create ISM Policies (Prevent Future Issues)

### Policy 1: App Logs (30-day retention)

```json
PUT _plugins/_ism/policies/app-logs-30d
{
  "policy": {
    "description": "Application logs retention policy - 30 days",
    "default_state": "hot",
    "states": [
      {
        "name": "hot",
        "actions": [{"rollover": {"min_index_age": "1d", "min_primary_shard_size": "30gb"}}],
        "transitions": [{"state_name": "delete", "conditions": {"min_index_age": "30d"}}]
      },
      {
        "name": "delete",
        "actions": [{"delete": {}}],
        "transitions": []
      }
    ],
    "ism_template": [{"index_patterns": ["iprod_tomcat_lucky_k8s-*", "iprod_tomcat_lucky-*"], "priority": 100}]
  }
}
```

### Policy 2: SkyWalking Traces (7-day retention)

```json
PUT _plugins/_ism/policies/skywalking-traces-7d
{
  "policy": {
    "description": "SkyWalking trace segments - 7 day retention",
    "default_state": "hot",
    "states": [
      {"name": "hot", "actions": [], "transitions": [{"state_name": "delete", "conditions": {"min_index_age": "7d"}}]},
      {"name": "delete", "actions": [{"delete": {}}], "transitions": []}
    ],
    "ism_template": [{"index_patterns": ["skywalking_idx_segment*"], "priority": 100}]
  }
}
```

### Policy 3: SkyWalking Metrics (30-day retention)

```json
PUT _plugins/_ism/policies/skywalking-metrics-30d
{
  "policy": {
    "description": "SkyWalking metrics - 30 day retention",
    "default_state": "hot",
    "states": [
      {"name": "hot", "actions": [], "transitions": [{"state_name": "delete", "conditions": {"min_index_age": "30d"}}]},
      {"name": "delete", "actions": [{"delete": {}}], "transitions": []}
    ],
    "ism_template": [{"index_patterns": ["skywalking_idx_metrics-all*"], "priority": 100}]
  }
}
```

---

## STEP 7: Attach Policies to Existing Indices

```json
POST _plugins/_ism/add/iprod_tomcat_lucky_k8s-*
{"policy_id": "app-logs-30d"}

POST _plugins/_ism/add/skywalking_idx_segment*
{"policy_id": "skywalking-traces-7d"}

POST _plugins/_ism/add/skywalking_idx_metrics-all*
{"policy_id": "skywalking-metrics-30d"}
```

---

## Expected Results After Cleanup

| Metric | Before | After (Expected) |
|--------|--------|------------------|
| Free Space | ~35 GB | ~180+ GB |
| Usage | 96%+ | ~85% |
| Days to Outage | 2-3 days | 30+ days |

---

## CloudWatch Monitoring

After cleanup, verify via AWS Console or CLI:

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ES \
  --metric-name FreeStorageSpace \
  --dimensions Name=DomainName,Value=luckyur-log Name=ClientId,Value=257394478466 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Minimum Maximum Average \
  --region us-east-1
```

---

## Emergency Contacts

- DevOps Team: For cluster access and execution
- Development Team: For SkyWalking config changes
- AWS Support: If cluster enters read-only mode

---

*Document created: 2026-02-10*
