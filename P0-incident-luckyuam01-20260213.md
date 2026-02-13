# P0 Incident Report / P0 事故报告

## 【vm-宕机】luckyuam01-prod-usb-aws Heartbeat Lost — AWS System Status Check Failure & VM Reboot

| Field | Value |
|-------|-------|
| **Incident ID** | INC-20260213-UAM01 |
| **Severity / 严重级别** | P0 (Critical) |
| **Alert Name** | 【vm-宕机】P0 up监控指标心跳丢失10分钟，需检查设备是否宕机 |
| **Host / 主机** | luckyuam01-prod-usb-aws |
| **Instance ID** | i-0be9616720a6290ea |
| **Private IP** | 10.238.8.157 |
| **Instance Type** | c6i.large |
| **AZ** | us-east-1b |
| **Application** | luckyuam (User Account Management / 用户账号管理) |
| **Environment** | Production |
| **Incident Commander** | DBA On-Call |
| **Report Time** | 2026-02-13T20:30:41Z |

---

## 1. 根因分析 / Root Cause Analysis

### Primary Root Cause: AWS System-Level Status Check Failure (AWS 系统级状态检查失败)

The AWS **System Status Check** (`StatusCheckFailed_System`) began failing at **~20:12 UTC**, indicating a problem with the **underlying AWS infrastructure** (hypervisor, host hardware, or network connectivity at the physical level). This is **NOT a guest OS issue** — it is an AWS-side failure.

**Evidence Chain:**

| Metric | Before 20:12 | At 20:12-20:22 | After Reboot |
|--------|-------------|-----------------|--------------|
| StatusCheckFailed_System | 0.0 (OK) | **1.0 (FAILING)** | 0.0 (OK) |
| StatusCheckFailed_Instance | 0.0 (OK) | **1.0 at 20:12** | 0.0 (OK) |
| StatusCheckFailed (combined) | 0.0 (OK) | **1.0 at 20:11-20:21** | 0.0 (OK) |
| CPUUtilization | ~0.3% | 0.68% spike at 20:16 | ~0.28% |
| NetworkIn | ~7.4KB avg | 13.3KB spike at 20:16 | ~5.4KB |
| EC2 Instance State | running | running | running |

The VM was **automatically rebooted/recovered** at **20:22:35 UTC**, confirmed by EC2 console output showing a fresh cloud-init boot sequence:
```
cloud-init[1881]: Cloud-init v. 19.3-46.amzn2 running 'init-local' at Fri, 13 Feb 2026 20:22:35 +0000. Up 4.40 seconds.
```

### Secondary Issue: Monitoring Gap (监控盲区)

**CRITICAL FINDING:** The IP `10.238.8.157` is **NOT registered in the current Prometheus instance** as a scrape target. Zero targets exist for:
- The specific IP `10.238.8.157`
- The entire `10.238.8.x` subnet
- Any target matching "uam" or "luckyuam"

This means:
1. The `up{job="node"} == 0` alert originates from a **different monitoring system** (likely a separate Prometheus instance or external monitor)
2. The node_exporter on this host has a **monitoring registration gap** — it was never added to (or was removed from) the primary Prometheus scrape configuration
3. There is **no historical metrics data** for this host in the primary observability stack

---

## 2. 影响范围 / Impact Assessment

### Direct Impact (直接影响)

| Component | Impact | Duration |
|-----------|--------|----------|
| **luckyuam01-prod-usb-aws** | VM unreachable / rebooted | ~10 min (20:12 - 20:22 UTC) |
| **UAM Application** (User Account Management) | Service unavailable during reboot | ~10 min |
| **node_exporter** | Heartbeat lost (triggered P0 alert) | ~10+ min (may still be down post-reboot if not enabled on boot) |

### Potential Downstream Impact (潜在下游影响)

The `luckyuam` (User Account Management) application may affect:
- **User authentication flows** — if UAM handles auth for internal or external users
- **Related services**: `luckyus-auth`, `luckyus-authservice`, `luckyus-unionauth` Redis clusters
- **Related database**: `aws-luckyus-iluckyauthapi-rw` MySQL instance (auth API backend)
- **Internal admin operations** — `aws-luckyus-iadmin-rw`, `luckyus-iadmin` Redis

### What is NOT Affected (未受影响)

- No other EC2 instances with `app_name=luckyuam` found (this is a single-instance application)
- All database servers (MySQL, Redis, PostgreSQL) are on separate infrastructure
- No scheduled AWS maintenance events were pending for this instance
- EC2 instance is now **fully recovered** — state=running, SystemStatus=ok, InstanceStatus=ok

---

## 3. 处理措施 / Actions Taken

### Investigation Actions (调查操作)

| # | Time (UTC) | Action | Result |
|---|-----------|--------|--------|
| 1 | 20:30 | Pinged 10.238.8.157 | Tool unavailable in environment |
| 2 | 20:30 | Checked EC2 instance state via AWS CLI | **running**, c6i.large, us-east-1b |
| 3 | 20:30 | Checked EC2 status checks | All **OK** (system=ok, instance=ok, EBS=ok) |
| 4 | 20:30 | Checked scheduled events | **None** — no pending maintenance |
| 5 | 20:30 | Pulled CloudWatch CPUUtilization (1hr) | Low ~0.3%, spike to 0.68% at 20:16 (reboot activity) |
| 6 | 20:30 | Pulled StatusCheckFailed metrics (2hr) | **System failure 20:12-20:22**, Instance failure at 20:12 |
| 7 | 20:30 | Retrieved EC2 console output | **Confirmed fresh boot at 20:22:35 UTC** via cloud-init |
| 8 | 20:30 | Queried Prometheus `up{instance=~"10.238.8.157.*"}` | **Empty** — no targets registered |
| 9 | 20:30 | Searched all Prometheus targets for IP/hostname | **Not found** — monitoring gap confirmed |
| 10 | 20:30 | Checked CloudTrail for instance events | No events found in trail |
| 11 | 20:30 | Verified EBS volumes | 2 volumes (40GB root + 100GB data gp3), both in-use |
| 12 | 20:30 | Attempted SSH to host | Permission denied (no key access from this environment) |
| 13 | 20:30 | Attempted SSM RunCommand | AccessDeniedException — IAM policy restriction |
| 14 | 20:30 | Checked Grafana alerts | No UAM-specific alerts configured |
| 15 | 20:31 | Verified current status | **RECOVERED** — running, all checks OK |

### Immediate Remediation Required (需立即执行)

> **ACTION ITEMS — Must be completed by on-call team with SSH/SSM access:**

1. **SSH into luckyuam01-prod-usb-aws and verify node_exporter:**
   ```bash
   ssh ec2-user@10.238.8.157
   systemctl status node_exporter
   systemctl is-enabled node_exporter
   # If not running:
   systemctl start node_exporter
   systemctl enable node_exporter
   ```

2. **Verify UAM application is running post-reboot:**
   ```bash
   # Check the "luckin coffee agent" service shown in boot logs
   systemctl status luckin-coffee-agent  # or equivalent service name
   # Check application health endpoint
   curl -s http://localhost:<APP_PORT>/health
   ```

3. **Check system logs for pre-crash errors:**
   ```bash
   journalctl --since "2026-02-13 20:00:00" --until "2026-02-13 20:25:00" --no-pager
   dmesg | grep -i -E "error|fail|oom|panic"
   ```

4. **Register node_exporter in Prometheus:**
   - Add `10.238.8.157:9100` to Prometheus scrape targets under `job="node"`
   - Verify with: `curl http://10.238.8.157:9100/metrics | head`

---

## 4. 后续改进 / Follow-up & Preventive Measures

### P0 — Immediate (within 24 hours)

| # | Action Item | Owner | Priority |
|---|------------|-------|----------|
| 1 | **Register node_exporter in Prometheus** — Add 10.238.8.157:9100 to scrape config | Infra/SRE | P0 |
| 2 | **Enable node_exporter auto-start** — `systemctl enable node_exporter` | Infra/SRE | P0 |
| 3 | **Verify UAM application health** — Confirm full service recovery | App Team | P0 |
| 4 | **Audit all production hosts** — Find others missing from Prometheus | Infra/SRE | P0 |

### P1 — Within 1 Week

| # | Action Item | Owner | Priority |
|---|------------|-------|----------|
| 5 | **Enable EC2 Auto Recovery** — Set CloudWatch alarm for StatusCheckFailed_System → auto-recover | Infra | P1 |
| 6 | **Create UAM Grafana dashboard** — No dashboard exists for this service | DBA/SRE | P1 |
| 7 | **Implement service discovery** — Replace static Prometheus targets with EC2 service discovery using tags | Infra/SRE | P1 |
| 8 | **Add health check alerts for UAM** — Application-level monitoring, not just node_exporter | App Team | P1 |

### P2 — Within 1 Month

| # | Action Item | Owner | Priority |
|---|------------|-------|----------|
| 9 | **Evaluate HA for UAM** — Currently single-instance; evaluate multi-AZ deployment | Architecture | P2 |
| 10 | **SSM access for DBA** — Current IAM policy blocks SSM; add for emergency access | Security/Infra | P2 |
| 11 | **CloudTrail monitoring** — Ensure instance state changes trigger alerts | Infra/SRE | P2 |
| 12 | **Runbook for VM-down alerts** — Standardize P0 VM investigation process | SRE | P2 |

---

## 5. Timeline / 事件时间线

```
2026-02-13 (All times UTC)
═══════════════════════════════════════════════════════════════

18:27 - 20:07   All EC2 status checks PASSING (baseline healthy)
                CPU ~0.3%, NetworkIn ~7.4KB avg

~20:10          ⚠️  INCIDENT START
                StatusCheckFailed begins (combined metric)

20:12           🔴 StatusCheckFailed_System = 1.0 (AWS infra failure)
                🔴 StatusCheckFailed_Instance = 1.0
                node_exporter heartbeat lost
                P0 alert fires: up{job="node"} == 0

20:16           CPU spike to 0.68%, NetworkIn spike to 13.3KB
                (likely VM instability / pre-reboot activity)

20:17           StatusCheckFailed_System = 1.0 (continued)

20:21           StatusCheckFailed (combined) = 1.0 (continued)

20:22:35        🔄 VM REBOOT — cloud-init starts fresh
                Kernel 5.10.147-133.644.amzn2.x86_64 boots
                eth0 comes up with 10.238.8.157
                SSM agent, SSHD, "luckin coffee agent" start

20:22           StatusCheckFailed_System = 1.0 (last failure datapoint)
                StatusCheckFailed_Instance = 0.0 (instance recovered)

20:27:44        Console output timestamp — boot complete

20:30           🔍 Investigation begins
                EC2 state: running, all status checks OK
                Prometheus: NO targets found for this IP (monitoring gap)
                CloudTrail: No events found
                SSH: Permission denied (no key)
                SSM: Access denied (IAM policy)

20:31           ✅ EC2 CONFIRMED RECOVERED
                SystemStatus=ok, InstanceStatus=ok, EBS=ok

                ⚠️  PENDING: node_exporter status unknown
                    (requires SSH/SSM access to verify)
                ⚠️  PENDING: UAM application health unknown
                    (requires SSH/SSM access to verify)
```

---

## 6. Technical Evidence / 技术证据

### EC2 Instance Details
```
Instance ID:     i-0be9616720a6290ea
Name:            luckyuam01-prod-usb-aws
App:             luckyuam (User Account Management)
Environment:     prod
Type:            c6i.large (2 vCPU, 4 GiB RAM)
AZ:              us-east-1b
Launch Time:     2025-07-24T14:42:03+00:00
EBS Volumes:     /dev/xvda (40GB gp3), /dev/xvdb (100GB gp3)
```

### Root Cause Classification
```
Category:        AWS Infrastructure Failure
Sub-category:    System Status Check Failed (hypervisor/hardware level)
Resolution:      Automatic VM recovery via reboot
Duration:        ~10 minutes (20:12 - 20:22 UTC)
Data Loss Risk:  LOW (EBS volumes persisted, no evidence of corruption)
```

### Monitoring Gaps Identified
```
1. node_exporter NOT in Prometheus scrape targets
2. No Grafana dashboard for UAM service
3. No application-level health check alert
4. No EC2 Auto Recovery alarm configured
5. No CloudTrail alert for instance state changes
```

---

*Report generated: 2026-02-13T20:31:00Z*
*Next update: After on-call team verifies node_exporter and UAM application status via SSH*
*Escalation: If UAM application is not recovered within 30 minutes, escalate to App Team lead*
