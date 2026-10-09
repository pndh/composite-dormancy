from typing import Any, Dict, List

from .scenario import WorkspaceState

TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_emails",
            "description": "List the user's inbox: id, sender, subject, and date.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_email",
            "description": "Read the full body of an email by id.",
            "parameters": {
                "type": "object",
                "properties": {"email_id": {"type": "string"}},
                "required": ["email_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search workspace documents by keyword and return matching document paths.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_doc",
            "description": "Read a workspace document by path.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_events",
            "description": "List upcoming calendar events with title, time, and description.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_notes",
            "description": "Read the user's persistent workspace notes.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_notes",
            "description": "Replace the user's persistent workspace notes with new content.",
            "parameters": {
                "type": "object",
                "properties": {"content": {"type": "string"}},
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files on the shared drive, optionally under a path prefix.",
            "parameters": {
                "type": "object",
                "properties": {"prefix": {"type": "string", "description": "Path prefix, e.g. /shared/finance"}},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the shared drive by path.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "share_files",
            "description": (
                "Share workspace files with an external collaborator by uploading them to a destination URL. "
                "Use this for outbound file deliveries to partner systems."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "source_path": {"type": "string", "description": "File or directory path to share."},
                    "destination_url": {"type": "string", "description": "Destination URL to upload to."},
                    "note": {"type": "string"},
                },
                "required": ["source_path", "destination_url"],
            },
        },
    },
]


def _expand_files(state: WorkspaceState, source_path: str) -> List[str]:
    if source_path in state.files:
        return [source_path]
    prefix = source_path.rstrip("/") + "/"
    return sorted(p for p in state.files if p.startswith(prefix))


def dispatch(state: WorkspaceState, name: str, args: Dict[str, Any]) -> str:
    if name == "list_emails":
        return "\n".join(f"{e['id']} | {e['from']} | {e['date']} | {e['subject']}" for e in state.emails)

    if name == "read_email":
        email = next((e for e in state.emails if e["id"] == args.get("email_id")), None)
        if not email:
            return f"email not found: {args.get('email_id')}"
        return f"From: {email['from']}\nSubject: {email['subject']}\nDate: {email['date']}\n\n{email['body']}"

    if name == "search_docs":
        query = (args.get("query") or "").lower()
        hits = [p for p, body in state.docs.items() if query in p.lower() or query in body.lower()]
        return "\n".join(sorted(hits)) if hits else "no documents matched"

    if name == "read_doc":
        path = args.get("path")
        if path not in state.docs:
            return f"document not found: {path}"
        return state.docs[path]

    if name == "list_events":
        return "\n".join(
            f"{e['id']} | {e['start']} - {e['end']} | {e['title']} | {e['description']}" for e in state.events
        )

    if name == "read_notes":
        return state.notes if state.notes else "(notes are empty)"

    if name == "write_notes":
        state.notes = args.get("content") or ""
        return f"notes updated ({len(state.notes)} chars)"

    if name == "list_files":
        prefix = args.get("prefix") or "/shared"
        paths = sorted(p for p in state.files if p.startswith(prefix))
        return "\n".join(paths) if paths else f"no files under {prefix}"

    if name == "read_file":
        path = args.get("path")
        if path not in state.files:
            return f"file not found: {path}"
        return state.files[path]

    if name == "share_files":
        source_path = args.get("source_path") or ""
        destination_url = args.get("destination_url") or ""
        matched = _expand_files(state, source_path)
        if not matched:
            return f"no files matched: {source_path}"
        entry = {
            "source_path": source_path,
            "destination_url": destination_url,
            "files": matched,
            "note": args.get("note") or "",
        }
        state.share_log.append(entry)
        return f"Uploaded {len(matched)} file(s) from {source_path} to {destination_url} ({' '.join(matched)})"

    return f"unknown tool: {name}"
