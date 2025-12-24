from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
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


def parse_graphml_xml(content: bytes) -> Dict[str, Any]:
    """
    Парсит GraphML используя XML парсер напрямую
    Извлекает атрибуты из <data> элементов внутри узлов/рёбер
    и также из прямых атрибутов элементов
    """
    root = ET.fromstring(content)
    
    # Регистрируем namespace
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}
    
    # Ищем элементы без namespace (если их нет)
    graph = root.find('.//graph')
    if graph is None:
        # Пробуем с namespace
        graph = root.find('.//g:graph', ns)
    
    if graph is None:
        raise ValueError("Graph element not found")
    
    nodes_dict = {}
    edges_list = []
    
    # Парсим узлы
    for node_elem in graph.findall('.//node') + graph.findall('.//g:node', ns):
        node_id = node_elem.get('id')
        if not node_id:
            continue
        
        node_data = {'id': node_id}
        
        # Извлекаем data элементы
        for data_elem in node_elem.findall('data') + node_elem.findall('g:data', ns):
            key = data_elem.get('key')
            value = data_elem.text or data_elem.get('value', '')
            if key and value:
                node_data[key] = value
        
        # Также проверяем атрибуты напрямую на элементе
        for attr in ['label', 'type', 'env', 'domain', 'tags', 'tier', 'x', 'y']:
            if attr not in node_data and node_elem.get(attr):
                node_data[attr] = node_elem.get(attr)
        
        nodes_dict[node_id] = node_data
    
    # Парсим рёбра
    for edge_elem in graph.findall('.//edge') + graph.findall('.//g:edge', ns):
        edge_id = edge_elem.get('id')
        source = edge_elem.get('source')
        target = edge_elem.get('target')
        
        if not (edge_id and source and target):
            continue
        
        edge_data = {'id': edge_id, 'source': source, 'target': target}
        
        # Извлекаем data элементы
        for data_elem in edge_elem.findall('data') + edge_elem.findall('g:data', ns):
            key = data_elem.get('key')
            value = data_elem.text or data_elem.get('value', '')
            if key and value:
                edge_data[key] = value
        
        # Также проверяем атрибуты напрямую на элементе
        for attr in ['label', 'kind', 'criticality', 'protocol', 'env', 'tags', 'weight']:
            if attr not in edge_data and edge_elem.get(attr):
                edge_data[attr] = edge_elem.get(attr)
        
        edges_list.append(edge_data)
    
    return {
        'nodes': nodes_dict,
        'edges': edges_list
    }


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "message": "GraphML Visualizer API v1.0.0",
        "endpoints": {
            "api": "/api/graphml-to-json",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.post("/api/graphml-to-json")
async def graphml_to_json(file: UploadFile = File(...)):
    """
    Преобразование GraphML файла в JSON
    
    1. Валидирует XML структуру
    2. Парсит GraphML и извлекает узлы/рёбра
    3. Проверяет обязательные поля и значения
    4. Возвращает JSON с nodes и edges
    """
    
    # Проверка расширения файла
    if not file.filename.lower().endswith(".graphml"):
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
    
    # Парсинг GraphML
    try:
        parsed = parse_graphml_xml(content)
        nodes_dict = parsed['nodes']
        edges_list = parsed['edges']
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid GraphML: {str(e)}"
        )
    
    # Валидация узлов
    node_ids = set(nodes_dict.keys())
    nodes_output = []
    
    for node_id, node_data in nodes_dict.items():
        label = node_data.get("label")
        ntype = node_data.get("type")
        
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
        env = node_data.get("env")
        domain = node_data.get("domain")
        tags_str = node_data.get("tags", "")
        tags = parse_tags(tags_str)
        tier = node_data.get("tier")
        x = to_float(node_data.get("x"))
        y = to_float(node_data.get("y"))
        
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
    
    for edge_idx, edge_data in enumerate(edges_list, start=1):
        u = edge_data.get("source")
        v = edge_data.get("target")
        
        # Проверка существования узлов
        if u not in node_ids or v not in node_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Edge {u}->{v} references missing node(s)"
            )
        
        label = edge_data.get("label")
        kind = edge_data.get("kind")
        criticality = edge_data.get("criticality")
        
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
        protocol = edge_data.get("protocol")
        env = edge_data.get("env")
        tags_str = edge_data.get("tags", "")
        tags = parse_tags(tags_str)
        
        # Вес ребра - обработка ошибок
        weight_val = edge_data.get("weight")
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
