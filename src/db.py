"""Kết nối Neo4j."""
import time

from src import config

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        from neo4j import GraphDatabase

        _driver = GraphDatabase.driver(
            config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD),
            # Neo4j Aura tự đóng kết nối để lâu không dùng -> chủ động thay kết nối mới
            max_connection_lifetime=600,
        )
    return _driver


def run(query, **params):
    """Chạy một câu Cypher và trả về list[dict].

    Thử lại tối đa 3 lần nếu kết nối bị rớt (hay gặp với Neo4j Aura sau một lúc không dùng).
    """
    from neo4j.exceptions import ServiceUnavailable, SessionExpired

    for lan in range(3):
        try:
            with get_driver().session(database=config.NEO4J_DATABASE) as s:
                return s.run(query, **params).data()
        except (ServiceUnavailable, SessionExpired):
            if lan == 2:
                raise
            time.sleep(0.5 * (lan + 1))


def is_online():
    try:
        get_driver().verify_connectivity()
        return True
    except Exception:  # noqa: BLE001
        return False
