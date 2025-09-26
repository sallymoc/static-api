#!/usr/bin/env python3
"""
Update data/smart_contracts.json by fetching sources from GitHub raw.

Rules:
- Skip contracts with contract_index == None.
- Include contracts even with zero REGISTER_USER_PROCEDURE calls (procedures=[]).
- "name": read from contract_def.h -> struct ContractDescription -> contractDescriptions array.
          Each item (EXCEPT the first) corresponds to index 1..N.
          Use the FIRST quoted string inside each item AS-IS (no transformations).
- "label": preserved if already exists; otherwise built from filename with special Q-rule:
      * If stem starts with "Q" or "q":
          - Ensure the next char is uppercase.
          - If whole name is uppercase, keep "Q" + next uppercase + rest lowercase (QVAULT -> QVault).
          - Examples: Qx -> Qx, QUTIL -> QUtil, Qswap -> QSwap, Qbay -> QBay.
      * Otherwise: prettified phrase (GeneralQuorumProposal -> General Quorum Proposal).
- Fields: filename, name, label, github_url, contract_index, address, procedures(list of {id,name}).
- address: computed via Node using your JS helper:
      const publicKey = helper.getIdentityBytes(addr56);  // addr56 built from contract_index (A..P, LE, len=56)
      const identity  = await helper.getIdentity(publicKey)  // 60-char with checksum
- Non-destructive merge: adds new contracts and new procedure IDs; preserves manual edits,
  but refreshes authoritative fields (name, contract_index, and address if newly computed).
- Sort: contracts by contract_index; procedures by id.
"""

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

# ---------------------------- Config ----------------------------------------

RAW_BASE_CONTRACTS = "https://raw.githubusercontent.com/qubic/core/main/src/contracts/"
RAW_CONTRACT_DEF   = "https://raw.githubusercontent.com/qubic/core/main/src/contract_core/contract_def.h"

# ---------------------------- Regexes ---------------------------------------

REGISTER_RE = re.compile(
    r"""
    REGISTER_USER_PROCEDURE
    \s*\(
        \s* [&\s]* (?P<name>[A-Za-z_][A-Za-z0-9_]*)   # 1st param (symbol), optional &
        \s*,\s*
        (?P<num>\d+)                                  # 2nd param (number)
    \s*\)
    """,
    re.VERBOSE | re.DOTALL | re.MULTILINE,
)

INCLUDE_RE = re.compile(r'#\s*include\s*["<](?P<path>[^">]+)[">]')
CONTRACT_INDEX_RE = re.compile(r'#\s*define\s+[A-Za-z0-9_]+_CONTRACT_INDEX\s+(?P<num>\d+)\b')

FIRST_QUOTED_STRING_RE = re.compile(r'"([^"]+)"')

BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
LINE_COMMENT_RE  = re.compile(r"//[^\n]*")

# ---------------------------- Helpers: text/format --------------------------

def strip_comments(code: str) -> str:
    code = BLOCK_COMMENT_RE.sub("", code)
    code = LINE_COMMENT_RE.sub("", code)
    return code

def split_camel_or_snake(name: str) -> List[str]:
    if "_" in name:
        parts = name.split("_")
    else:
        parts = re.sub(r"(?<!^)(?=[A-Z])", " ", name).split()
    words: List[str] = []
    for p in parts:
        words.extend(re.findall(r"[A-Za-z]+|\d+", p))
    return [w for w in words if w]

SMALL_WORDS = {
    "a","an","the","and","but","or","nor","so","yet","at","by","for","from","in","into","of","on","onto","out","over",
    "to","up","with","as","per","via","vs","vs.","off","than","till","until","past","near","down","upon","within",
    "without","through","about","before","after","around","behind","below","beneath","beside","between","beyond",
    "during","inside","outside","under","underneath","across","along","amid","among","despite","except","including",
    "like","since","toward","towards","regarding",
}

def title_with_small_words(words: List[str]) -> str:
    if not words:
        return ""
    out: List[str] = []
    last = len(words) - 1
    for i, w in enumerate(words):
        wl = w.lower()
        if w.isupper() and len(w) > 1:
            out.append(w)  # keep acronyms as-is
        elif i not in (0, last) and wl in SMALL_WORDS:
            out.append(wl)
        else:
            out.append(w.capitalize())
    return " ".join(out)

def pretty_label_from_filename(stem: str) -> str:
    return title_with_small_words(split_camel_or_snake(stem))

def pretty_procedure_name(identifier: str) -> str:
    """Format a procedure identifier into a nice phrase."""
    return title_with_small_words(split_camel_or_snake(identifier))

def label_from_filename_with_q_rule(stem: str) -> str:
    """
    Build a label from the filename stem with special 'Q*' handling:
    - If stem starts with 'Q' or 'q':
        * Ensure the NEXT char is uppercase.
        * If the whole stem is ALL CAPS (e.g., 'QVAULT'), keep 'Q' + next uppercase + rest lowercase.
          Examples: 'QUTIL' -> 'QUtil', 'QVAULT' -> 'QVault'
        * 'Qx' -> 'Qx', 'Qswap' -> 'QSwap', 'Qbay' -> 'QBay'
    - Otherwise: fall back to the pretty phrase.
    """
    if not stem:
        return ""
    if stem[0].lower() != "q" or len(stem) == 1:
        return pretty_label_from_filename(stem)

    rest = stem[1:]
    first = rest[0].upper()
    tail = rest[1:]

    if stem.isupper():
        return "Q" + first + tail.lower()

    return "Q" + first + tail

# ---------------------------- Fetch from GitHub raw -------------------------

def fetch_text(url: str) -> Optional[str]:
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return resp.text
        print(f"Warning: GET {url} -> {resp.status_code}")
    except Exception as e:
        print(f"Warning: GET {url} failed: {e}")
    return None

# ---------------------------- Parse contract_def.h --------------------------

def parse_contract_def_from_raw(raw_text: str, known_contract_basenames: Optional[set] = None) -> Dict[str, int]:
    lines = raw_text.splitlines()
    mapping: Dict[str, int] = {}
    for i, line in enumerate(lines):
        inc = INCLUDE_RE.search(line)
        if not inc:
            continue
        basename = Path(inc.group("path")).name
        if known_contract_basenames and basename not in known_contract_basenames:
            continue

        cidx: Optional[int] = None
        for j in range(i - 1, max(i - 6, -1), -1):
            m = CONTRACT_INDEX_RE.search(lines[j])
            if m:
                cidx = int(m.group("num"))
                break
        if cidx is not None:
            mapping[basename] = cidx
    return mapping

def extract_contract_names_from_descriptions(raw_text: str) -> Dict[int, str]:
    text = strip_comments(raw_text)
    token = "contractDescriptions"
    pos = text.find(token)
    if pos == -1:
        return {}
    eq_pos = text.find("=", pos)
    if eq_pos == -1:
        return {}
    brace_start = text.find("{", eq_pos)
    if brace_start == -1:
        return {}

    depth = 0
    end = brace_start
    while end < len(text):
        ch = text[end]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        end += 1
    if depth != 0:
        return {}

    body = text[brace_start + 1:end]

    items: List[str] = []
    i = 0
    while i < len(body):
        if body[i].isspace() or body[i] == ",":
            i += 1
            continue
        if body[i] != "{":
            i += 1
            continue
        start = i
        d = 0
        while i < len(body):
            if body[i] == "{":
                d += 1
            elif body[i] == "}":
                d -= 1
                if d == 0:
                    i += 1
                    items.append(body[start:i])
                    break
            i += 1

    names: Dict[int, str] = {}
    for idx1, item in enumerate(items, start=0):
        if idx1 == 0:
            continue
        m = FIRST_QUOTED_STRING_RE.search(item)
        if not m:
            continue
        name = m.group(1)
        names[idx1] = name
    return names

# ---------------------------- Header scanning -------------------------------

def should_skip_filename(fname: str) -> bool:
    if fname == "README.md":
        return True
    if fname.startswith("Test"):
        return True
    if fname in {"math_lib.h", "qpi.h"}:
        return True
    return False

def find_registers(text: str) -> List[Tuple[int, str]]:
    text_nc = strip_comments(text)
    out: List[Tuple[int, str]] = []
    for m in REGISTER_RE.finditer(text_nc):
        out.append((int(m.group("num")), m.group("name")))
    return out

# ---------------------------- Address helpers -------------------------------

def index_to_base56(idx: int) -> str:
    alphabet = "ABCDEFGHIJKLMNOP"
    if idx <= 0:
        return "A" * 56
    chars: List[str] = []
    n = idx
    while n > 0 and len(chars) < 56:
        chars.append(alphabet[n & 0xF])
        n >>= 4
    while len(chars) < 56:
        chars.append("A")
    return "".join(chars[:56])

def run_js_get_identity_from_index(cidx: int, js_lib_path: Path) -> Optional[str]:
    js_path = js_lib_path.resolve()
    if not js_path.exists():
        print(f"Warning: JS helper not found at {js_path}; skipping identity.")
        return None

    addr56 = index_to_base56(cidx)

    js_program = f"""
    (async () => {{
      const g = globalThis;
      if (typeof g.self === 'undefined') g.self = g;
      if (typeof g.window === 'undefined') g.window = g;
      if (!g.crypto || !g.crypto.subtle) {{
        try {{ g.crypto = require('crypto').webcrypto; }} catch (e) {{}}
      }}
      if (typeof g.atob === 'undefined') g.atob = (s) => Buffer.from(s, 'base64').toString('binary');
      if (typeof g.btoa === 'undefined') g.btoa = (s) => Buffer.from(s, 'binary').toString('base64');

      const mod = require({json.dumps(str(js_path))});
      let QubicHelper = null;
      if (mod && typeof mod.QubicHelper === 'function') QubicHelper = mod.QubicHelper;
      else if (mod && mod.default && typeof mod.default.QubicHelper === 'function') QubicHelper = mod.default.QubicHelper;
      else if (typeof mod === 'function') QubicHelper = mod;
      if (!QubicHelper) throw new Error('QubicHelper class not found in exports');

      const helper = new QubicHelper();

      const addr = {json.dumps(addr56)};
      const publicKey = helper.getIdentityBytes(addr);
      const identity = await helper.getIdentity(publicKey);
      if (typeof identity !== 'string' || identity.length !== 60) throw new Error('Invalid identity length');
      process.stdout.write(identity);
    }})().catch(e => {{ console.error(String(e && e.stack || e)); process.exit(1); }});
    """

    try:
        res = subprocess.run(
            ["node", "-e", js_program],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except FileNotFoundError:
        print("Warning: Node not found; skipping identity.")
    except subprocess.CalledProcessError as e:
        msg = e.stderr.strip() or e.stdout.strip()
        print(f"Warning: getIdentity failed: {msg}")
    return None

# ---------------------------- JSON merge/sort -------------------------------

def normalize_procs_to_list(procs: Any) -> List[Dict[str, Any]]:
    items: Dict[int, str] = {}
    if isinstance(procs, dict):
        for k, v in procs.items():
            try:
                items[int(k)] = v
            except (TypeError, ValueError):
                continue
    elif isinstance(procs, list):
        for obj in procs:
            if isinstance(obj, dict) and "id" in obj and "name" in obj:
                try:
                    items[int(obj["id"])] = obj["name"]
                except (TypeError, ValueError):
                    continue
    return [{"id": pid, "name": items[pid]} for pid in sorted(items.keys())]

def index_by_filename(contracts: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for sc in contracts:
        fn = sc.get("filename")
        if isinstance(fn, str):
            out[fn] = sc
    return out

def merge_contracts(existing: List[Dict[str, Any]], fresh: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_filename: Dict[str, Dict[str, Any]] = index_by_filename(existing)

    for new in fresh:
        fname = new.get("filename")
        if not isinstance(fname, str):
            continue

        if fname not in by_filename:
            new["procedures"] = normalize_procs_to_list(new.get("procedures", []))
            existing.append(new)
            by_filename[fname] = new
            continue

        ex = by_filename[fname]

        if isinstance(new.get("name"), str):
            ex["name"] = new["name"]
        if "contract_index" in new:
            ex["contract_index"] = new["contract_index"]
        if new.get("address"):
            ex["address"] = new["address"]

        # keep existing label if present
        if not ex.get("label") and isinstance(new.get("label"), str):
            ex["label"] = new["label"]

        ex_list = normalize_procs_to_list(ex.get("procedures", []))
        new_list = normalize_procs_to_list(new.get("procedures", []))
        have = {p["id"] for p in ex_list}
        for p in new_list:
            if p["id"] not in have:
                ex_list.append(p)
                have.add(p["id"])
        ex_list.sort(key=lambda x: x["id"])
        ex["procedures"] = ex_list

    return existing

def sort_contracts(contracts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        contracts,
        key=lambda sc: sc.get("contract_index") if sc.get("contract_index") is not None else 1e9
    )

# ---------------------------- Main -----------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Update data/smart_contracts.json from GitHub raw (names from contract_def.h; correct identity calc; Q-label rule)."
    )
    ap.add_argument("--data-file", default="data/smart_contracts.json", help="Path to smart_contracts.json")
    ap.add_argument("--js-lib", default="lib/qubic-js-library.js", help="Path to qubic-js-library.js")
    args = ap.parse_args()

    data_path = Path(args.data_file).resolve()
    data_path.parent.mkdir(parents=True, exist_ok=True)
    js_lib_path = Path(args.js_lib).resolve()

    contract_def_text = fetch_text(RAW_CONTRACT_DEF)
    if not contract_def_text:
        raise SystemExit("Could not fetch contract_def.h")

    stripped = strip_comments(contract_def_text)

    all_basenames = set(Path(m.group("path")).name for m in INCLUDE_RE.finditer(stripped))
    basenames = {b for b in all_basenames if not should_skip_filename(b)}
    idx_map = parse_contract_def_from_raw(stripped, basenames)

    idx_to_name = extract_contract_names_from_descriptions(stripped)

    fresh_entries: List[Dict[str, Any]] = []
    for basename in sorted(basenames):
        cidx = idx_map.get(basename)
        if cidx is None:
            continue

        url = RAW_BASE_CONTRACTS + basename
        text = fetch_text(url)

        regs: List[Tuple[int, str]] = []
        if text:
            regs = find_registers(text)

        procs: List[Dict[str, Any]] = []
        seen: set[int] = set()
        for num, ident in regs:
            if num in seen:
                continue
            seen.add(num)
            procs.append({"id": num, "name": pretty_procedure_name(ident)})
        procs.sort(key=lambda x: x["id"])

        stem = Path(basename).stem
        label = label_from_filename_with_q_rule(stem)

        name_value = idx_to_name.get(cidx, stem.upper())

        addr: Optional[str] = None
        identity = run_js_get_identity_from_index(cidx, js_lib_path)
        if identity and len(identity) == 60:
            addr = identity
        else:
            addr = index_to_base56(cidx)

        github_url = f"https://github.com/qubic/core/blob/main/src/contracts/{basename}"

        fresh_entries.append({
            "filename": basename,
            "name": name_value,
            "label": label,
            "github_url": github_url,
            "contract_index": cidx,
            "address": addr,
            "procedures": procs,
        })

    try:
        existing_top = json.loads(data_path.read_text(encoding="utf-8"))
    except Exception:
        existing_top = {}
    if not isinstance(existing_top, dict):
        existing_top = {}

    existing_sc = existing_top.get("smart_contracts", [])
    if not isinstance(existing_sc, list):
        existing_sc = []

    merged_sc = merge_contracts(existing_sc, fresh_entries)
    merged_sc = sort_contracts(merged_sc)

    existing_top["smart_contracts"] = merged_sc

    data_path.write_text(json.dumps(existing_top, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated {data_path} with {len(merged_sc)} smart_contract(s).")

# ----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
