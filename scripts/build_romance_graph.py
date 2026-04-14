"""
三国演义知识图谱构建脚本

功能：
1. 读取三国演义 TXT 文件
2. 使用 spaCy 中文模型进行分词和实体识别
3. 基于预定义的实体名单和别名进行实体消歧
4. 基于共现关系提取人物关系
5. 生成 Neo4j Cypher 导入脚本

使用方法：
python scripts/build_romance_graph.py [--input data/三国演义.txt] [--output backend/neo4j]
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# 添加项目根目录到 path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import spacy

SYMMETRIC_RELATION_TYPES = {
    "ASSOCIATED_WITH",
    "ALLIED_WITH",
    "FOUGHT_AGAINST",
    "SWORN_BROTHERS",
}

PERSON_RELATION_RULES = [
    ("SWORN_BROTHERS", ("结义", "义兄弟", "桃园")),
    ("ALLIED_WITH", ("结盟", "同盟", "会盟", "联合", "联手", "同心协力")),
]
SERVICE_KEYWORDS = ("辅佐", "投奔", "归顺", "归降", "效力", "追随", "侍奉", "依附")
TITLE_KEYWORDS = ("拜", "封", "任", "授", "为", "加封", "册封")


def load_entity_map(entity_file: Path) -> dict:
    """加载实体别名映射表"""
    with open(entity_file, "r", encoding="utf-8") as f:
        return json.load(f)


def build_alias_index(entity_map: dict) -> dict[str, str]:
    """
    构建别名到标准名的索引
    
    返回: {别名: (标准名, 实体类型)}
    """
    alias_index = {}
    
    for entity_type in ["persons", "locations", "events", "titles"]:
        type_label = entity_type[:-1]  # persons -> person
        entities = entity_map.get(entity_type, {})
        
        for standard_name, info in entities.items():
            aliases = info.get("aliases", [])
            summary = info.get("summary", "")
            
            # 标准名本身也是别名
            alias_index[standard_name] = (standard_name, type_label, summary)
            
            # 添加其他别名
            for alias in aliases:
                alias_index[alias] = (standard_name, type_label, summary)
    
    return alias_index


def extract_entities_with_spacy(text: str, nlp, alias_index: dict[str, tuple]) -> list[dict]:
    """
    使用 spaCy 和别名索引提取实体
    
    策略：
    1. 先用别名索引做精确匹配（优先级高）
    2. 再用 spaCy NER 做补充
    """
    # 策略 1: 精确匹配别名
    found_entities = {}  # {实体位置: (标准名, 类型, summary)}
    
    # 按长度降序排序，优先匹配长别名
    sorted_aliases = sorted(alias_index.keys(), key=len, reverse=True)
    
    for alias in sorted_aliases:
        standard_name, entity_type, summary = alias_index[alias]
        # 查找所有出现位置
        for match in re.finditer(re.escape(alias), text):
            start, end = match.start(), match.end()
            # 如果这个位置没被占用，或者新实体更长（更具体）
            if start not in found_entities or len(alias) > len(found_entities[start][0]):
                found_entities[start] = (alias, standard_name, entity_type, summary, end)
    
    # 策略 2: 用 spaCy 补充识别未匹配的实体
    doc = nlp(text)
    for ent in doc.ents:
        if ent.start_char not in found_entities:
            # 检查是否在别名索引中
            ent_text = ent.text.strip()
            if ent_text in alias_index:
                standard_name, entity_type, summary = alias_index[ent_text]
                found_entities[ent.start_char] = (
                    ent_text, standard_name, entity_type, summary, ent.end_char
                )
    
    # 转换为列表并排序
    entities = []
    for start, (alias, standard_name, entity_type, summary, end) in sorted(found_entities.items()):
        entities.append({
            "text": alias,
            "standard_name": standard_name,
            "type": entity_type,
            "summary": summary,
            "start": start,
            "end": end,
        })
    
    return entities


def iter_text_segments(text: str) -> list[tuple[int, int, str]]:
    segments: list[tuple[int, int, str]] = []
    for match in re.finditer(r"[^。！？\n]+[。！？]?", text):
        segment_text = match.group().strip()
        if segment_text:
            segments.append((match.start(), match.end(), segment_text))
    return segments


def entities_in_range(
    entities: list[dict],
    start: int,
    end: int,
    *,
    entity_type: str | None = None,
) -> list[dict]:
    return [
        entity
        for entity in entities
        if entity["start"] >= start
        and entity["end"] <= end
        and (entity_type is None or entity["type"] == entity_type)
    ]


def group_entities_by_gap(entities: list[dict], max_gap: int = 500) -> list[list[dict]]:
    groups: list[list[dict]] = []
    current_group: list[dict] = []

    for entity in entities:
        if not current_group:
            current_group.append(entity)
        elif entity["start"] - current_group[-1]["end"] < max_gap:
            current_group.append(entity)
        else:
            groups.append(current_group)
            current_group = [entity]

    if current_group:
        groups.append(current_group)

    return groups


def normalize_relation_endpoints(
    source: str,
    target: str,
    source_type: str,
    target_type: str,
    relation_type: str,
) -> tuple[str, str, str, str]:
    if relation_type in SYMMETRIC_RELATION_TYPES and (source, source_type) > (target, target_type):
        return target, source, target_type, source_type
    return source, target, source_type, target_type


def build_relation(
    source: str,
    target: str,
    *,
    relation_type: str,
    source_type: str,
    target_type: str,
    confidence: float,
) -> dict | None:
    source, target, source_type, target_type = normalize_relation_endpoints(
        source, target, source_type, target_type, relation_type
    )
    if source == target and source_type == target_type:
        return None
    return {
        "source": source,
        "target": target,
        "source_type": source_type,
        "target_type": target_type,
        "type": relation_type,
        "confidence": confidence,
    }


def extract_cooccurrence_relations(
    entities: list[dict], 
    window_size: int = 200
) -> list[dict]:
    """
    基于共现窗口提取关系
    
    如果两个实体在 window_size 字符内同时出现，认为它们存在关系
    """
    relations = []
    relation_set = set()  # 去重
    
    for i, entity1 in enumerate(entities):
        # 只看 person 类型之间的关系
        if entity1["type"] != "person":
            continue
        
        # 在窗口内查找其他实体
        window_end = entity1["end"] + window_size
        
        for j in range(i + 1, len(entities)):
            entity2 = entities[j]
            
            # 超出窗口
            if entity2["start"] > window_end:
                break
            
            # 只看 person 类型
            if entity2["type"] != "person":
                continue
            
            # 避免自环
            if entity1["standard_name"] == entity2["standard_name"]:
                continue
            
            # 创建关系（去重）
            rel_key = tuple(sorted([entity1["standard_name"], entity2["standard_name"]]))
            if rel_key not in relation_set:
                relation_set.add(rel_key)
                relation = build_relation(
                    entity1["standard_name"],
                    entity2["standard_name"],
                    relation_type="ASSOCIATED_WITH",
                    source_type="person",
                    target_type="person",
                    confidence=0.5,
                )
                if relation:
                    relations.append(relation)
    
    return relations


def extract_location_relations(entities: list[dict]) -> list[dict]:
    """
    提取人物-地点关系
    
    如果人物和地点在同一段落出现，认为人物"位于"该地点
    """
    relations = []
    relation_set = set()
    
    paragraphs = group_entities_by_gap(entities, max_gap=500)
    
    # 提取人物-地点关系
    for paragraph in paragraphs:
        persons = [e for e in paragraph if e["type"] == "person"]
        locations = [e for e in paragraph if e["type"] == "location"]
        
        for person in persons:
            for location in locations:
                rel_key = (person["standard_name"], location["standard_name"])
                if rel_key not in relation_set:
                    relation_set.add(rel_key)
                    relation = build_relation(
                        person["standard_name"],
                        location["standard_name"],
                        relation_type="LOCATED_AT",
                        source_type="person",
                        target_type="location",
                        confidence=0.6,
                    )
                    if relation:
                        relations.append(relation)
    
    return relations


def extract_event_relations(entities: list[dict], known_locations: set[str]) -> list[dict]:
    relations = []
    relation_set = set()

    for paragraph in group_entities_by_gap(entities, max_gap=500):
        paragraph_events = [entity for entity in paragraph if entity["type"] == "event"]
        paragraph_persons = [entity for entity in paragraph if entity["type"] == "person"]
        paragraph_locations = [entity for entity in paragraph if entity["type"] == "location"]

        for event in paragraph_events:
            nearby_persons = [
                person
                for person in paragraph_persons
                if abs(person["start"] - event["start"]) <= 160
            ]
            if not nearby_persons:
                nearby_persons = paragraph_persons

            for person in nearby_persons:
                rel_key = (person["standard_name"], event["standard_name"], "PARTICIPATED_IN")
                if rel_key in relation_set:
                    continue
                relation_set.add(rel_key)
                relation = build_relation(
                    person["standard_name"],
                    event["standard_name"],
                    relation_type="PARTICIPATED_IN",
                    source_type="person",
                    target_type="event",
                    confidence=0.82,
                )
                if relation:
                    relations.append(relation)

            inferred_locations = set()
            for location_name in known_locations:
                if location_name in event["standard_name"]:
                    inferred_locations.add(location_name)

            nearby_locations = [
                location for location in paragraph_locations if abs(location["start"] - event["start"]) <= 80
            ]
            unique_nearby_location_names = {location["standard_name"] for location in nearby_locations}
            if not inferred_locations and len(unique_nearby_location_names) == 1:
                inferred_locations = unique_nearby_location_names

            for location_name in inferred_locations:
                rel_key = (event["standard_name"], location_name, "OCCURRED_IN")
                if rel_key in relation_set:
                    continue
                relation_set.add(rel_key)
                relation = build_relation(
                    event["standard_name"],
                    location_name,
                    relation_type="OCCURRED_IN",
                    source_type="event",
                    target_type="location",
                    confidence=0.88,
                )
                if relation:
                    relations.append(relation)

    return relations


def extract_title_relations(text: str, entities: list[dict]) -> list[dict]:
    relations = []
    relation_set = set()

    for start, end, sentence in iter_text_segments(text):
        sentence_persons = entities_in_range(entities, start, end, entity_type="person")
        sentence_titles = entities_in_range(entities, start, end, entity_type="title")
        if not sentence_persons or not sentence_titles:
            continue

        for person in sentence_persons:
            for title in sentence_titles:
                person_local_start = person["start"] - start
                title_local_start = title["start"] - start
                distance = abs(person_local_start - title_local_start)
                if distance > 16 and not any(keyword in sentence for keyword in TITLE_KEYWORDS):
                    continue

                rel_key = (person["standard_name"], title["standard_name"], "HELD_TITLE")
                if rel_key in relation_set:
                    continue
                relation_set.add(rel_key)
                relation = build_relation(
                    person["standard_name"],
                    title["standard_name"],
                    relation_type="HELD_TITLE",
                    source_type="person",
                    target_type="title",
                    confidence=0.78,
                )
                if relation:
                    relations.append(relation)
    
    return relations


def extract_person_keyword_relations(text: str, entities: list[dict]) -> list[dict]:
    relations = []
    relation_set = set()

    for start, end, sentence in iter_text_segments(text):
        sentence_persons = entities_in_range(entities, start, end, entity_type="person")
        if len(sentence_persons) < 2:
            continue

        unique_names = []
        seen_names = set()
        for person in sentence_persons:
            name = person["standard_name"]
            if name not in seen_names:
                seen_names.add(name)
                unique_names.append(name)

        if len(unique_names) < 2:
            continue

        matched_relation_types = {
            relation_type
            for relation_type, keywords in PERSON_RELATION_RULES
            if any(keyword in sentence for keyword in keywords)
        }

        for relation_type in matched_relation_types:
            for index, source in enumerate(unique_names):
                for target in unique_names[index + 1 :]:
                    rel_key = (source, target, relation_type)
                    if rel_key in relation_set:
                        continue
                    relation_set.add(rel_key)
                    relation = build_relation(
                        source,
                        target,
                        relation_type=relation_type,
                        source_type="person",
                        target_type="person",
                        confidence=0.84 if relation_type == "SWORN_BROTHERS" else 0.72,
                    )
                    if relation:
                        relations.append(relation)

        if len(unique_names) == 2 and any(keyword in sentence for keyword in SERVICE_KEYWORDS):
            source, target = unique_names
            rel_key = (source, target, "SERVED_UNDER")
            if rel_key not in relation_set:
                relation_set.add(rel_key)
                relation = build_relation(
                    source,
                    target,
                    relation_type="SERVED_UNDER",
                    source_type="person",
                    target_type="person",
                    confidence=0.7,
                )
                if relation:
                    relations.append(relation)
    
    return relations


def deduplicate_relations(relations: list[dict]) -> list[dict]:
    relation_map: dict[tuple[str, str, str, str, str], dict] = {}

    for relation in relations:
        key = (
            relation["source"],
            relation["target"],
            relation["source_type"],
            relation["target_type"],
            relation["type"],
        )
        existing = relation_map.get(key)
        if existing is None or relation.get("confidence", 0) > existing.get("confidence", 0):
            relation_map[key] = relation

    person_specific_pairs = {
        tuple(sorted((relation["source"], relation["target"])))
        for relation in relation_map.values()
        if relation["source_type"] == "person"
        and relation["target_type"] == "person"
        and relation["type"] != "ASSOCIATED_WITH"
    }

    filtered_relations = []
    for relation in relation_map.values():
        if (
            relation["type"] == "ASSOCIATED_WITH"
            and relation["source_type"] == "person"
            and relation["target_type"] == "person"
            and tuple(sorted((relation["source"], relation["target"]))) in person_specific_pairs
        ):
            continue
        filtered_relations.append(relation)

    return filtered_relations


def process_text_in_chunks(
    text: str, 
    nlp, 
    alias_index: dict[str, tuple],
    known_locations: set[str],
    chunk_size: int = 10000
) -> tuple[list[dict], list[dict]]:
    """
    分块处理大文本，避免内存溢出
    """
    all_entities = []
    all_relations = []
    
    # 按章节或固定大小分块
    chunks: list[tuple[int, str]] = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        # 尝试在章节标题处截断
        if i + chunk_size < len(text):
            # 查找最近的章节标题
            next_chapter = text.find("\n第", i + chunk_size - 500)
            if next_chapter != -1 and next_chapter < i + chunk_size + 500:
                chunk = text[i:next_chapter]
        
        chunks.append((i, chunk))
    
    print(f"文本已分为 {len(chunks)} 个块")
    
    for idx, (offset, chunk) in enumerate(chunks):
        print(f"处理第 {idx + 1}/{len(chunks)} 块...")
        
        # 提取实体
        entities = extract_entities_with_spacy(chunk, nlp, alias_index)
        # 调整位置偏移
        for entity in entities:
            entity["start"] += offset
            entity["end"] += offset
        
        all_entities.extend(entities)
        
        # 提取共现关系
        relations = extract_cooccurrence_relations(entities)
        all_relations.extend(relations)
        
        # 提取地点关系
        location_rels = extract_location_relations(entities)
        all_relations.extend(location_rels)

        # 提取人物-事件、事件-地点关系
        event_rels = extract_event_relations(entities, known_locations)
        all_relations.extend(event_rels)

        # 提取人物-官职关系
        title_rels = extract_title_relations(chunk, entities)
        all_relations.extend(title_rels)

        # 提取更细粒度的人物关系
        person_keyword_rels = extract_person_keyword_relations(chunk, entities)
        all_relations.extend(person_keyword_rels)
    
    return all_entities, all_relations


def deduplicate_entities(entities: list[dict]) -> list[dict]:
    """去重实体，保留每个标准名的一次出现"""
    seen = set()
    unique_entities = []
    
    for entity in entities:
        key = entity["standard_name"]
        if key not in seen:
            seen.add(key)
            unique_entities.append(entity)
    
    return unique_entities


def count_entity_occurrences(entities: list[dict]) -> dict[str, int]:
    """统计每个实体出现的次数"""
    counts = defaultdict(int)
    for entity in entities:
        counts[entity["standard_name"]] += 1
    return dict(counts)


def generate_cypher_schema(entity_types: list[str]) -> str:
    """生成 Neo4j schema 的 Cypher 语句"""
    cypher = "// 三国演义知识图谱 Schema\n\n"
    
    # 创建约束
    for entity_type in entity_types:
        type_upper = entity_type.upper()
        cypher += f"""// {type_upper} ID 唯一约束
CREATE CONSTRAINT {entity_type.lower()}_id_unique IF NOT EXISTS
FOR (n:{type_upper}) REQUIRE n.id IS UNIQUE;

"""
    
    # 创建索引
    cypher += "\n// 名称索引\n"
    for entity_type in entity_types:
        type_upper = entity_type.upper()
        cypher += f"""CREATE INDEX {entity_type.lower()}_name_index IF NOT EXISTS
FOR (n:{type_upper}) ON (n.name);

"""
    
    # 全文索引
    cypher += """
// 全文搜索索引
CREATE FULLTEXT INDEX romance_entity_fulltext IF NOT EXISTS
FOR (n:Person|Location|Event|Title)
ON EACH [n.name, n.summary];
"""
    
    return cypher


def generate_cypher_seed(
    entities: list[dict], 
    relations: list[dict], 
    occurrence_counts: dict[str, int]
) -> str:
    """生成 Neo4j 种子数据的 Cypher 语句"""
    cypher = "// 三国演义知识图谱种子数据\n\n"
    
    # 创建节点
    cypher += "// 创建人物节点\n"
    person_entities = [e for e in entities if e["type"] == "person"]
    for entity in person_entities:
        name = entity["standard_name"]
        summary = entity.get("summary", "")
        popularity = occurrence_counts.get(name, 1)
        
        cypher += f"""CREATE (:Person {{
  id: 'person_{name}',
  name: '{name}',
  type: 'Person',
  summary: '{summary}',
  popularity: {popularity}
}});
"""
    
    cypher += "\n// 创建地点节点\n"
    location_entities = [e for e in entities if e["type"] == "location"]
    for entity in location_entities:
        name = entity["standard_name"]
        cypher += f"""CREATE (:Location {{
  id: 'location_{name}',
  name: '{name}',
  type: 'Location',
  summary: '三国时期重要地点'
}});
"""
    
    cypher += "\n// 创建事件节点\n"
    event_entities = [e for e in entities if e["type"] == "event"]
    for entity in event_entities:
        name = entity["standard_name"]
        cypher += f"""CREATE (:Event {{
  id: 'event_{name}',
  name: '{name}',
  type: 'Event',
  summary: '三国时期重要事件'
}});
"""
    
    cypher += "\n// 创建官职节点\n"
    title_entities = [e for e in entities if e["type"] == "title"]
    for entity in title_entities:
        name = entity["standard_name"]
        cypher += f"""CREATE (:Title {{
  id: 'title_{name}',
  name: '{name}',
  type: 'Title',
  summary: '三国时期官职或封号'
}});
"""
    
    def build_entity_id(name: str, entity_type: str) -> str:
        type_prefix = {
            "person": "person",
            "location": "location",
            "event": "event",
            "title": "title",
        }.get(entity_type, entity_type)
        return f"{type_prefix}_{name}"

    # 创建关系
    cypher += "\n\n// 创建关系\n"
    for relation in relations:
        source = relation["source"]
        target = relation["target"]
        rel_type = relation["type"]
        confidence = relation.get("confidence", 0.5)
        source_type = relation.get("source_type", "person")
        target_type = relation.get("target_type", "person")
        
        source_id = build_entity_id(source, source_type)
        target_id = build_entity_id(target, target_type)
        
        cypher += f"""MATCH (a {{id: '{source_id}'}}), (b {{id: '{target_id}'}})
CREATE (a)-[:{rel_type} {{confidence: {confidence}, source: 'romance_txt'}}]->(b);
"""
    
    return cypher


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="从三国演义TXT构建知识图谱")
    parser.add_argument(
        "--input",
        type=str,
        default=str(PROJECT_ROOT / "data" / "三国演义.txt"),
        help="三国演义 TXT 文件路径",
    )
    parser.add_argument(
        "--entity-map",
        type=str,
        default=str(PROJECT_ROOT / "data" / "romance_entities.json"),
        help="实体别名映射表 JSON 文件",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(PROJECT_ROOT / "backend" / "neo4j"),
        help="输出 Cypher 文件目录",
    )
    args = parser.parse_args()
    
    input_file = Path(args.input)
    entity_map_file = Path(args.entity_map)
    output_dir = Path(args.output)
    
    # 检查输入文件
    if not input_file.exists():
        print(f"❌ 错误: 找不到输入文件 {input_file}")
        print(f"请将三国演义 TXT 文件放置在此路径，或使用 --input 参数指定")
        sys.exit(1)
    
    if not entity_map_file.exists():
        print(f"❌ 错误: 找不到实体映射表 {entity_map_file}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载实体映射
    print("📖 加载实体别名映射表...")
    entity_map = load_entity_map(entity_map_file)
    alias_index = build_alias_index(entity_map)
    known_locations = set(entity_map.get("locations", {}).keys())
    print(f"   已加载 {len(alias_index)} 个别名")
    
    # 读取文本
    print(f"📄 读取三国演义: {input_file}")
    text = input_file.read_text(encoding="utf-8")
    print(f"   文本长度: {len(text):,} 字符")
    
    # 加载 spaCy 模型
    print("🔧 加载 spaCy 中文模型...")
    try:
        nlp = spacy.load("zh_core_web_md")
        print("   ✓ zh_core_web_md 加载成功")
    except Exception as e:
        print(f"❌ 错误: 无法加载 spaCy 模型: {e}")
        print("   请运行: python -m spacy download zh_core_web_md")
        sys.exit(1)
    
    # 处理文本
    print("\n🔍 开始提取实体和关系...")
    entities, relations = process_text_in_chunks(text, nlp, alias_index, known_locations)
    
    # 去重和统计
    unique_entities = deduplicate_entities(entities)
    unique_relations = deduplicate_relations(relations)
    occurrence_counts = count_entity_occurrences(entities)
    
    print(f"\n📊 提取结果:")
    print(f"   实体总数（去重后）: {len(unique_entities)}")
    print(f"   关系总数: {len(unique_relations)}")
    
    # 按类型统计
    type_counts = defaultdict(int)
    for entity in unique_entities:
        type_counts[entity["type"]] += 1
    
    print(f"\n   按类型分布:")
    for type_name, count in sorted(type_counts.items()):
        print(f"     {type_name}: {count}")
    
    # 显示高频实体
    print(f"\n🏆 出现频率 TOP 20 实体:")
    sorted_entities = sorted(occurrence_counts.items(), key=lambda x: x[1], reverse=True)
    for name, count in sorted_entities[:20]:
        print(f"   {name}: {count} 次")
    
    # 生成 Cypher 文件
    print(f"\n💾 生成 Neo4j Cypher 文件...")
    
    # Schema
    schema_file = output_dir / "romance_schema.cypher"
    schema_cypher = generate_cypher_schema(["Person", "Location", "Event", "Title"])
    schema_file.write_text(schema_cypher, encoding="utf-8")
    print(f"   ✓ {schema_file}")
    
    # Seed data
    seed_file = output_dir / "romance_seed.cypher"
    seed_cypher = generate_cypher_seed(unique_entities, unique_relations, occurrence_counts)
    seed_file.write_text(seed_cypher, encoding="utf-8")
    print(f"   ✓ {seed_file}")
    
    # 保存中间结果（用于调试）
    debug_dir = PROJECT_ROOT / "data"
    entities_file = debug_dir / "entities.json"
    relations_file = debug_dir / "relationships.json"
    
    with open(entities_file, "w", encoding="utf-8") as f:
        json.dump(unique_entities, f, ensure_ascii=False, indent=2)
    print(f"   ✓ {entities_file}")
    
    with open(relations_file, "w", encoding="utf-8") as f:
        json.dump(unique_relations, f, ensure_ascii=False, indent=2)
    print(f"   ✓ {relations_file}")
    
    print(f"\n✅ 完成！")
    print(f"\n下一步:")
    print(f"1. 启动 Neo4j: docker compose up -d")
    print(f"2. 导入数据: python backend/scripts/init_neo4j.py --schema-only")
    print(f"3. 导入种子数据: python backend/scripts/init_neo4j.py --seed-only")
    print(f"4. 启动后端: cd backend && uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
