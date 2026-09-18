#!/usr/bin/env python3
"""Knowledge-graph and harness validator for Foxglove DOOM.

Two modes:

    python3 .agent/knowledge-graph/validate.py
        Graph gate. Validates nodes.jsonl and edges.jsonl: every line parses as
        one JSON object, no blank lines, file ends with a newline, no wrapping
        array, required fields present, node ids unique, node types drawn from
        the eight, edge types drawn from the six, every edge endpoint resolves,
        every status value is legal for its node type, and every Workstream
        source is a directory on disk.

    python3 .agent/knowledge-graph/validate.py --harness
        Harness self-check. Runs the graph gate and additionally checks the
        file tree, ContractItem coverage for H-nn items, required edges, and
        progress.md / log.md formats.

Paths may be overridden so a mutated copy can be checked:

    python3 .agent/knowledge-graph/validate.py --nodes /tmp/bad-nodes.jsonl

Exit code is 0 only when every check passes; every failure is printed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

NODE_TYPES = {
    "Decision",
    "Workstream",
    "ContractItem",
    "Repo",
    "Hardware",
    "Capability",
    "Risk",
    "Event",
}

EDGE_TYPES = {
    "DECIDES",
    "DEPENDS_ON",
    "EVIDENCED_BY",
    "BLOCKS",
    "IMPLEMENTS",
    "SUPERSEDES",
}

NODE_REQUIRED = ("id", "type", "label", "body", "status", "ts", "source")
EDGE_REQUIRED = ("from", "type", "to", "ts")

STATUS_VOCAB = {
    "Decision": {"locked", "superseded"},
    "Workstream": {"planned", "in_progress", "done", "deferred"},
    "Capability": {"planned", "in_progress", "done", "deferred"},
    "ContractItem": {"specified", "implemented", "verified", "failed"},
    "Repo": {"pinned", "vendored", "referenced", "deferred"},
    "Hardware": {"present", "absent", "not_acquired"},
    "Risk": {"open", "mitigated", "closed"},
    "Event": {"scheduled", "past"},
}

NODE_OPTIONAL = {"url", "date", "date_end"}

ALLOWED_PAIRS = {
    "DECIDES": {
        ("Decision", "Workstream"),
        ("Decision", "Capability"),
        ("Decision", "Event"),
    },
    "DEPENDS_ON": {
        ("Workstream", "Workstream"),
        ("Capability", "Capability"),
        ("Event", "Capability"),
        ("Workstream", "Capability"),
        ("Capability", "Hardware"),
    },
    "EVIDENCED_BY": {
        ("Decision", "Repo"),
        ("Decision", "Event"),
        ("Risk", "Repo"),
        ("Risk", "Hardware"),
        ("ContractItem", "Repo"),
    },
    "BLOCKS": {
        ("Risk", "Workstream"),
        ("Risk", "Capability"),
        ("Risk", "Hardware"),
        ("Hardware", "Capability"),
    },
    "IMPLEMENTS": {
        ("Workstream", "Capability"),
        ("ContractItem", "Workstream"),
    },
    "SUPERSEDES": {
        ("Decision", "Decision"),
        ("Workstream", "Workstream"),
    },
}

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LOG_HEADING = re.compile(r"^## \[(\d{4}-\d{2}-\d{2})\] [a-z-]+ \| .+$")
NODE_ID = re.compile(r"[a-z0-9_]+|[A-Z]{1,3}-\d{2}")

WORKSTREAMS = (
    "00-harness",
    "01-hero-loop",
    "02-robotics-layout",
    "03-embed-shell",
    "04-record-replay",
    "05-stunt-extras",
)

PROGRESS_KEYS = ("status", "owner", "updated", "next action", "blockers")
PROGRESS_STATUS = {
    "planning",
    "planning complete",
    "amended",
    "awaiting generator",
    "in progress",
    "blocked",
    "done",
    "deferred",
}

REQUIRED_EDGES = [
    ("dec_vizdoom_engine", "DECIDES", "ws_01_hero_loop"),
    ("dec_foxglove_sdk_ws", "DECIDES", "cap_live_ws_camera_teleop"),
    ("dec_freedoom_legal", "DECIDES", "ws_01_hero_loop"),
    ("dec_teleop_twist", "DECIDES", "ws_01_hero_loop"),
    ("dec_embed_viz", "DECIDES", "ws_03_embed_shell"),
    ("dec_no_canvas", "DECIDES", "ws_01_hero_loop"),
    ("dec_phase_gating", "DECIDES", "ws_05_stunt_extras"),
    ("dec_state_on_disk", "DECIDES", "ws_00_harness"),
    ("ws_01_hero_loop", "DEPENDS_ON", "ws_00_harness"),
    ("ws_02_robotics_layout", "DEPENDS_ON", "ws_01_hero_loop"),
    ("ws_03_embed_shell", "DEPENDS_ON", "ws_02_robotics_layout"),
    ("ws_04_record_replay", "DEPENDS_ON", "ws_03_embed_shell"),
    ("ws_05_stunt_extras", "DEPENDS_ON", "ws_03_embed_shell"),
    ("cap_3d_map_hud", "DEPENDS_ON", "cap_live_ws_camera_teleop"),
    ("cap_embed_page", "DEPENDS_ON", "cap_3d_map_hud"),
    ("cap_mcap_replay", "DEPENDS_ON", "cap_embed_page"),
    ("dec_foxglove_sdk_ws", "EVIDENCED_BY", "repo_foxglove_sdk"),
    ("dec_vizdoom_engine", "EVIDENCED_BY", "repo_vizdoom"),
    ("dec_freedoom_legal", "EVIDENCED_BY", "repo_freedoom"),
    ("vizdoom_macos_build", "BLOCKS", "ws_01_hero_loop"),
    ("ws_01_hero_loop", "IMPLEMENTS", "cap_live_ws_camera_teleop"),
    ("ws_02_robotics_layout", "IMPLEMENTS", "cap_3d_map_hud"),
    ("ws_03_embed_shell", "IMPLEMENTS", "cap_embed_page"),
    ("ws_04_record_replay", "IMPLEMENTS", "cap_mcap_replay"),
    ("ws_05_stunt_extras", "IMPLEMENTS", "cap_stunt_extras"),
]


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.checks = 0

    def check(self, ok: bool, message: str) -> bool:
        self.checks += 1
        if not ok:
            self.failures.append(message)
        return ok

    def fail(self, message: str) -> None:
        self.checks += 1
        self.failures.append(message)


def read_jsonl(path: str, report: Report) -> list[dict]:
    if not os.path.isfile(path):
        report.fail("%s: file is missing" % path)
        return []
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    if raw == "":
        report.fail("%s: file is empty" % path)
        return []
    report.check(raw.endswith("\n"), "%s: file does not end with a newline" % path)
    report.check(
        not raw.lstrip().startswith("["),
        "%s: starts with '[' — JSONL must not be a wrapping array" % path,
    )
    records = []
    for lineno, line in enumerate(raw.split("\n")[:-1], start=1):
        if line.strip() == "":
            report.fail("%s:%d: blank line is not allowed in JSONL" % (path, lineno))
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            report.fail("%s:%d: line does not parse as JSON (%s)" % (path, lineno, exc))
            continue
        if not isinstance(obj, dict):
            report.fail("%s:%d: line is not a JSON object" % (path, lineno))
            continue
        obj["__line__"] = lineno
        records.append(obj)
    return records


def validate_graph(nodes_path: str, edges_path: str, report: Report) -> None:
    nodes = read_jsonl(nodes_path, report)
    edges = read_jsonl(edges_path, report)

    ids: dict[str, int] = {}
    node_types: dict[str, str] = {}
    for node in nodes:
        lineno = node["__line__"]
        where = "%s:%d" % (nodes_path, lineno)
        missing = [f for f in NODE_REQUIRED if f not in node]
        if missing:
            report.fail("%s: node missing required field(s) %s" % (where, missing))
            continue
        node_id = node["id"]
        if node_id in ids:
            report.fail(
                "%s: duplicate node id %r (first seen on line %d)"
                % (where, node_id, ids[node_id])
            )
        else:
            ids[node_id] = lineno
        if not report.check(
            node["type"] in NODE_TYPES,
            "%s: node %r has unknown type %r" % (where, node_id, node["type"]),
        ):
            continue
        node_types[node_id] = node["type"]
        report.check(
            NODE_ID.fullmatch(str(node_id)) is not None,
            "%s: node id %r is not snake_case or [A-Z]{1,3}-nn" % (where, node_id),
        )
        report.check(
            node["status"] in STATUS_VOCAB[node["type"]],
            "%s: node %r status %r is not legal for type %s (allowed: %s)"
            % (
                where,
                node_id,
                node["status"],
                node["type"],
                sorted(STATUS_VOCAB[node["type"]]),
            ),
        )
        report.check(
            ISO_DATE.fullmatch(str(node["ts"])) is not None,
            "%s: node %r ts %r is not an ISO date" % (where, node_id, node["ts"]),
        )
        report.check(
            isinstance(node["body"], str) and len(node["body"].strip()) > 0,
            "%s: node %r has an empty body" % (where, node_id),
        )
        report.check(
            isinstance(node["label"], str) and len(node["label"].strip()) > 0,
            "%s: node %r has an empty label" % (where, node_id),
        )
        unknown = set(node) - set(NODE_REQUIRED) - NODE_OPTIONAL - {"__line__"}
        report.check(
            not unknown,
            "%s: node %r carries undocumented field(s) %s" % (where, node_id, sorted(unknown)),
        )
        if node["type"] == "Workstream":
            report.check(
                os.path.isdir(node["source"]),
                "%s: Workstream %r source %r is not a directory on disk"
                % (where, node_id, node["source"]),
            )

    for edge in edges:
        where = "%s:%d" % (edges_path, edge["__line__"])
        missing = [f for f in EDGE_REQUIRED if f not in edge]
        if missing:
            report.fail("%s: edge missing required field(s) %s" % (where, missing))
            continue
        report.check(
            edge["type"] in EDGE_TYPES,
            "%s: edge has unknown type %r" % (where, edge["type"]),
        )
        report.check(
            edge["from"] in ids,
            "%s: edge 'from' %r does not resolve to a node id" % (where, edge["from"]),
        )
        report.check(
            edge["to"] in ids,
            "%s: edge 'to' %r does not resolve to a node id" % (where, edge["to"]),
        )
        report.check(
            ISO_DATE.fullmatch(str(edge["ts"])) is not None,
            "%s: edge ts %r is not an ISO date" % (where, edge["ts"]),
        )
        unknown = set(edge) - set(EDGE_REQUIRED) - {"note", "__line__"}
        report.check(
            not unknown,
            "%s: edge carries undocumented field(s) %s" % (where, sorted(unknown)),
        )
        if edge["type"] in ALLOWED_PAIRS and edge["from"] in ids and edge["to"] in ids:
            pair = (node_types[edge["from"]], node_types[edge["to"]])
            report.check(
                pair in ALLOWED_PAIRS[edge["type"]],
                "%s: edge %s --%s--> %s uses direction pair %s -> %s, which SCHEMA.md does not allow"
                % (where, edge["from"], edge["type"], edge["to"], pair[0], pair[1]),
            )

    if nodes and edges:
        print(
            "graph: %d nodes, %d edges, %d distinct node types, %d distinct edge types"
            % (
                len(nodes),
                len(edges),
                len({n["type"] for n in nodes if "type" in n}),
                len({e["type"] for e in edges if "type" in e}),
            )
        )


def expected_tree() -> list[str]:
    paths = [
        ".agent/GOAL.md",
        ".agent/COORDINATION.md",
        ".agent/knowledge-graph/SCHEMA.md",
        ".agent/knowledge-graph/nodes.jsonl",
        ".agent/knowledge-graph/edges.jsonl",
        ".agent/knowledge-graph/validate.py",
        ".agent/loops/README.md",
        ".agent/workstreams/00-harness/critique.md",
        ".cursor/rules/agent-os.mdc",
    ]
    for ws in WORKSTREAMS:
        for name in ("contract.md", "progress.md", "log.md"):
            paths.append(".agent/workstreams/%s/%s" % (ws, name))
    for ws in WORKSTREAMS[1:]:
        paths.append(".agent/workstreams/%s/PLAN.md" % ws)
    return sorted(set(paths))


def validate_harness(report: Report) -> None:
    for path in expected_tree():
        report.check(os.path.isfile(path), "H-01: missing required path %s" % path)

    loops = ".agent/loops/README.md"
    if os.path.isfile(loops):
        with open(loops, encoding="utf-8") as fh:
            loops_text = fh.read().lower()
        report.check(
            "eval-after-generator" in loops_text or "eval after generator" in loops_text,
            "H-19: loops/README.md does not specify the eval-after-generator loop",
        )
        report.check(
            "knowledge-graph sync" in loops_text or "kg sync" in loops_text,
            "H-19: loops/README.md does not specify the knowledge-graph sync loop",
        )
        report.check(
            "no event deadline" in loops_text or "there is no event deadline" in loops_text,
            "H-19: loops/README.md must state that there is no event deadline loop",
        )

    rule = ".cursor/rules/agent-os.mdc"
    if os.path.isfile(rule):
        with open(rule, encoding="utf-8") as fh:
            rule_text = fh.read()
        report.check(
            "alwaysApply: true" in rule_text,
            "H-20: .cursor/rules/agent-os.mdc is missing alwaysApply: true",
        )
        report.check(
            "cursor-grok-4.6-high-fast" in rule_text and "kimi-k3-high" in rule_text,
            "H-20: .cursor/rules/agent-os.mdc must name both allowed model slugs",
        )

    harness_contract = ".agent/workstreams/00-harness/contract.md"
    if os.path.isfile(harness_contract):
        with open(harness_contract, encoding="utf-8") as fh:
            headings = re.findall(r"^### (H-\d{2}) ", fh.read(), flags=re.M)
        nodes = [
            json.loads(line)
            for line in open(".agent/knowledge-graph/nodes.jsonl", encoding="utf-8")
        ]
        item_ids = {n["id"] for n in nodes if n.get("type") == "ContractItem"}
        missing = sorted(set(headings) - item_ids)
        extra = sorted(i for i in item_ids - set(headings) if re.fullmatch(r"H-\d{2}", i))
        report.check(not missing, "H-12: contract headings without a ContractItem node: %s" % missing)
        report.check(not extra, "H-12: ContractItem nodes without a contract heading: %s" % extra)

        edges = [
            json.loads(line)
            for line in open(".agent/knowledge-graph/edges.jsonl", encoding="utf-8")
        ]
        triples = {(e.get("from"), e.get("type"), e.get("to")) for e in edges}
        for item in headings:
            report.check(
                (item, "IMPLEMENTS", "ws_00_harness") in triples,
                "H-12: %s has no IMPLEMENTS edge to ws_00_harness" % item,
            )
        for triple in REQUIRED_EDGES:
            report.check(
                triple in triples,
                "H-13: required edge missing: %s --%s--> %s" % triple,
            )

    for ws in WORKSTREAMS:
        progress = ".agent/workstreams/%s/progress.md" % ws
        if os.path.isfile(progress):
            with open(progress, encoding="utf-8") as fh:
                text = fh.read()
            header = {}
            for line in text.split("\n"):
                if line.strip() == "":
                    break
                if ":" in line:
                    key, _, value = line.partition(":")
                    header[key.strip().lower()] = value.strip()
            for key in PROGRESS_KEYS:
                report.check(key in header, "H-17: %s: header is missing %r" % (progress, key))
            if "status" in header:
                report.check(
                    header["status"] in PROGRESS_STATUS,
                    "H-17: %s: status %r is outside the allowed vocabulary"
                    % (progress, header["status"]),
                )
            if "updated" in header:
                report.check(
                    ISO_DATE.fullmatch(header["updated"]) is not None,
                    "H-17: %s: updated %r is not an ISO date" % (progress, header["updated"]),
                )
            if "blockers" in header:
                blockers = header["blockers"]
                if blockers.lower() != "none":
                    risk_ids = {
                        json.loads(line)["id"]
                        for line in open(".agent/knowledge-graph/nodes.jsonl", encoding="utf-8")
                        if json.loads(line).get("type") == "Risk"
                    }
                    for token in re.split(r"[,\s]+", blockers):
                        token = token.strip("`,. ")
                        if token:
                            report.check(
                                token in risk_ids,
                                "H-17: %s: blocker %r is not a Risk node id" % (progress, token),
                            )

        log = ".agent/workstreams/%s/log.md" % ws
        if os.path.isfile(log):
            with open(log, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            report.check(
                any("append-only" in line.lower() for line in lines[:8]),
                "H-18: %s: no append-only notice near the top" % log,
            )
            dates = []
            for lineno, line in enumerate(lines, start=1):
                if line.startswith("## ") and not line.startswith("### "):
                    match = LOG_HEADING.fullmatch(line)
                    if not report.check(
                        match is not None,
                        "H-18: %s:%d: heading does not match '## [YYYY-MM-DD] op | title': %r"
                        % (log, lineno, line),
                    ):
                        continue
                    dates.append(match.group(1))
            report.check(
                dates == sorted(dates),
                "H-18: %s: entry dates are not non-decreasing: %s" % (log, dates),
            )
            report.check(bool(dates), "H-18: %s: contains no log entries" % log)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodes", default=".agent/knowledge-graph/nodes.jsonl")
    parser.add_argument("--edges", default=".agent/knowledge-graph/edges.jsonl")
    parser.add_argument(
        "--harness",
        action="store_true",
        help="also run the file-tree / H-nn / progress / log harness checks",
    )
    args = parser.parse_args()

    report = Report()
    validate_graph(args.nodes, args.edges, report)
    if args.harness:
        validate_harness(report)

    if report.failures:
        print("FAIL: %d of %d checks failed" % (len(report.failures), report.checks))
        for failure in report.failures:
            print("  - %s" % failure)
        return 1
    print("OK: %d checks passed" % report.checks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
