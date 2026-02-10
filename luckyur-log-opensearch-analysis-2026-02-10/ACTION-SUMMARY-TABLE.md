# luckyur-log Cleanup Action Summary

**Date**: 2026-02-10
**Status**: 🔴 CRITICAL

---

## Priority Action Table

| Priority | Action | Command | Expected Recovery | Risk | Timeline |
|----------|--------|---------|-------------------|------|----------|
| **P0** | Delete Sep 2025 indices | `DELETE *2025.09*` | ~125 GB | Low | **TODAY** |
| **P0** | Delete Oct 2025 indices | `DELETE *2025.10*` | ~50 GB | Low | **TODAY** |
| **P1** | Delete Nov 2025 indices | `DELETE *2025.11*` | ~50 GB | Medium | This week |
| **P1** | Create ISM policy: app-logs-30d | See JSON | Prevents recurrence | None | This week |
| **P1** | Create ISM policy: skywalking-traces-7d | See JSON | Reduces daily growth | None | This week |
| **P1** | Create ISM policy: skywalking-metrics-30d | See JSON | Prevents recurrence | None | This week |
| **P2** | Delete Dec 2025 indices | `DELETE *2025.12*` | ~30 GB | Medium-High | If needed |
| **P2** | Configure SkyWalking retention | OAP config | Reduces future ingest | Low | This week |
| **P3** | Migrate gp2 → gp3 | AWS CLI | $26/mo savings | None | Next week |
| **P3** | Graviton migration | AWS Console | $58/mo savings | Low | Next month |

---

## Cleanup Sequence (Recommended Order)

### Phase 1: Emergency Cleanup (Today)
1. ✅ Verify cluster access
2. ✅ Run discovery queries to confirm stale indices
3. ⚠️ Delete September 2025 indices (~125 GB)
4. 📊 Monitor FreeStorageSpace metric
5. ⚠️ Delete October 2025 indices if needed (~50 GB)
6. 📊 Verify storage recovery

### Phase 2: Prevention (This Week)
1. Create ISM policy: `app-logs-30d`
2. Create ISM policy: `skywalking-traces-7d`
3. Create ISM policy: `skywalking-metrics-30d`
4. Attach policies to existing indices
5. Verify policies are active

### Phase 3: Optimization (This Month)
1. Review SkyWalking OAP retention settings
2. Delete November 2025 indices
3. Plan gp3 storage migration
4. Set up CloudWatch alarms

---

## Index Retention Policy Summary

| Index Pattern | Current Retention | Recommended | Savings |
|---------------|-------------------|-------------|---------|
| `iprod_tomcat_lucky_k8s-*` | Unlimited | 30 days | ~50% reduction |
| `skywalking_idx_segment*` | Unlimited | 7 days | ~75% reduction |
| `skywalking_idx_metrics-all*` | Unlimited | 30 days | ~50% reduction |
| `aws_cloud_operation*` | Unlimited | 14 days | ~50% reduction |
| `prod-*-dify*` | Unlimited | 14 days | ~50% reduction |

---

## Storage Projection

### Current State (No Action)
```
Day 0 (Feb 10):  ~35 GB free
Day 1 (Feb 11):  ~30 GB free
Day 2 (Feb 12):  ~25 GB free
Day 3 (Feb 13):  ⚠️ 15-20 GB - WRITE BLOCK RISK
```

### After Cleanup (~175 GB recovered)
```
Day 0 (Feb 10):  ~210 GB free (after cleanup)
Day 7:           ~185 GB free
Day 14:          ~160 GB free
Day 30:          ~100 GB free (ISM starts deleting)
Day 45+:         Stable ~100-150 GB (ISM maintaining)
```

---

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Cluster write-block | HIGH (2-3 days) | CRITICAL | Immediate cleanup |
| Data loss from deletion | LOW | LOW | Old data, 5+ months |
| ISM policy misconfiguration | LOW | MEDIUM | Test on small index first |
| Application impact | VERY LOW | LOW | Only historical data |

---

## Verification Checkpoints

- [ ] Sep 2025 indices deleted
- [ ] Oct 2025 indices deleted
- [ ] FreeStorageSpace > 150 GB
- [ ] ISM policies created (4 policies)
- [ ] ISM policies attached to indices
- [ ] CloudWatch alarms configured
- [ ] Team notified of changes

---

*Generated: 2026-02-10*
