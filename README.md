# apcyber-u3-network-segmentation-sim — Network Segmentation Simulator

AP Cybersecurity Unit 3, Lesson 10. A CLI-based network simulator where you configure VLANs, trunk ports, inter-VLAN routing, and firewall rules to segment a small business network.

**You do not write the simulator.** The network engine is provided in `seg_sim.py`. You run it, configure the network step by step, and capture evidence that your segmentation works.

## The Scenario

You are a network security engineer for **ICA Taiwan — Tan Tzu Campus**. The campus network has grown organically and is currently **flat** (one /24, no segmentation). Your job: design and implement a segmented network with **6 VLANs** and a **firewall** controlling all inter-VLAN traffic.

**Current state (flat):**
- Web server (public) — 10.10.10.10
- Email server (public) — 10.10.10.11
- File server (private) — 10.10.10.20
- 20 employee PCs — 10.10.10.100–119
- 10 IoT cameras — 10.10.10.200–209
- Guest Wi-Fi clients — 10.10.10.150–169
- Core switch (L3) — 10.10.10.1
- Firewall (WAN) — 10.10.10.254

**Target state (segmented):**

| VLAN | Name | CIDR | Purpose | Internet? |
|------|------|------|---------|-----------|
| 10 | MGMT | 10.10.10.0/24 | Switch/firewall management | Out-of-band only |
| 20 | STAFF | 10.10.20.0/24 | Employee PCs | Yes (via FW) |
| 30 | DMZ | 10.10.30.0/24 | Web + Email servers | Restricted (80/443, 25/587) |
| 40 | SERVERS | 10.10.40.0/24 | Internal file server | **NO** |
| 50 | IOT | 10.10.50.0/24 | Cameras/sensors | **NO** (CISA fix) |
| 60 | GUEST | 10.10.60.0/24 | Guest Wi-Fi | Captive portal only |

## Your Job

1. **Fork** this repo to your account.
2. Open in VS Code — Codespaces from the repo page, or on the class server at `vscode.ivycollegiate.org` (school account). `git pull` first, always.
3. Review the **segmentation checklist** (`segmentation_checklist.md`) — it defines every required step.
4. Run the simulator in the **terminal panel**:

   ```bash
   python3 seg_sim.py
   ```

   The environment has Python 3.11 with standard library only (no external deps). Do not edit the script.
5. The simulator starts in **flat mode**. You issue commands to:
   - Create VLANs and assign IP ranges
   - Configure access ports (assign ports to VLANs)
   - Configure trunk ports (tagged VLANs)
   - Enable inter-VLAN routing on the core switch
   - Configure firewall rules (source VLAN → dest VLAN, protocol, port, action)
6. After each step, run **verification commands** (ping, traceroute, port scan) to prove the segmentation works.
7. The simulator logs every command and verification result to **`segmentation_log.csv`** — your graded deliverable.
8. **Read your own output.** Annotate each verification with PASS/FAIL and notes in the `notes` column.
9. Commit `segmentation_log.csv`. Then write your **engineer notes** explaining any failures and how you fixed them.
10. Commit again with your annotated log.

## The Simulator Commands

```bash
# Start the simulator (interactive)
python3 seg_sim.py

# Inside the simulator:
> help                          # Show all commands
> status                        # Show current network state (VLANs, ports, routes, FW rules)
> create_vlan <id> <name> <cidr>   # e.g., create_vlan 20 STAFF 10.10.20.0/24
> assign_access <port> <vlan_id>   # e.g., assign_access eth1 20
> assign_trunk <port> <vlan_ids>   # e.g., assign_trunk eth0 "10,20,30,40,50,60"
> enable_routing                  # Enable inter-VLAN routing on core switch
> fw_rule <src_vlan> <dst_vlan> <proto> <port> <action>  # e.g., fw_rule STAFF DMZ tcp 80 allow
> verify_ping <src_ip> <dst_ip>    # Test connectivity
> verify_port <src_ip> <dst_ip> <port>  # Test specific port
> save_log                        # Write segmentation_log.csv
> exit                            # Quit (auto-saves)
```

## The Segmentation Checks (What You Must Verify)

| Check ID | Verification | Expected Result | Why It Matters |
|----------|--------------|-----------------|----------------|
| **VLAN-001** | All 6 VLANs created with correct CIDRs | `status` shows 6 VLANs | Foundation of segmentation |
| **VLAN-002** | Access ports assigned correctly | Staff PCs in VLAN 20, IoT in VLAN 50, etc. | Devices in right broadcast domain |
| **VLAN-003** | Trunk port carries all VLAN tags | `eth0` trunk has all 6 VLANs | Inter-switch / FW connectivity |
| **ROUTE-001** | Inter-VLAN routing enabled | Core switch has L3 interfaces for all VLANs | Traffic can cross VLANs (if FW allows) |
| **FW-001** | DMZ → Internet (80, 443, 25, 587) **ALLOW** | Web/email servers reachable from WAN | Public services work |
| **FW-002** | DMZ → SERVERS, STAFF, IOT **DENY** | No lateral movement from compromised DMZ | Containment |
| **FW-003** | STAFF → DMZ (80, 443) **ALLOW** | Employees access web/email | Business function |
| **FW-004** | STAFF → SERVERS (445, 2049) **ALLOW** | File server access (SMB/NFS) | Business function |
| **FW-005** | STAFF → IOT **DENY** | No access to cameras from PCs | IoT isolation |
| **FW-006** | GUEST → ALL INTERNAL **DENY** | Guest cannot reach Staff, DMZ, Servers, IoT | Guest isolation |
| **FW-007** | IOT → INTERNET **DENY** | Cameras cannot phone home / be hacked | **CISA water-system fix** |
| **FW-008** | MGMT → ALL **DENY** except out-of-band | Management plane isolated | Admin security |

## The Real Skill Is Verification

**Every `verify_ping` and `verify_port` must be intentional.** Your job is not to just run commands — it's to prove the segmentation works *and* document what fails when you test the "deny" rules.

- A **DENY** rule that you test and *fails* (traffic blocked) = **PASS** (the rule works)
- An **ALLOW** rule that you test and *succeeds* (traffic passes) = **PASS**
- Any other result = **FAIL** — fix the rule or the routing

## What You Hand In

1. **`segmentation_log.csv`** — committed, with your `notes` column filled in for every verification row.
2. **A one-paragraph engineer summary** (in commit message or `ENGINEER_SUMMARY.md`):
   - How many verification tests total?
   - How many PASS / FAIL?
   - **The one rule that was hardest to get right** — and why.
3. **A specific misconfiguration you caught**, named by Check ID, with one sentence on what was wrong and how you fixed it.

## The Gate (Auto-Grading)

The GitHub Action will verify:

- `segmentation_log.csv` exists and is committed.
- It contains all verification columns + `notes`.
- Every verification row has PASS/FAIL in `notes`.
- At least 10 verification rows (covers all checks above).
- You named a specific misconfiguration you caught.

---

## Files

| File | What It Is |
|------|------------|
| `seg_sim.py` | The network simulator. Read it. Do not edit it. |
| `segmentation_checklist.md` | Step-by-step checklist. Read before running. |
| `segmentation_log.csv` | **Your output.** Created when you run `save_log` in the simulator. You edit this. |
| `ENGINEER_SUMMARY.md` | Optional — your summary if not in commit message. |
| `paper-fallback.md` | **Offline equivalent** — worksheet version if Codespaces/Chromebooks fail. |

---

## Paper Fallback (If Codespaces Fails)

See `paper-fallback.md` for the complete worksheet version. You will:
- Draw the network diagram with VLANs and firewall rules
- Fill in a verification table by hand (simulated results provided)
- Write the same engineer summary and misconfiguration analysis