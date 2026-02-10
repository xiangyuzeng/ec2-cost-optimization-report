# OpenSearch luckyur-log Storage Crisis Analysis

**Date**: 2026-02-10
**Cluster**: luckyur-log (AWS OpenSearch Service)
**Region**: us-east-1
**Status**: 🔴 CRITICAL - Immediate action required

---

## Overview

This repository contains a comprehensive analysis of the luckyur-log OpenSearch cluster storage crisis, including:

- **Root cause analysis** of storage consumption
- **Immediate cleanup actions** to prevent cluster outage
- **ISM (Index State Management) policies** for long-term prevention
- **Monitoring recommendations** and CloudWatch alarms

---

## Current Situation

| Metric | Value | Status |
|--------|-------|--------|
| Free Storage | ~35 GB | 🔴 CRITICAL |
| Lowest Point (Feb 9) | **21.6 GB** | 🔴 NEAR OUTAGE |
| Storage Utilization | 96.4%+ | 🔴 CRITICAL |
| Days to Outage | 2-3 days | 🔴 URGENT |

---

## Files in This Repository

| File | Description |
|------|-------------|
| `LUCKYUR-LOG-STORAGE-CRISIS-ANALYSIS.md` | Full comprehensive analysis report |
| `QUICK-REFERENCE-EMERGENCY-CLEANUP.md` | Copy-paste commands for immediate cleanup |
| `ACTION-SUMMARY-TABLE.md` | Priority action table with timeline |
| `ism-policies/` | JSON files for Index State Management policies |

### ISM Policies

| Policy File | Description | Retention |
|-------------|-------------|-----------|
| `app-logs-30d.json` | Application logs (iprod_tomcat_*) | 30 days |
| `skywalking-traces-7d.json` | SkyWalking trace segments | 7 days |
| `skywalking-metrics-30d.json` | SkyWalking aggregated metrics | 30 days |
| `aws-ops-14d.json` | AWS cloud operation logs | 14 days |
| `dify-logs-14d.json` | Dify service logs | 14 days |

---

## Quick Start - Emergency Cleanup

### Step 1: Delete Stale Indices (Immediate)

```json
// In OpenSearch Dev Tools - DELETE September 2025 indices (~125 GB)
DELETE iprod_tomcat_lucky_k8s-2025.09.*
DELETE skywalking_idx_segment-2025.09.*
DELETE skywalking_idx_metrics-all-2025.09.*

// DELETE October 2025 indices (~50 GB)
DELETE iprod_tomcat_lucky_k8s-2025.10.*
DELETE skywalking_idx_segment-2025.10.*
DELETE skywalking_idx_metrics-all-2025.10.*
```

### Step 2: Apply ISM Policies (This Week)

See `ism-policies/` directory for JSON files to apply.

---

## Root Cause

1. **No Index Lifecycle Management (ILM/ISM) policies configured**
2. **Historical indices from September 2025 still present** (5 months old)
3. **SkyWalking default retention too long** (likely 90 days, should be 7-14 days)

---

## Expected Outcome After Cleanup

| Metric | Before | After |
|--------|--------|-------|
| Free Storage | ~35 GB | ~210 GB |
| Storage Utilization | 96%+ | ~82% |
| Days to Outage | 2-3 days | 30+ days |

---

## Contact

- DevOps Team: Cluster access and execution
- Development Team: SkyWalking configuration changes

---

*Analysis generated: 2026-02-10*
