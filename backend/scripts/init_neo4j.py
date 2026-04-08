import argparse
import sys
from pathlib import Path

from neo4j import GraphDatabase

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings


def split_cypher_statements(content: str) -> list[str]:
    statements: list[str] = []
    buffer: list[str] = []
    in_single_quote = False
    in_double_quote = False

    for char in content:
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote

        if char == ";" and not in_single_quote and not in_double_quote:
            statement = "".join(buffer).strip()
            if statement:
                statements.append(statement)
            buffer = []
            continue

        buffer.append(char)

    tail = "".join(buffer).strip()
    if tail:
        statements.append(tail)
    return statements


def execute_cypher_file(session, cypher_path: Path) -> None:
    content = cypher_path.read_text(encoding="utf-8")
    statements = split_cypher_statements(content)

    for statement in statements:
        session.run(statement).consume()


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize MusicGraph Neo4j schema and seed data.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete all nodes and relationships before applying schema and seed data.",
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Apply schema only.",
    )
    parser.add_argument(
        "--seed-only",
        action="store_true",
        help="Apply seed data only.",
    )
    args = parser.parse_args()

    if args.schema_only and args.seed_only:
        raise SystemExit("--schema-only and --seed-only cannot be used together.")

    settings = get_settings()
    if not settings.neo4j_uri or not settings.neo4j_username or not settings.neo4j_password:
        raise SystemExit("Neo4j connection settings are incomplete. Check backend/.env.")

    neo4j_dir = BACKEND_DIR / "neo4j"
    schema_file = neo4j_dir / "schema.cypher"
    seed_file = neo4j_dir / "seed.cypher"
    reset_file = neo4j_dir / "reset.cypher"

    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )

    try:
        driver.verify_connectivity()
        with driver.session(database=settings.neo4j_database) as session:
            if args.reset:
                execute_cypher_file(session, reset_file)
                print("Reset complete.")

            if not args.seed_only:
                execute_cypher_file(session, schema_file)
                print("Schema applied.")

            if not args.schema_only:
                execute_cypher_file(session, seed_file)
                print("Seed data applied.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
