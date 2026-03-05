import argparse
import sys

from auth_server import app
from app_db.docs_attachments import cleanup_orphaned_files


def main():
    parser = argparse.ArgumentParser(
        description="Docs attachments housekeeping: detect and clean orphaned /docs/attachments files."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply cleanup changes. Default is dry-run.",
    )
    parser.add_argument(
        "--delete-permanently",
        action="store_true",
        help="Delete orphan files permanently. Default behavior moves to trash.",
    )
    parser.add_argument(
        "--include-legacy",
        action="store_true",
        help="Also scan legacy directory uploads/attachments/changemanagement.",
    )
    parser.add_argument(
        "--min-age-minutes",
        type=int,
        default=60,
        help="Skip orphan files newer than this many minutes (default: 60).",
    )
    args = parser.parse_args()

    with app.app_context():
        result = cleanup_orphaned_files(
            apply_changes=args.apply,
            delete_permanently=args.delete_permanently,
            include_legacy=args.include_legacy,
            min_age_minutes=args.min_age_minutes,
        )

    mode = "APPLY" if args.apply else "DRY-RUN"
    action = "delete" if args.delete_permanently else "move-to-trash"

    print(f"Mode: {mode}")
    print(f"Action: {action}")
    print(f"Referenced files: {result['referenced_count']}")
    print(f"Orphan candidates: {result['orphaned_count']}")
    print(f"Skipped recent: {len(result['skipped_recent'])}")

    if args.apply:
        print(f"Moved: {len(result['moved'])}")
        print(f"Deleted: {len(result['deleted'])}")

    if result["orphaned"]:
        print("\nOrphan files:")
        for item in result["orphaned"]:
            print(f"- {item}")

    if result["skipped_recent"]:
        print("\nSkipped recent files:")
        for item in result["skipped_recent"]:
            print(f"- {item}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
