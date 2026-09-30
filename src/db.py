"""Kết nối Neo4j."""
from src import config

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        from neo4j import GraphDatabase

        _driver = GraphDatabase.driver(
            config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
    return _driver


def run(query, **params):
    """Chạy một câu Cypher và trả về list[dict]."""
    with get_driver().session(database=config.NEO4J_DATABASE) as s:
        return s.run(query, **params).data()


def is_online():
    try:
        get_driver().verify_connectivity()
        return True
    except Exception:  # noqa: BLE001
        return False
