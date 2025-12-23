from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import networkx as nx
from xml.etree import ElementTree as ET
import io

app = FastAPI(
    title="GraphML Visualizer API",
    description="API для парсинга и валидации GraphML файлов",
    version="1.0.0"
)

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Допустимые значения
ALLOWED_NODE_TYPES = {"service", "db", "cache", "queue", "external"}
ALLOWED_EDGE_KINDS = {"sync", "async", "stream"}
ALLOWED_CRITICALITY = {"low", "medium", "high"}


def validate_xml(content: bytes) -> None:
    """Валидация XML структуры"""
    try:
        ET.fromstring(content)
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Invalid XML: {str(e)}")


def to_float(value) -> Optional[float]:
    """Конвертация в float с обработкой ошибок"""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_tags(tags_str: str) -> List[str]:
    """Парсинг тегов из строки"""
    if not tags_str:
        return []
    return [t.strip() for t in tags_str.split(",") if t.strip()]


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "message": "GraphML Visualizer API v1.0.0",
        "endpoint": "/api/graphml-to-json"
    }


@app.post("/api/graphml-to-json")
async def graphml_to_json(file: UploadFile = File(...)):
    """
    Преобразование GraphML файла в JSON
    
    1. Валидирует XML структуру
    2. Парсит с помощью networkx
    3. Проверяет обязательные поля и значения
    4. Возвращает JSON с nodes и edges
    """
    
    # Проверка расширения файла
    if not file.filename.endswith(".graphml"):
        raise HTTPException(
            status_code=400,
            detail="File must have .graphml extension"
        )
    
    # Чтение содержимого
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    
    # Валидация как XML
    validate_xml(content)
    
    # Парсинг GraphML с помощью networkx
    try:
        G = nx.read_graphml(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid GraphML: {str(e)}"
        )
    
    # Валидация узлов
    node_ids = set(G.nodes())
    nodes_output = []
    
    for node_id, data in G.nodes(data=True):
        label = data.get("label")
        ntype = data.get("type")
        
        # Проверка обязательных полей
        if not label:
            raise HTTPException(
                status_code=400,
                detail=f"Node '{node_id}' missing required field: label"
            )
        if not ntype:
            raise HTTPException(
                status_code=400,
                detail=f"Node '{node_id}' missing required field: type"
            )
        
        # Проверка допустимого значения type
        if ntype not in ALLOWED_NODE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Node '{node_id}' has invalid type '{ntype}'. "
                       f"Allowed: {', '.join(ALLOWED_NODE_TYPES)}"
            )
        
        # Опциональные поля
        env = data.get("env")
        domain = data.get("domain")
        tags_str = data.get("tags", "")
        tags = parse_tags(tags_str)
        tier = data.get("tier")
        x = to_float(data.get("x"))
        y = to_float(data.get("y"))
        
        nodes_output.append({
            "id": node_id,
            "label": label,
            "type": ntype,
            "env": env,
            "domain": domain,
            "tags": tags,
            "tier": tier,
            "x": x,
            "y": y,
        })
    
    # Валидация рёбер
    edges_output = []
    
    for edge_idx, (u, v, data) in enumerate(G.edges(data=True), start=1):
        # Проверка существования узлов
        if u not in node_ids or v not in node_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Edge {u}->{v} references missing node(s)"
            )
        
        label = data.get("label")
        kind = data.get("kind")
        criticality = data.get("criticality")
        
        # Проверка обязательных полей
        if not label:
            raise HTTPException(
                status_code=400,
                detail=f"Edge {u}->{v} missing required field: label"
            )
        if not kind:
            raise HTTPException(
                status_code=400,
                detail=f"Edge {u}->{v} missing required field: kind"
            )
        if not criticality:
            raise HTTPException(
                status_code=400,
                detail=f"Edge {u}->{v} missing required field: criticality"
            )
        
        # Проверка допустимых значений
        if kind not in ALLOWED_EDGE_KINDS:
            raise HTTPException(
                status_code=400,
                detail=f"Edge {u}->{v} has invalid kind '{kind}'. "
                       f"Allowed: {', '.join(ALLOWED_EDGE_KINDS)}"
            )
        
        if criticality not in ALLOWED_CRITICALITY:
            raise HTTPException(
                status_code=400,
                detail=f"Edge {u}->{v} has invalid criticality '{criticality}'. "
                       f"Allowed: {', '.join(ALLOWED_CRITICALITY)}"
            )
        
        # Опциональные поля
        protocol = data.get("protocol")
        env = data.get("env")
        tags_str = data.get("tags", "")
        tags = parse_tags(tags_str)
        
        # Вес ребра
        weight_val = data.get("weight")
        try:
            weight = float(weight_val) if weight_val is not None else 1.0
        except (ValueError, TypeError):
            weight = 1.0
        
        edges_output.append({
            "id": f"e{edge_idx}",
            "source": u,
            "target": v,
            "label": label,
            "kind": kind,
            "criticality": criticality,
            "protocol": protocol,
            "weight": weight,
            "env": env,
            "tags": tags,
        })
    
    return {
        "nodes": nodes_output,
        "edges": edges_output
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
