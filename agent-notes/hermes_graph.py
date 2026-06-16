#!/usr/bin/env python3
"""Hermes GraphMemory — entity graph on ChromaDB.

Hooks:
  hermes_graph.py session_start   -> loads graph for agent context
  hermes_graph.py extract <text>  -> extracts entities from LLM response
"""
import os, sys, json, re, textwrap, hashlib, uuid, time

# -- ensure PYTHONPATH includes our packages --
_PP = os.environ.get("PYTHONPATH", "")
_OUR_PATHS = ["/root/.hermes/python-packages", "/root/wiki/agent-notes"]
for _p in _OUR_PATHS:
    if _p not in _PP.split(":") and os.path.isdir(_p):
        sys.path.insert(0, _p)

# -- config --
AGENT_NAME  = os.environ.get("AGENT_NAME", "unknown")
CHROMA_DIR  = os.environ.get("HERMES_GRAPH_DIR", "/root/.hermes/graph_db")
MODEL       = os.environ.get("LLM_MODEL", "deepseek-chat")

_import_err = None
try:
    import chromadb
    from chromadb.config import Settings
except ImportError as e:
    _import_err = str(e)

# -- helpers --
def _get_client():
    return chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False),
    )

def _ensure_collections(cli):
    """Return (entities, relations) collections."""
    try:
        e = cli.get_collection("entities")
    except Exception:
        e = cli.create_collection(
            name="entities",
            metadata={"hnsw:space": "cosine", "description": AGENT_NAME + " entities"},
        )
    try:
        r = cli.get_collection("relations")
    except Exception:
        r = cli.create_collection(
            name="relations",
            metadata={"hnsw:space": "cosine", "description": AGENT_NAME + " relations"},
        )
    return e, r

def _entity_id(name):
    return hashlib.md5(name.lower().strip().encode()).hexdigest()

def _relation_id(subj, pred, obj):
    raw = subj + "|" + pred + "|" + obj
    return hashlib.md5(raw.lower().encode()).hexdigest()

# -- entity extraction via LLM --
def _extract_entities_from_llm(text):
    """Use DeepSeek to extract entities + relations from text."""
    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base    = os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
    if not api_key:
        return []

    import urllib.request
    prompt = textwrap.dedent("""\
        Extract entities and relationships from the text below.
        Return ONLY valid JSON array: [{"subject": "...", "predicate": "...", "object": "..."}]
        Text: """ + text[:3000])
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1, "max_tokens": 1024,
    }).encode()
    req = urllib.request.Request(
        base + "/chat/completions",
        data=body,
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        content = data["choices"][0]["message"]["content"]
        # strip code fences
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        return json.loads(content)
    except Exception as exc:
        print("[graph] LLM extraction error: " + str(exc), file=sys.stderr)
        return []

# -- session_start hook --
def cmd_session_start():
    if _import_err:
        print("[graph] chromadb unavailable: " + _import_err, file=sys.stderr)
        return
    cli = _get_client()
    col_entities, col_relations = _ensure_collections(cli)
    count_e = col_entities.count()
    count_r = col_relations.count()
    print("[" + AGENT_NAME + "] GraphMemory: " + str(count_e) + " entities, " + str(count_r) + " relationships")

    if count_e == 0:
        return  # nothing yet

    # Show top entities
    all_e = col_entities.get(limit=min(count_e, 30))
    names = sorted(set(
        m.get("name", "") for m in (all_e.get("metadatas") or [])
    ))
    if names:
        print("Known entities: " + ", ".join(names[:15]))
        if len(names) > 15:
            print("  ... and " + str(len(names) - 15) + " more")

    # Show top relations
    if count_r > 0:
        all_r = col_relations.get(limit=min(count_r, 20))
        rels = []
        for midx, md in enumerate(all_r.get("metadatas") or []):
            if md:
                rels.append(md.get("subject","?") + " -> " + md.get("predicate","?") + " -> " + md.get("object","?"))
        if rels:
            print("Relations (" + str(len(rels)) + "):")
            for r in rels[:10]:
                print("   " + r)

# -- extract hook --
def cmd_extract(text=None):
    if _import_err:
        print("[graph] chromadb unavailable: " + _import_err, file=sys.stderr)
        return
    if not text:
        text = os.environ.get("HERMES_RESPONSE", "")
    if not text or len(text.strip()) < 20:
        return

    triples = _extract_entities_from_llm(text)
    if not triples:
        return

    cli = _get_client()
    col_e, col_r = _ensure_collections(cli)

    entities_seen = {}
    for t in triples:
        subj = str(t.get("subject", "")).strip()
        pred = str(t.get("predicate", "")).strip()
        obj  = str(t.get("object", "")).strip()
        if not subj or not pred or not obj:
            continue
        entities_seen[_entity_id(subj)] = subj
        entities_seen[_entity_id(obj)]  = obj

        # upsert relation
        rel_id = _relation_id(subj, pred, obj)
        try:
            col_r.upsert(
                ids=[rel_id],
                documents=[subj + " " + pred + " " + obj],
                metadatas=[{"subject": subj, "predicate": pred, "object": obj, "agent": AGENT_NAME}],
            )
        except Exception as exc:
            print("[graph] relation upsert error: " + str(exc), file=sys.stderr)

    # upsert entities
    for eid, ename in entities_seen.items():
        try:
            col_e.upsert(
                ids=[eid],
                documents=[ename],
                metadatas=[{"name": ename, "agent": AGENT_NAME}],
            )
        except Exception as exc:
            print("[graph] entity upsert error: " + str(exc), file=sys.stderr)

    print("[graph] Extracted " + str(len(triples)) + " relations, " + str(len(entities_seen)) + " entities")

# -- entrypoint --
if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: hermes_graph.py session_start|extract [text]", file=sys.stderr)
        sys.exit(1)

    cmd = args[0]
    if cmd == "session_start":
        cmd_session_start()
    elif cmd == "extract":
        text = " ".join(args[1:]) if len(args) > 1 else None
        cmd_extract(text)
    else:
        print("Unknown command: " + cmd, file=sys.stderr)
        sys.exit(1)
