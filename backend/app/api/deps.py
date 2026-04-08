from fastapi import Request

from app.services.graph_service import GraphService


def get_graph_service(request: Request) -> GraphService:
    return request.app.state.graph_service
