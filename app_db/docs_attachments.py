import shutil
import time
from pathlib import Path
from typing import Dict, List, Set

from app_db.models import DocumentationPage


ATTACHMENT_REF_TOKEN = "/docs/attachments/"


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_docs_attachments_dir() -> Path:
    target = get_project_root() / "uploads" / "attachments" / "docs"
    target.mkdir(parents=True, exist_ok=True)
    return target


def get_legacy_attachments_dir() -> Path:
    return get_project_root() / "uploads" / "attachments" / "changemanagement"


def get_trash_dir() -> Path:
    target = get_project_root() / "uploads" / "attachments" / ".trash" / "docs"
    target.mkdir(parents=True, exist_ok=True)
    return target


def _extract_references_from_html(content_html: str) -> Set[str]:
    refs = set()
    html = content_html or ""
    start = 0
    while True:
        idx = html.find(ATTACHMENT_REF_TOKEN, start)
        if idx < 0:
            break
        begin = idx + len(ATTACHMENT_REF_TOKEN)
        end = begin
        while end < len(html) and html[end] not in {'"', "'", "?", "#", "<", " ", "\\n", "\\r", "\\t"}:
            end += 1
        filename = Path(html[begin:end]).name
        if filename:
            refs.add(filename)
        start = end
    return refs


def collect_referenced_filenames() -> Set[str]:
    refs = set()
    docs = DocumentationPage.query.with_entities(DocumentationPage.content_html).all()
    for (content_html,) in docs:
        refs.update(_extract_references_from_html(content_html or ""))
    return refs


def _list_files(dir_path: Path) -> List[Path]:
    if not dir_path.exists():
        return []
    return [p for p in dir_path.iterdir() if p.is_file()]


def find_orphaned_files(include_legacy: bool = False) -> Dict[str, List[str]]:
    referenced = collect_referenced_filenames()

    scan_dirs = [("docs", get_docs_attachments_dir())]
    if include_legacy:
        scan_dirs.append(("legacy", get_legacy_attachments_dir()))

    orphaned = []
    existing = []
    for label, scan_dir in scan_dirs:
        for file_path in _list_files(scan_dir):
            existing.append(f"{label}:{file_path.name}")
            if file_path.name not in referenced:
                orphaned.append(f"{label}:{file_path.name}")

    return {
        "referenced": sorted(referenced),
        "existing": sorted(existing),
        "orphaned": sorted(orphaned),
    }


def cleanup_orphaned_files(
    *,
    apply_changes: bool,
    delete_permanently: bool,
    include_legacy: bool,
    min_age_minutes: int,
) -> Dict[str, object]:
    referenced = collect_referenced_filenames()
    scan_dirs = [("docs", get_docs_attachments_dir())]
    if include_legacy:
        scan_dirs.append(("legacy", get_legacy_attachments_dir()))

    now = time.time()
    min_age_seconds = max(0, min_age_minutes) * 60

    moved = []
    deleted = []
    skipped_recent = []
    orphaned = []

    for label, scan_dir in scan_dirs:
        for file_path in _list_files(scan_dir):
            if file_path.name in referenced:
                continue

            age_seconds = now - file_path.stat().st_mtime
            if age_seconds < min_age_seconds:
                skipped_recent.append(f"{label}:{file_path.name}")
                continue

            orphan_key = f"{label}:{file_path.name}"
            orphaned.append(orphan_key)

            if not apply_changes:
                continue

            if delete_permanently:
                file_path.unlink(missing_ok=True)
                deleted.append(orphan_key)
            else:
                destination = get_trash_dir() / f"{label}_{file_path.name}"
                counter = 2
                while destination.exists():
                    destination = get_trash_dir() / f"{label}_{file_path.stem}_{counter}{file_path.suffix}"
                    counter += 1
                shutil.move(str(file_path), str(destination))
                moved.append(orphan_key)

    return {
        "apply_changes": apply_changes,
        "delete_permanently": delete_permanently,
        "include_legacy": include_legacy,
        "min_age_minutes": min_age_minutes,
        "referenced_count": len(referenced),
        "orphaned_count": len(orphaned),
        "orphaned": sorted(orphaned),
        "moved": sorted(moved),
        "deleted": sorted(deleted),
        "skipped_recent": sorted(skipped_recent),
    }
