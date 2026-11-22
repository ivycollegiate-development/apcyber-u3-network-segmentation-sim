# Segmentation Checklist — U3 L10 Network Segmentation Sim

**Complete each step in order. Check off (☑) as you go. Capture screenshots for evidence.**

---

## Phase 0: Setup (2 min)

- [ ] Fork repo → your GitHub account
- [ ] Open in Codespaces (green "Code" → "Codespaces" → "Create codespace on main")
- [ ] Wait for container to start (Python 3.11, no extra deps needed)
- [ ] Terminal: `python3 seg_sim.py` → type `help` to see commands
- [ ] Type `status` — confirm **flat network** (all devices in 10.10.10.0/24, no VLANs)

---

## Phase 1: Create VLANs (5 min)

*Use `create_vlan <id> <name> <cidr>` for each.*

- [ ] VLAN 10 — MGMT — 10.10.10.0/24
- [ ] VLAN 20 — STAFF — 10.10.20.0/24
- [ ] VLAN 30 — DMZ — 10.10.30.0/24
- [ ] VLAN 40 — SERVERS — 10.10.40.0/24
- [ ] VLAN 50 — IOT — 10.10.50.0/24
- [ ] VLAN 60 — GUEST — 10.10.60.0/24
- [ ] Verify: `status` → shows 6 VLANs with correct CIDRs

---

## Phase 2: Assign Access Ports (5 min)

*Map each device group to its VLAN. Use `assign_access <port> <vlan_id>`.*

| Device Group | Port(s) | VLAN ID | Command |
|--------------|---------|---------|---------|
| Core switch mgmt | eth_mgmt | 10 | `assign_access eth_mgmt 10` |
| Employee PCs (20) | eth1–eth20 | 20 | `assign_access eth1 20` ... `assign_access eth20 20` |
| Web server | eth_web | 30 | `assign_access eth_web 30` |
| Email server | eth_email | 30 | `assign_access eth_email 30` |
| File server | eth_files | 40 | `assign_access eth_files 40` |
| IoT cameras (10) | eth_cam1–eth_cam10 | 50 | `assign_access eth_cam1 50` ... |
| Guest Wi-Fi AP | eth_guest_ap | 60 | `assign_access eth_guest_ap 60` |
| Firewall (LAN side) | eth_fw_lan | (trunk — see Phase 3) | — |

- [ ] Verify: `status` → each access port shows correct VLAN

---

## Phase 3: Configure Trunk Ports (3 min)

*Firewall and any uplink switches need all VLANs tagged.*

- [ ] `assign_trunk eth_fw_lan "10,20,30,40,50,60"` (firewall LAN interface)
- [ ] `assign_trunk eth_uplink "10,20,30,40,50,60"` (if simulator has uplink)
- [ ] Verify: `status` → trunk ports show all 6 VLANs

---

## Phase 4: Enable Inter-VLAN Routing (2 min)

- [ ] `enable_routing` — creates L3 interfaces (SVIs) on core switch for each VLAN
- [ ] Verify: `status` → shows gateway IPs for each VLAN (e.g., 10.10.20.1 for STAFF)

---

## Phase 5: Configure Firewall Rules (10 min)

*Syntax: `fw_rule <src_vlan> <dst_vlan> <proto> <port> <action>`*
*Use VLAN **names** (MGMT, STAFF, DMZ, SERVERS, IOT, GUEST) or "INTERNET" for WAN.*
*Protocol: `tcp`, `udp`, `icmp`, `any`. Port: number or `any`. Action: `allow`, `deny`.*

**Required rules (in order — first match wins):**

| # | Source | Dest | Proto | Port | Action | Check ID |
|---|--------|------|-------|------|--------|----------|
| 1 | DMZ | INTERNET | tcp | 80 | allow | FW-001 |
| 2 | DMZ | INTERNET | tcp | 443 | allow | FW-001 |
| 3 | DMZ | INTERNET | tcp | 25 | allow | FW-001 |
| 4 | DMZ | INTERNET | tcp | 587 | allow | FW-001 |
| 5 | DMZ | SERVERS | any | any | deny | FW-002 |
| 6 | DMZ | STAFF | any | any | deny | FW-002 |
| 7 | DMZ | IOT | any | any | deny | FW-002 |
| 8 | DMZ | GUEST | any | any | deny | FW-002 |
| 9 | STAFF | DMZ | tcp | 80 | allow | FW-003 |
| 10 | STAFF | DMZ | tcp | 443 | allow | FW-003 |
| 11 | STAFF | SERVERS | tcp | 445 | allow | FW-004 |
| 12 | STAFF | SERVERS | tcp | 2049 | allow | FW-004 |
| 13 | STAFF | IOT | any | any | deny | FW-005 |
| 14 | GUEST | STAFF | any | any | deny | FW-006 |
| 15 | GUEST | DMZ | any | any | deny | FW-006 |
| 16 | GUEST | SERVERS | any | any | deny | FW-006 |
| 17 | GUEST | IOT | any | any | deny | FW-006 |
| 18 | IOT | INTERNET | any | any | deny | **FW-007** |
| 19 | MGMT | STAFF | any | any | deny | FW-008 |
| 20 | MGMT | DMZ | any | any | deny | FW-008 |
| 21 | MGMT | SERVERS | any | any | deny | FW-008 |
| 22 | MGMT | IOT | any | any | deny | FW-008 |
| 23 | MGMT | GUEST | any | any | deny | FW-008 |
| 24 | MGMT | INTERNET | any | any | deny | FW-008 |

- [ ] Verify: `status` → firewall rules table shows all 24 rules in correct order

---

## Phase 6: Verification Testing (15 min)

*Test EVERY check. Use `verify_ping <src_ip> <dst_ip>` and `verify_port <src_ip> <dst_ip> <port>`.*
*Source IPs are the gateway IPs of each VLAN (e.g., STAFF gateway = 10.10.20.1).*
*Destination IPs are the actual device IPs in target VLAN.*

### ALLOW tests (expect SUCCESS = PASS)

| Check | Test | Command | Expected |
|-------|------|---------|----------|
| FW-001 | DMZ Web → Internet (HTTP) | `verify_port 10.10.30.10 8.8.8.8 80` | PASS (connects) |
| FW-001 | DMZ Web → Internet (HTTPS) | `verify_port 10.10.30.10 8.8.8.8 443` | PASS |
| FW-001 | DMZ Email → Internet (SMTP) | `verify_port 10.10.30.11 8.8.8.8 25` | PASS |
| FW-001 | DMZ Email → Internet (Submission) | `verify_port 10.10.30.11 8.8.8.8 587` | PASS |
| FW-003 | STAFF → DMZ Web (HTTP) | `verify_port 10.10.20.100 10.10.30.10 80` | PASS |
| FW-003 | STAFF → DMZ Web (HTTPS) | `verify_port 10.10.20.100 10.10.30.10 443` | PASS |
| FW-004 | STAFF → File Server (SMB) | `verify_port 10.10.20.100 10.10.40.20 445` | PASS |
| FW-004 | STAFF → File Server (NFS) | `verify_port 10.10.20.100 10.10.40.20 2049` | PASS |
| VLAN-001 | Same-VLAN ping (STAFF PC → STAFF PC) | `verify_ping 10.10.20.100 10.10.20.101` | PASS |
| VLAN-001 | Same-VLAN ping (IoT cam → IoT cam) | `verify_ping 10.10.50.200 10.10.50.201` | PASS |

### DENY tests (expect FAILURE = PASS — traffic blocked)

| Check | Test | Command | Expected |
|-------|------|---------|----------|
| FW-002 | DMZ Web → File Server | `verify_port 10.10.30.10 10.10.40.20 445` | FAIL (blocked) |
| FW-002 | DMZ Web → Staff PC | `verify_ping 10.10.30.10 10.10.20.100` | FAIL |
| FW-002 | DMZ Web → IoT Cam | `verify_ping 10.10.30.10 10.10.50.200` | FAIL |
| FW-002 | DMZ Web → Guest | `verify_ping 10.10.30.10 10.10.60.150` | FAIL |
| FW-005 | STAFF → IoT Cam | `verify_ping 10.10.20.100 10.10.50.200` | FAIL |
| FW-006 | Guest → Staff PC | `verify_ping 10.10.60.150 10.10.20.100` | FAIL |
| FW-006 | Guest → DMZ Web | `verify_ping 10.10.60.150 10.10.30.10` | FAIL |
| FW-006 | Guest → File Server | `verify_port 10.10.60.150 10.10.40.20 445` | FAIL |
| FW-006 | Guest → IoT Cam | `verify_ping 10.10.60.150 10.10.50.200` | FAIL |
| **FW-007** | **IoT Cam → Internet** | `verify_port 10.10.50.200 8.8.8.8 53` | **FAIL (CRITICAL)** |
| FW-008 | MGMT → Staff | `verify_ping 10.10.10.1 10.10.20.100` | FAIL |
| FW-008 | MGMT → DMZ | `verify_ping 10.10.10.1 10.10.30.10` | FAIL |

### Routing / VLAN sanity tests

| Check | Test | Command | Expected |
|-------|------|---------|----------|
| ROUTE-001 | STAFF gateway reachable | `verify_ping 10.10.20.100 10.10.20.1` | PASS |
| ROUTE-001 | DMZ gateway reachable | `verify_ping 10.10.30.10 10.10.30.1` | PASS |
| VLAN-002 | Staff PC in VLAN 20 | `status` shows eth1–eth20 in VLAN 20 | PASS |
| VLAN-002 | IoT cams in VLAN 50 | `status` shows eth_cam1–10 in VLAN 50 | PASS |
| VLAN-003 | Firewall trunk has all VLANs | `status` shows eth_fw_lan trunk: 10,20,30,40,50,60 | PASS |

---

## Phase 7: Save & Annotate (5 min)

- [ ] In simulator: `save_log` → writes `segmentation_log.csv`
- [ ] Exit simulator: `exit`
- [ ] Open `segmentation_log.csv` — every row has a `notes` column
- [ ] **Annotate every row:** PASS or FAIL + one-sentence justification
  - Example PASS: "PASS — FW rule 1 allows DMZ→Internet TCP/80 as designed"
  - Example FAIL: "FAIL — FW rule 18 missing; added `fw_rule IOT INTERNET any any deny` and retested"
- [ ] Write **Engineer Summary** (commit message or `ENGINEER_SUMMARY.md`):
  - Total verifications: ___
  - PASS: ___ | FAIL: ___
  - Hardest rule: ________________________________________ (why?)
  - Misconfiguration caught: ______________________________ (Check ID + fix)

---

## Phase 8: Submit (2 min)

- [ ] `git add segmentation_log.csv ENGINEER_SUMMARY.md`
- [ ] `git commit -m "U3 L10: Segmentation complete — X PASS, Y FAIL. Hardest: FW-007 (IoT internet block). Caught: FW-007 missing initially."`
- [ ] `git push`
- [ ] Submit via GitHub Classroom (link in Classroom)

---

## Time Budget (45 min class)

| Phase | Time |
|-------|------|
| 0: Setup | 2 min |
| 1: Create VLANs | 5 min |
| 2: Access Ports | 5 min |
| 3: Trunk Ports | 3 min |
| 4: Routing | 2 min |
| 5: Firewall Rules | 10 min |
| 6: Verification | 15 min |
| 7: Save & Annotate | 5 min |
| 8: Submit | 2 min |
| **Total** | **~49 min** (buffer: skip sanity tests if short) |

---

## Common Pitfalls (From Pilot)

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Firewall rules evaluated top-down; deny before allow | Allow rule never matches | Put specific ALLOW rules before broad DENY rules |
| Forgot `enable_routing` | All cross-VLAN pings fail (no gateway) | Run `enable_routing` before testing |
| Used VLAN IDs instead of names in fw_rule | "Unknown VLAN" error | Use names: STAFF, DMZ, SERVERS, IOT, GUEST, MGMT, INTERNET |
| IoT → Internet not tested | FW-007 missed | **Always test FW-007 explicitly** — it's the CISA fix |
| Trunk missing VLAN 10 (MGMT) | Firewall can't reach mgmt interface | Include 10 in trunk VLAN list |
| Verification log not saved | Empty CSV | Must run `save_log` before `exit` |
| Notes column empty | Auto-grade fails | Fill every row before commit |