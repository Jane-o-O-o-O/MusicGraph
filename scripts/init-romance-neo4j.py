"""
导入三国演义知识图谱到 Neo4j

使用方法：
python scripts/init_romance-neo4j.py [--reset]
"""

import argparse
import sys
from pathlib import Path

# 将 backend 目录加入 path，以便导入 app 模块
BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings
from neo4j import GraphDatabase


def is_backslash_escaped(content: str, index: int) -> bool:
    backslash_count = 0
    cursor = index - 1
    while cursor >= 0 and content[cursor] == "\\":
        backslash_count += 1
        cursor -= 1
    return backslash_count % 2 == 1


def split_cypher_statements(content: str) -> list[str]:
    statements: list[str] = []
    buffer: list[str] = []
    in_single_quote = False
    in_double_quote = False
    index = 0

    while index < len(content):
        char = content[index]
        if char == "'" and not in_double_quote:
            if in_single_quote and index + 1 < len(content) and content[index + 1] == "'":
                buffer.extend(["'", "'"])
                index += 2
                continue
            if is_backslash_escaped(content, index):
                buffer.append(char)
                index += 1
                continue
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            if in_double_quote and index + 1 < len(content) and content[index + 1] == '"':
                buffer.extend(['"', '"'])
                index += 2
                continue
            if is_backslash_escaped(content, index):
                buffer.append(char)
                index += 1
                continue
            in_double_quote = not in_double_quote

        if char == ";" and not in_single_quote and not in_double_quote:
            statement = "".join(buffer).strip()
            if statement:
                statements.append(statement)
            buffer = []
            index += 1
            continue

        buffer.append(char)
        index += 1

    tail = "".join(buffer).strip()
    if tail:
        statements.append(tail)
    return statements


def execute_cypher_file(session, cypher_path: Path) -> None:
    content = cypher_path.read_text(encoding="utf-8-sig")
    statements = split_cypher_statements(content)
    
    print(f"执行 {cypher_path.name}，共 {len(statements)} 条语句...")
    
    for i, statement in enumerate(statements, 1):
        if i % 10 == 0 or i == len(statements):
            print(f"  进度: {i}/{len(statements)}")
        session.run(statement).consume()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="导入三国演义知识图谱到 Neo4j")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="先清空数据库再导入",
    )
    args = parser.parse_args()

    settings = get_settings()
    if not settings.neo4j_uri or not settings.neo4j_username or not settings.neo4j_password:
        raise SystemExit("Neo4j connection settings are incomplete. Check backend/.env.")

    neo4j_dir = BACKEND_DIR / "neo4j"
    schema_file = neo4j_dir / "romance_schema.cypher"
    seed_file = neo4j_dir / "romance_seed.cypher"
    reset_file = neo4j_dir / "reset.cypher"

    if not schema_file.exists():
        raise SystemExit(f"找不到 {schema_file}，请先运行: python scripts/build_romance_graph.py")
    
    if not seed_file.exists():
        raise SystemExit(f"找不到 {seed_file}，请先运行: python scripts/build_romance_graph.py")

    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )

    try:
        driver.verify_connectivity()
        with driver.session(database=settings.neo4j_database) as session:
            if args.reset:
                print("🗑️  清空数据库...")
                execute_cypher_file(session, reset_file)
                print("✓ 清空完成\n")

            print("📐 导入三国演义 Schema...")
            execute_cypher_file(session, schema_file)
            print("✓ Schema 导入完成\n")

            print("📊 导入三国演义种子数据...")
            execute_cypher_file(session, seed_file)
            print("✓ 种子数据导入完成\n")
            
            print("✅ 三国演义知识图谱已成功导入！")
            print("\n你可以在 Neo4j Browser 中测试:")
            print("  http://localhost:7474")
            print("\n测试查询:")
            print("  MATCH (p:Person) RETURN p.name, p.popularity ORDER BY p.popularity DESC LIMIT 20;")
            print("  MATCH (p1:Person)-[r]-(p2:Person) RETURN p1.name, type(r), p2.name LIMIT 20;")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
