#!/usr/bin/env python3
"""
Network Segmentation Simulator — AP Cyber U3 L10
Simulates VLAN creation, port assignment, trunking, routing, firewall rules, and verification.
Log every command and verification to segmentation_log.csv.
"""

import csv
import sys
import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

# ===================== DATA MODELS =====================

class Action(Enum):
    ALLOW = "allow"
    DENY = "deny"

class Protocol(Enum):
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ANY = "any"

@dataclass
class VLAN:
    vid: int
    name: str
    cidr: str
    gateway_ip: str = ""
    access_ports: List[str] = field(default_factory=list)

@dataclass
class TrunkPort:
    port: str
    allowed_vlans: List[int] = field(default_factory=list)

@dataclass
class FirewallRule:
    src: str      # VLAN name or "INTERNET"
    dst: str      # VLAN name or "INTERNET"
    proto: Protocol
    port: str     # port number or "any"
    action: Action
    rule_id: int = 0

@dataclass
class Device:
    name: str
    ip: str
    vlan_name: str
    port: str = ""
    target_ip: str = ""  # Desired IP in segmented network

@dataclass
class LogEntry:
    timestamp: str
    phase: str
    command: str
    check_id: str
    test_type: str      # "config", "verify_ping", "verify_port", "verify_trunk", "verify_routing"
    source: str
    destination: str
    protocol: str
    port: str
    expected: str       # "PASS" or "FAIL"
    actual: str         # "PASS" or "FAIL" or "ERROR"
    notes: str = ""

# ===================== SIMULATOR STATE =====================

class NetworkSimulator:
    def __init__(self):
        self.vlans: Dict[int, VLAN] = {}
        self.vlan_by_name: Dict[str, VLAN] = {}
        self.trunks: Dict[str, TrunkPort] = {}
        self.fw_rules: List[FirewallRule] = []
        self.rule_counter = 0
        self.routing_enabled = False
        self.devices: List[Device] = []
        self.log: List[LogEntry] = []
        self.phase = "setup"
        self._init_flat_network()

    def _init_flat_network(self):
        """Initialize the flat /24 network (pre-segmentation state)."""
        # All devices in 10.10.10.0/24
        self.devices = [
            Device("core_switch", "10.10.10.1", "FLAT", "eth0", "10.10.10.1"),
            Device("firewall_wan", "10.10.10.254", "FLAT", "eth_wan", "10.10.10.254"),
            Device("firewall_lan", "10.10.10.2", "FLAT", "eth_fw_lan", "10.10.10.2"),
            Device("web_server", "10.10.10.10", "FLAT", "eth_web", "10.10.30.10"),
            Device("email_server", "10.10.10.11", "FLAT", "eth_email", "10.10.30.11"),
            Device("file_server", "10.10.10.20", "FLAT", "eth_files", "10.10.40.20"),
            *[Device(f"pc{i}", f"10.10.10.{100+i}", "FLAT", f"eth{i}", f"10.10.20.{100+i}") for i in range(1, 21)],
            *[Device(f"cam{i}", f"10.10.10.{200+i}", "FLAT", f"eth_cam{i}", f"10.10.50.{200+i}") for i in range(1, 11)],
            *[Device(f"guest{i}", f"10.10.10.{150+i}", "FLAT", f"eth_guest{i}", f"10.10.60.{150+i}") for i in range(1, 21)],
        ]

    def _log(self, phase: str, command: str, check_id: str, test_type: str,
             source: str, destination: str, protocol: str, port: str,
             expected: str, actual: str, notes: str = ""):
        entry = LogEntry(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            phase=phase, command=command, check_id=check_id, test_type=test_type,
            source=source, destination=destination, protocol=protocol, port=port,
            expected=expected, actual=actual, notes=notes
        )
        self.log.append(entry)

    # ===================== COMMANDS =====================

    def cmd_help(self):
        print("""
Network Segmentation Simulator — Commands
=========================================
  help                          Show this help
  status                        Show current network state
  create_vlan <id> <name> <cidr>    Create VLAN (e.g., create_vlan 20 STAFF 10.10.20.0/24)
  assign_access <port> <vlan_id>    Assign access port to VLAN
  assign_trunk <port> <vlan_ids>    Assign trunk port with comma-separated VLAN IDs
  enable_routing                  Enable inter-VLAN routing (creates SVIs)
  fw_rule <src> <dst> <proto> <port> <action>
                                  Add firewall rule (e.g., fw_rule STAFF DMZ tcp 80 allow)
  verify_ping <src_ip> <dst_ip>   Test ICMP connectivity
  verify_port <src_ip> <dst_ip> <port>  Test TCP/UDP port connectivity
  save_log                        Write segmentation_log.csv
  exit                            Quit (auto-saves log)

VLAN Names: MGMT, STAFF, DMZ, SERVERS, IOT, GUEST, INTERNET
Protocols: tcp, udp, icmp, any
Actions: allow, deny
""")

    def cmd_status(self):
        print("\n=== NETWORK STATUS ===")
        print(f"Routing enabled: {self.routing_enabled}")
        print(f"\nVLANs ({len(self.vlans)}):")
        for vlan in sorted(self.vlans.values(), key=lambda v: v.vid):
            gw = vlan.gateway_ip or "—"
            print(f"  VLAN {vlan.vid:2d}  {vlan.name:8s}  {vlan.cidr:18s}  GW: {gw}  Ports: {vlan.access_ports}")
        if not self.vlans:
            print("  (none — flat network)")

        print(f"\nTrunk Ports ({len(self.trunks)}):")
        for trunk in self.trunks.values():
            vlans = ",".join(str(v) for v in trunk.allowed_vlans)
            print(f"  {trunk.port:12s}  VLANs: [{vlans}]")
        if not self.trunks:
            print("  (none)")

        print(f"\nFirewall Rules ({len(self.fw_rules)}):")
        for rule in self.fw_rules:
            proto = rule.proto.value.upper()
            port = rule.port
            print(f"  [{rule.rule_id:2d}] {rule.src:8s} → {rule.dst:8s}  {proto:4s}  {port:>5s}  {rule.action.value.upper()}")
        if not self.fw_rules:
            print("  (none — implicit deny all)")

        print(f"\nDevices ({len(self.devices)}):")
        for dev in self.devices:
            print(f"  {dev.name:15s}  {dev.ip:15s}  VLAN: {dev.vlan_name:8s}  Port: {dev.port}")

    def cmd_create_vlan(self, args: List[str]):
        if len(args) != 3:
            print("Usage: create_vlan <id> <name> <cidr>")
            return
        try:
            vid = int(args[0])
            name = args[1].upper()
            cidr = args[2]
        except ValueError:
            print("Error: VLAN ID must be integer")
            return

        if vid in self.vlans:
            print(f"Error: VLAN {vid} already exists")
            return
        if name in self.vlan_by_name:
            print(f"Error: VLAN name {name} already exists")
            return

        # Calculate gateway IP (first usable in CIDR)
        import ipaddress
        net = ipaddress.IPv4Network(cidr, strict=False)
        gateway = str(net.network_address + 1)

        vlan = VLAN(vid=vid, name=name, cidr=cidr, gateway_ip=gateway)
        self.vlans[vid] = vlan
        self.vlan_by_name[name] = vlan
        self._log(self.phase, f"create_vlan {vid} {name} {cidr}", "VLAN-001", "config",
                  "simulator", f"VLAN {vid}", "any", "any", "PASS", "PASS",
                  f"Created VLAN {vid} ({name}) {cidr} GW={gateway}")
        print(f"Created VLAN {vid}: {name} {cidr} (gateway {gateway})")

    def cmd_assign_access(self, args: List[str]):
        if len(args) != 2:
            print("Usage: assign_access <port> <vlan_id>")
            return
        port = args[0]
        try:
            vid = int(args[1])
        except ValueError:
            print("Error: VLAN ID must be integer")
            return

        if vid not in self.vlans:
            print(f"Error: VLAN {vid} does not exist")
            return

        vlan = self.vlans[vid]
        if port in vlan.access_ports:
            print(f"Port {port} already in VLAN {vid}")
            return

        # Remove from any other VLAN
        for v in self.vlans.values():
            if port in v.access_ports:
                v.access_ports.remove(port)

        vlan.access_ports.append(port)
        # Update device VLAN assignment
        for dev in self.devices:
            if dev.port == port:
                dev.vlan_name = vlan.name
                # Use target_ip if set (for predefined devices), otherwise auto-assign
                if dev.target_ip:
                    dev.ip = dev.target_ip
                else:
                    import ipaddress
                    net = ipaddress.IPv4Network(vlan.cidr, strict=False)
                    idx = vlan.access_ports.index(port)
                    dev.ip = str(net.network_address + 2 + idx)
                break

        self._log(self.phase, f"assign_access {port} {vid}", "VLAN-002", "config",
                  "simulator", f"Port {port}", "any", "any", "PASS", "PASS",
                  f"Assigned port {port} to VLAN {vid} ({vlan.name})")
        print(f"Assigned port {port} to VLAN {vid} ({vlan.name})")

    def cmd_assign_trunk(self, args: List[str]):
        if len(args) != 2:
            print("Usage: assign_trunk <port> <vlan_ids_comma_separated>")
            return
        port = args[0]
        try:
            vlan_ids = [int(x.strip()) for x in args[1].split(",")]
        except ValueError:
            print("Error: VLAN IDs must be comma-separated integers")
            return

        for vid in vlan_ids:
            if vid not in self.vlans:
                print(f"Error: VLAN {vid} does not exist")
                return

        trunk = TrunkPort(port=port, allowed_vlans=vlan_ids)
        self.trunks[port] = trunk
        self._log(self.phase, f"assign_trunk {port} {vlan_ids}", "VLAN-003", "config",
                  "simulator", f"Trunk {port}", "any", "any", "PASS", "PASS",
                  f"Configured trunk {port} with VLANs {vlan_ids}")
        print(f"Configured trunk {port} with VLANs {vlan_ids}")

    def cmd_enable_routing(self):
        if self.routing_enabled:
            print("Routing already enabled")
            return
        self.routing_enabled = True
        # Create SVI IPs for each VLAN (already in VLAN.gateway_ip)
        self._log(self.phase, "enable_routing", "ROUTE-001", "config",
                  "core_switch", "all VLANs", "any", "any", "PASS", "PASS",
                  "Enabled inter-VLAN routing; SVIs created for all VLANs")
        print("Inter-VLAN routing enabled. SVIs active on all VLAN gateways.")

    def cmd_fw_rule(self, args: List[str]):
        if len(args) != 5:
            print("Usage: fw_rule <src_vlan> <dst_vlan> <proto> <port> <action>")
            return
        src, dst, proto_str, port_str, action_str = args
        src = src.upper()
        dst = dst.upper()

        # Validate VLAN names
        valid_vlans = set(self.vlan_by_name.keys()) | {"INTERNET"}
        if src not in valid_vlans:
            print(f"Error: Unknown source VLAN '{src}'. Valid: {', '.join(sorted(valid_vlans))}")
            return
        if dst not in valid_vlans:
            print(f"Error: Unknown dest VLAN '{dst}'. Valid: {', '.join(sorted(valid_vlans))}")
            return

        try:
            proto = Protocol(proto_str.lower())
        except ValueError:
            print(f"Error: Invalid protocol '{proto_str}'. Use: tcp, udp, icmp, any")
            return

        if port_str != "any":
            try:
                int(port_str)
            except ValueError:
                print("Error: Port must be integer or 'any'")
                return

        try:
            action = Action(action_str.lower())
        except ValueError:
            print(f"Error: Invalid action '{action_str}'. Use: allow, deny")
            return

        self.rule_counter += 1
        rule = FirewallRule(src=src, dst=dst, proto=proto, port=port_str, action=action, rule_id=self.rule_counter)
        self.fw_rules.append(rule)
        self._log(self.phase, f"fw_rule {src} {dst} {proto_str} {port_str} {action_str}",
                  f"FW-{self.rule_counter:03d}", "config", src, dst, proto_str, port_str,
                  "PASS", "PASS", f"Added firewall rule #{self.rule_counter}")
        print(f"Added firewall rule #{self.rule_counter}: {src} → {dst} {proto_str} {port_str} {action_str}")

    def _check_firewall(self, src_ip: str, dst_ip: str, proto: Protocol, port: str) -> Tuple[bool, str]:
        """Check if traffic is allowed by firewall. Returns (allowed, matched_rule_description)."""
        # Find source and destination VLANs
        src_vlan = None
        dst_vlan = None
        for dev in self.devices:
            if dev.ip == src_ip:
                src_vlan = dev.vlan_name
            if dev.ip == dst_ip:
                dst_vlan = dev.vlan_name
        # Check if dst is Internet (simulated as 8.8.8.8 or similar)
        if dst_ip.startswith("8.8.8.") or dst_ip.startswith("1.1.1."):
            dst_vlan = "INTERNET"
        if src_ip.startswith("8.8.8.") or src_ip.startswith("1.1.1."):
            src_vlan = "INTERNET"

        if not src_vlan or not dst_vlan:
            return False, "Unknown VLAN for source or destination"

        # First-match firewall evaluation
        for rule in self.fw_rules:
            src_match = (rule.src == src_vlan) or (rule.src == "any")
            dst_match = (rule.dst == dst_vlan) or (rule.dst == "any")
            proto_match = (rule.proto == proto) or (rule.proto == Protocol.ANY)
            port_match = (rule.port == port) or (rule.port == "any")

            if src_match and dst_match and proto_match and port_match:
                allowed = (rule.action == Action.ALLOW)
                desc = f"Rule #{rule.rule_id}: {rule.src}→{rule.dst} {rule.proto.value} {rule.port} {rule.action.value}"
                return allowed, desc

        # Implicit deny
        return False, "Implicit deny (no matching rule)"

    def _simulate_connectivity(self, src_ip: str, dst_ip: str, proto: Protocol, port: str) -> Tuple[bool, str]:
        """Simulate connectivity check. Returns (success, reason)."""
        # Same VLAN = always allowed (Layer 2)
        src_vlan = None
        dst_vlan = None
        for dev in self.devices:
            if dev.ip == src_ip:
                src_vlan = dev.vlan_name
            if dev.ip == dst_ip:
                dst_vlan = dev.vlan_name
        if dst_ip.startswith("8.8.8.") or dst_ip.startswith("1.1.1."):
            dst_vlan = "INTERNET"
        if src_ip.startswith("8.8.8.") or src_ip.startswith("1.1.1."):
            src_vlan = "INTERNET"

        if src_vlan and dst_vlan and src_vlan == dst_vlan and src_vlan != "INTERNET":
            return True, "Same VLAN (Layer 2)"

        # Cross-VLAN requires routing enabled
        if not self.routing_enabled:
            return False, "Inter-VLAN routing not enabled"

        # Firewall check
        allowed, rule_desc = self._check_firewall(src_ip, dst_ip, proto, port)
        if not allowed:
            return False, f"Blocked by firewall: {rule_desc}"
        return True, f"Allowed by firewall: {rule_desc}"

    def cmd_verify_ping(self, args: List[str]):
        if len(args) != 2:
            print("Usage: verify_ping <src_ip> <dst_ip>")
            return
        src_ip, dst_ip = args
        success, reason = self._simulate_connectivity(src_ip, dst_ip, Protocol.ICMP, "any")
        result = "PASS" if success else "FAIL"
        expected = "PASS"  # We'll determine expected from check_id context
        self._log(self.phase, f"verify_ping {src_ip} {dst_ip}", "VERIFY", "verify_ping",
                  src_ip, dst_ip, "icmp", "any", expected, result, reason)
        print(f"PING {src_ip} → {dst_ip} : {result} ({reason})")

    def cmd_verify_port(self, args: List[str]):
        if len(args) != 3:
            print("Usage: verify_port <src_ip> <dst_ip> <port>")
            return
        src_ip, dst_ip, port_str = args
        try:
            port = int(port_str)
        except ValueError:
            print("Error: Port must be integer")
            return
        success, reason = self._simulate_connectivity(src_ip, dst_ip, Protocol.TCP, port_str)
        result = "PASS" if success else "FAIL"
        expected = "PASS"
        self._log(self.phase, f"verify_port {src_ip} {dst_ip} {port}", "VERIFY", "verify_port",
                  src_ip, dst_ip, "tcp", port_str, expected, result, reason)
        print(f"PORT {src_ip} → {dst_ip}:{port} : {result} ({reason})")

    def cmd_save_log(self):
        filename = "segmentation_log.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "phase", "command", "check_id", "test_type",
                "source", "destination", "protocol", "port",
                "expected", "actual", "notes"
            ])
            for entry in self.log:
                writer.writerow([
                    entry.timestamp, entry.phase, entry.command, entry.check_id,
                    entry.test_type, entry.source, entry.destination,
                    entry.protocol, entry.port, entry.expected, entry.actual, entry.notes
                ])
        print(f"Log saved to {filename} ({len(self.log)} entries)")

    def run_command(self, line: str):
        line = line.strip()
        if not line:
            return
        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "help":
            self.cmd_help()
        elif cmd == "status":
            self.cmd_status()
        elif cmd == "create_vlan":
            self.cmd_create_vlan(args)
        elif cmd == "assign_access":
            self.cmd_assign_access(args)
        elif cmd == "assign_trunk":
            self.cmd_assign_trunk(args)
        elif cmd == "enable_routing":
            self.cmd_enable_routing()
        elif cmd == "fw_rule":
            self.cmd_fw_rule(args)
        elif cmd == "verify_ping":
            self.cmd_verify_ping(args)
        elif cmd == "verify_port":
            self.cmd_verify_port(args)
        elif cmd == "save_log":
            self.cmd_save_log()
        elif cmd == "exit":
            self.cmd_save_log()
            print("Exiting. Log auto-saved.")
            sys.exit(0)
        else:
            print(f"Unknown command: {cmd}. Type 'help' for commands.")

    def repl(self):
        print("Network Segmentation Simulator — AP Cyber U3 L10")
        print("Type 'help' for commands. Type 'exit' to quit and save log.")
        print("Starting in FLAT network mode (all devices in 10.10.10.0/24).")
        print()
        while True:
            try:
                line = input("> ")
                self.run_command(line)
            except (EOFError, KeyboardInterrupt):
                self.cmd_save_log()
                print("\nExiting. Log auto-saved.")
                break

def main():
    sim = NetworkSimulator()
    sim.repl()

if __name__ == "__main__":
    main()