"""Layer B — the course design graph, owned by the design pipeline.

A small property graph (nodes + typed edges) persisted as JSON per design project. Same vocabulary as
graph/schema.cypher Layer B, so a Neo4j backend can replace it without touching agents or validators.

Invariants enforced here:
- uid = "<project_id>/<local_id>"; nodes carry version, status, created_by, prompt_id, prompt_version, model, sources
- frozen nodes cannot be modified or removed (FrozenError) — non-negotiable 6
- replacing a node bumps version; the old version is kept under `history`
"""
from __future__ import annotations

import copy
import re
import json
import time
from pathlib import Path
from typing import Any, Iterable


class FrozenError(RuntimeError):
    pass


class DesignGraph:
    def __init__(self, project_id: str, path: Path | None = None):
        self.project_id = project_id
        self.path = path
        self.nodes: dict[str, dict] = {}
        self.edges: list[dict] = []
        self.history: list[dict] = []

    # ------------------------------------------------------------------ ids
    def uid(self, local_id: str) -> str:
        return local_id if local_id.startswith(self.project_id + "/") else f"{self.project_id}/{local_id}"

    def local(self, uid: str) -> str:
        return uid.split("/", 1)[1] if uid.startswith(self.project_id + "/") else uid

    # ------------------------------------------------------------------ nodes
    def put(self, label: str, local_id: str, props: dict, *, created_by: str, prompt_id: str | None = None,
            prompt_version: str | None = None, model: str | None = None, sources: list | None = None, status: str = "draft") -> str:
        u = self.uid(local_id)
        old = self.nodes.get(u)
        if old and old["status"] == "frozen":
            raise FrozenError(f"{u} is frozen")
        node = {
            "uid": u, "local_id": self.local(u), "label": label, "props": copy.deepcopy(props),
            "version": (old["version"] + 1) if old else 1, "status": status, "created_by": created_by,
            "prompt_id": prompt_id or (created_by if re.match(r"^[A-Z]\d+$", created_by) else None), "prompt_version": prompt_version,
            "model": model, "sources": sources or props.get("sources") or [], "ts": time.time(),
        }
        if old:
            self.history.append(old)
        self.nodes[u] = node
        return u

    def update(self, uid: str, field: str, value: Any, by: str) -> None:
        u = self.uid(uid)
        n = self.nodes[u]
        if n["status"] == "frozen":
            raise FrozenError(f"{u} is frozen")
        self.history.append(copy.deepcopy(n))
        n["props"][field] = value
        n["version"] += 1
        n["created_by"] = by
        n["ts"] = time.time()

    def remove(self, uid: str) -> None:
        u = self.uid(uid)
        if self.nodes.get(u, {}).get("status") == "frozen":
            raise FrozenError(f"{u} is frozen")
        if u in self.nodes:
            self.history.append(self.nodes.pop(u))
        self.edges = [e for e in self.edges if e["src"] != u and e["dst"] != u]

    def get(self, uid: str) -> dict | None:
        return self.nodes.get(self.uid(uid)) or self.nodes.get(uid)

    def props(self, uid: str) -> dict:
        n = self.get(uid)
        return n["props"] if n else {}

    def by_label(self, label: str) -> list[dict]:
        return sorted((n for n in self.nodes.values() if n["label"] == label), key=lambda n: n["local_id"])

    def remove_label(self, label: str) -> None:
        for n in list(self.by_label(label)):
            self.remove(n["uid"])

    # ------------------------------------------------------------------ edges
    def link(self, src: str, rel: str, dst: str, **props) -> None:
        s = self.uid(src) if not _external(src) else src
        d = self.uid(dst) if not _external(dst) else dst
        self.edges = [e for e in self.edges if not (e["src"] == s and e["rel"] == rel and e["dst"] == d)]
        self.edges.append({"src": s, "rel": rel, "dst": d, "props": props})

    def out(self, uid: str, rel: str) -> list[dict]:
        u = self.uid(uid) if not _external(uid) else uid
        return [e for e in self.edges if e["src"] == u and e["rel"] == rel]

    def into(self, uid: str, rel: str) -> list[dict]:
        u = self.uid(uid) if not _external(uid) else uid
        return [e for e in self.edges if e["dst"] == u and e["rel"] == rel]

    def edges_rel(self, rel: str) -> list[dict]:
        return [e for e in self.edges if e["rel"] == rel]

    def drop_edges(self, rel: str, src_label: str | None = None) -> None:
        self.edges = [e for e in self.edges
                      if not (e["rel"] == rel and (src_label is None or self.nodes.get(e["src"], {}).get("label") == src_label))]

    # ------------------------------------------------------------------ status
    def set_status(self, uids: Iterable[str], status: str) -> None:
        for u in uids:
            n = self.get(u)
            if n:
                n["status"] = status

    def freeze_labels(self, labels: Iterable[str]) -> list[str]:
        frozen = []
        for lab in labels:
            for n in self.by_label(lab):
                n["status"] = "frozen"
                frozen.append(n["uid"])
        return frozen

    def frozen_ids(self) -> list[str]:
        return [u for u, n in self.nodes.items() if n["status"] == "frozen"]

    # ------------------------------------------------------------------ persistence
    def save(self) -> None:
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps({"project_id": self.project_id, "nodes": self.nodes, "edges": self.edges,
                                             "history_len": len(self.history)}, indent=1, ensure_ascii=False, default=str),
                                 encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "DesignGraph":
        d = json.loads(path.read_text(encoding="utf-8"))
        g = cls(d["project_id"], path)
        g.nodes, g.edges = d["nodes"], d["edges"]
        return g


def _external(uid: str) -> bool:
    """Layer A / external references are stored verbatim (e.g. 'CSE201', 'BTECH-CSE/PO4', 'EXT:MIT/6.1020')."""
    return uid.startswith(("EXT:", "BTECH-", "T:")) or (uid.isupper() and "/" not in uid and any(ch.isdigit() for ch in uid))
