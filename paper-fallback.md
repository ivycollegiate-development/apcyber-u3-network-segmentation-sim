# U3 L10: Network Segmentation Sim — Paper Fallback
**Unit 3: Securing Networks** | **Period 10 (Fri Nov 27)** | **PAPER DAY (if Codespaces/Chromebooks fail)**

---

## Instructions
Complete this worksheet **instead of** the GitHub lab if the simulator is unavailable. All verification results are **pre-simulated** below — your job is to analyze them, identify the one misconfiguration, and write the engineer summary.

**Name:** ___________________________  
**Date:** ___________________________  
**Submit:** End of class (paper) or photo to Classroom

---

## Part 1: Network Diagram (10 min)

Draw the **target segmented network** based on the requirements. Include:
- 6 VLANs with names, IDs, and CIDRs
- Core switch (L3) with SVIs
- Firewall with trunk port
- All device groups placed in correct VLANs
- Firewall rule flow (use arrows: ALLOW = green, DENY = red)

```
                    INTERNET (WAN)
                         │
                         ▼
                  ┌─────────────┐
                  │  FIREWALL   │ ← Trunk: VLANs 10,20,30,40,50,60
                  │  (L3/L4)    │
                  └──────┬──────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │   DMZ     │  │  STAFF    │  │  GUEST    │
    │  VLAN 30  │  │  VLAN 20  │  │  VLAN 60  │
    │10.10.30/24│  │10.10.20/24│  │10.10.60/24│
    │  Web/Email│  │  20 PCs   │  │  Guest AP │
    └───────────┘  └───────────┘  └───────────┘
          │              │              │
          │              │              │
          ▼              ▼              ▼
    ┌───────────┐  ┌───────────┐
    │ SERVERS   │  │   IOT     │
    │  VLAN 40  │  │  VLAN 50  │
    │10.10.40/24│  │10.10.50/24│
    │ File Srv  │  │ 10 Cams   │
    └───────────┘  └───────────┘
          │
          ▼
    ┌───────────┐
    │   MGMT    │
    │  VLAN 10  │
    │10.10.10/24│
    │ Switch/FW │
    └───────────┘
```

**Your diagram here (or attach separate sheet):**

---

## Part 2: Firewall Rule Design (10 min)

Fill in the **minimal required firewall rules** (source → dest, proto, port, action). Order matters — first match wins.

| # | Source | Dest | Proto | Port | Action | Check ID |
|---|--------|------|-------|------|--------|----------|
| 1 | DMZ | INTERNET | TCP | 80 | ALLOW | FW-001 |
| 2 | DMZ | INTERNET | TCP | 443 | ALLOW | FW-001 |
| 3 | DMZ | INTERNET | TCP | 25 | ALLOW | FW-001 |
| 4 | DMZ | INTERNET | TCP | 587 | ALLOW | FW-001 |
| 5 | DMZ | SERVERS | ANY | ANY | DENY | FW-002 |
| 6 | DMZ | STAFF | ANY | ANY | DENY | FW-002 |
| 7 | DMZ | IOT | ANY | ANY | DENY | FW-002 |
| 8 | DMZ | GUEST | ANY | ANY | DENY | FW-002 |
| 9 | STAFF | DMZ | TCP | 80 | ALLOW | FW-003 |
| 10 | STAFF | DMZ | TCP | 443 | ALLOW | FW-003 |
| 11 | STAFF | SERVERS | TCP | 445 | ALLOW | FW-004 |
| 12 | STAFF | SERVERS | TCP | 2049 | ALLOW | FW-004 |
| 13 | STAFF | IOT | ANY | ANY | DENY | FW-005 |
| 14 | GUEST | STAFF | ANY | ANY | DENY | FW-006 |
| 15 | GUEST | DMZ | ANY | ANY | DENY | FW-006 |
| 16 | GUEST | SERVERS | ANY | ANY | DENY | FW-006 |
| 17 | GUEST | IOT | ANY | ANY | DENY | FW-006 |
| 18 | IOT | INTERNET | ANY | ANY | DENY | **FW-007** |
| 19 | MGMT | STAFF | ANY | ANY | DENY | FW-008 |
| 20 | MGMT | DMZ | ANY | ANY | DENY | FW-008 |
| 21 | MGMT | SERVERS | ANY | ANY | DENY | FW-008 |
| 22 | MGMT | IOT | ANY | ANY | DENY | FW-008 |
| 23 | MGMT | GUEST | ANY | ANY | DENY | FW-008 |
| 24 | MGMT | INTERNET | ANY | ANY | DENY | FW-008 |

**Question:** Why must rule 18 (IOT → INTERNET DENY) be explicit, not just implicit deny?
**Answer:** _________________________________________________________________________
__________________________________________________________________________________

---

## Part 3: Verification Analysis (15 min)

Below are **pre-simulated verification results** from a student run. One check has a **misconfiguration** (the result doesn't match the design). Find it.

| Check ID | Test | Source → Dest | Proto/Port | Simulated Result | PASS/FAIL? |
|----------|------|---------------|------------|------------------|------------|
| VLAN-001 | VLANs created | — | — | 6 VLANs, correct CIDRs | ☐ PASS ☐ FAIL |
| VLAN-002 | Access ports | Staff PCs → VLAN 20 | — | All 20 ports in VLAN 20 | ☐ PASS ☐ FAIL |
| VLAN-002 | Access ports | IoT cams → VLAN 50 | — | All 10 ports in VLAN 50 | ☐ PASS ☐ FAIL |
| VLAN-003 | Trunk port | FW LAN → all VLANs | — | Trunk carries 10,20,30,40,50,60 | ☐ PASS ☐ FAIL |
| ROUTE-001 | Routing enabled | Core switch SVIs | — | All 6 gateway IPs active | ☐ PASS ☐ FAIL |
| FW-001 | DMZ Web → Internet | 10.10.30.10 → 8.8.8.8 | TCP/80 | **Connected** | ☐ PASS ☐ FAIL |
| FW-001 | DMZ Web → Internet | 10.10.30.10 → 8.8.8.8 | TCP/443 | **Connected** | ☐ PASS ☐ FAIL |
| FW-001 | DMZ Email → Internet | 10.10.30.11 → 8.8.8.8 | TCP/25 | **Connected** | ☐ PASS ☐ FAIL |
| FW-001 | DMZ Email → Internet | 10.10.30.11 → 8.8.8.8 | TCP/587 | **Connected** | ☐ PASS ☐ FAIL |
| FW-002 | DMZ → File Server | 10.10.30.10 → 10.10.40.20 | TCP/445 | **Blocked** | ☐ PASS ☐ FAIL |
| FW-002 | DMZ → Staff PC | 10.10.30.10 → 10.10.20.100 | ICMP | **Blocked** | ☐ PASS ☐ FAIL |
| FW-002 | DMZ → IoT Cam | 10.10.30.10 → 10.10.50.200 | ICMP | **Blocked** | ☐ PASS ☐ FAIL |
| FW-002 | DMZ → Guest | 10.10.30.10 → 10.10.60.150 | ICMP | **Blocked** | ☐ PASS ☐ FAIL |
| FW-003 | Staff → DMZ Web | 10.10.20.100 → 10.10.30.10 | TCP/80 | **Connected** | ☐ PASS ☐ FAIL |
| FW-003 | Staff → DMZ Web | 10.10.20.100 → 10.10.30.10 | TCP/443 | **Connected** | ☐ PASS ☐ FAIL |
| FW-004 | Staff → File Srv | 10.10.20.100 → 10.10.40.20 | TCP/445 | **Connected** | ☐ PASS ☐ FAIL |
| FW-004 | Staff → File Srv | 10.10.20.100 → 10.10.40.20 | TCP/2049 | **Connected** | ☐ PASS ☐ FAIL |
| FW-005 | Staff → IoT Cam | 10.10.20.100 → 10.10.50.200 | ICMP | **Blocked** | ☐ PASS ☐ FAIL |
| FW-006 | Guest → Staff | 10.10.60.150 → 10.10.20.100 | ICMP | **Blocked** | ☐ PASS ☐ FAIL |
| FW-006 | Guest → DMZ | 10.10.60.150 → 10.10.30.10 | ICMP | **Blocked** | ☐ PASS ☐ FAIL |
| FW-006 | Guest → File Srv | 10.10.60.150 → 10.10.40.20 | TCP/445 | **Blocked** | ☐ PASS ☐ FAIL |
| FW-006 | Guest → IoT | 10.10.60.150 → 10.10.50.200 | ICMP | **Blocked** | ☐ PASS ☐ FAIL |
| **FW-007** | **IoT → Internet** | **10.10.50.200 → 8.8.8.8** | **TCP/53** | **Connected** ⚠️ | ☐ PASS ☐ **FAIL** |
| FW-008 | MGMT → Staff | 10.10.10.1 → 10.10.20.100 | ICMP | **Blocked** | ☐ PASS ☐ FAIL |
| FW-008 | MGMT → DMZ | 10.10.10.1 → 10.10.30.10 | ICMP | **Blocked** | ☐ PASS ☐ FAIL |
| SAME-VLAN | Staff PC → Staff PC | 10.10.20.100 → 10.10.20.101 | ICMP | **Connected** | ☐ PASS ☐ FAIL |
| SAME-VLAN | IoT Cam → IoT Cam | 10.10.50.200 → 10.10.50.201 | ICMP | **Connected** | ☐ PASS ☐ FAIL |

---

### Find the Misconfiguration

**Which Check ID failed?** _______________ (should be **FW-007**)

**What was the result?** ________________________________________________________

**What rule was missing or wrong?**
______________________________________________________________________________
______________________________________________________________________________

**What command would fix it?**
```
fw_rule _______ _______ _______ _______ _______
```

**Why is this the most critical rule in the entire lab? (Connect to CISA water-system hack)**
______________________________________________________________________________
______________________________________________________________________________
______________________________________________________________________________

---

## Part 4: Engineer Summary (5 min)

Write a **one-paragraph engineer summary** (3–5 sentences) covering:

1. Total verification tests run: _____
2. PASS: _____ | FAIL: _____
3. The one rule that was hardest to get right: _________________________________
4. The misconfiguration you caught: ___________________________________________
5. Why FW-007 is the CISA water-system fix in one sentence: ____________________

**Your summary:**
______________________________________________________________________________
______________________________________________________________________________
______________________________________________________________________________
______________________________________________________________________________

---

## Part 5: Vocab Check

| Term | Definition |
|------|------------|
| VLAN | |
| Access Port | |
| Trunk Port | |
| Native VLAN | |
| SVI (Switch Virtual Interface) | |
| Inter-VLAN Routing | |
| Firewall Rule Evaluation Order | |
| Implicit Deny | |
| DMZ | |
| Out-of-Band Management | |

---

## Teacher Key — Paper Fallback

### Part 2 Question Answer
Rule 18 must be explicit because **implicit deny only applies after all rules are evaluated**. If a broader ALLOW rule exists earlier (e.g., `STAFF → INTERNET ALLOW` and IoT is accidentally in STAFF VLAN), the implicit deny never triggers. Explicit DENY at the correct priority guarantees the block regardless of rule order changes.

### Part 3 Misconfiguration
- **Failed Check:** FW-007
- **Result:** IoT camera (10.10.50.200) → Internet (8.8.8.8) TCP/53 = **Connected** (should be Blocked)
- **Root Cause:** Missing firewall rule `fw_rule IOT INTERNET any any deny` (Rule 18 not added)
- **Fix Command:** `fw_rule IOT INTERNET any any deny`
- **Criticality:** This is the **exact CISA fix** from the Aug 2026 water-system hack — internet-connected OT/IoT devices were the attack vector. Blocking IoT → Internet prevents command-and-control, firmware update hijacking, and data exfiltration from cameras/sensors.

### Part 4 Sample Summary
> "Ran 28 verification tests: 27 PASS, 1 FAIL. The hardest rule was FW-007 (IOT → INTERNET DENY) because it's easy to forget in a long rule list and the simulator's implicit deny doesn't protect against misordered rules. I caught that the IoT → Internet rule was missing entirely — the camera could reach 8.8.8.8 on port 53. Added `fw_rule IOT INTERNET any any deny` and retested: BLOCKED. This rule is the direct implementation of the CISA fix for the Iran-linked water-system hacks: unplug OT/IoT from the internet."

---

## Submission Checklist

- [ ] Part 1: Network diagram drawn
- [ ] Part 2: Firewall rule table complete + question answered
- [ ] Part 3: Misconfiguration identified (FW-007) + fix command written
- [ ] Part 4: Engineer summary written (3–5 sentences)
- [ ] Part 5: Vocab definitions filled
- [ ] Name and date on paper
- [ ] Submitted to teacher / photo uploaded to Classroom