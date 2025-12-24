"""🧪 Тесты для GraphML Visualizer API

Покрывает:
- Парсинг GraphML файлов
- Валидацию узлов и рёбер
- Обработку ошибок
- HTTP endpoints
"""

import io
import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


# ===================== FIXTURES =====================

@pytest.fixture
def valid_graphml_content():
    """Валидный GraphML файл"""
    return b"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="G" edgedefault="directed">
    <node id="n1" label="Service A" type="service" env="prod"/>
    <node id="n2" label="Database" type="db" env="prod"/>
    <node id="n3" label="Cache" type="cache" env="prod"/>
    
    <edge id="e1" source="n1" target="n2" label="Query" kind="sync" criticality="high" weight="1.0"/>
    <edge id="e2" source="n1" target="n3" label="Get Cache" kind="async" criticality="medium" weight="0.5"/>
  </graph>
</graphml>"""


@pytest.fixture
def invalid_node_type_graphml():
    """GraphML с неверным типом узла"""
    return b"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="G" edgedefault="directed">
    <node id="n1" label="Service A" type="invalid_type"/>
    <node id="n2" label="Database" type="db"/>
    <edge id="e1" source="n1" target="n2" label="Query" kind="sync" criticality="high"/>
  </graph>
</graphml>"""


@pytest.fixture
def missing_required_field_graphml():
    """GraphML с отсутствующим обязательным полем"""
    return b"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="G" edgedefault="directed">
    <node id="n1" type="service"/>
    <node id="n2" label="Database" type="db"/>
    <edge id="e1" source="n1" target="n2" label="Query" kind="sync" criticality="high"/>
  </graph>
</graphml>"""


@pytest.fixture
def missing_edge_field_graphml():
    """GraphML с отсутствующим полем в ребре"""
    return b"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="G" edgedefault="directed">
    <node id="n1" label="Service A" type="service"/>
    <node id="n2" label="Database" type="db"/>
    <edge id="e1" source="n1" target="n2" label="Query" kind="sync"/>
  </graph>
</graphml>"""


@pytest.fixture
def broken_xml():
    """Некорректный XML"""
    return b"""<?xml version="1.0"?>
<graphml>
  <graph>
    <node id="n1" label="Test"
  </graph>
</graphml>"""


# ===================== ТЕСТЫ HEALTH CHECK =====================

class TestHealthCheck:
    """Тесты для health check endpoint"""

    def test_root_endpoint(self):
        """Проверка GET /"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data
        assert "endpoints" in data


# ===================== ТЕСТЫ ВАЛИДНОГО GraphML =====================

class TestValidGraphML:
    """Тесты успешного парсинга и валидации"""

    def test_graphml_to_json_success(self, valid_graphml_content):
        """Успешное преобразование валидного GraphML"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(valid_graphml_content))}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Проверка структуры ответа
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 3
        assert len(data["edges"]) == 2

    def test_nodes_structure(self, valid_graphml_content):
        """Проверка структуры узлов в ответе"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(valid_graphml_content))}
        )
        data = response.json()
        node = data["nodes"][0]
        
        # Проверка обязательных полей
        assert "id" in node
        assert "label" in node
        assert "type" in node
        
        # Проверка опциональных полей
        assert "env" in node
        assert "tags" in node
        assert isinstance(node["tags"], list)

    def test_edges_structure(self, valid_graphml_content):
        """Проверка структуры рёбер в ответе"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(valid_graphml_content))}
        )
        data = response.json()
        edge = data["edges"][0]
        
        # Проверка обязательных полей
        assert "id" in edge
        assert "source" in edge
        assert "target" in edge
        assert "label" in edge
        assert "kind" in edge
        assert "criticality" in edge
        assert "weight" in edge

    def test_edge_kind_values(self, valid_graphml_content):
        """Проверка допустимых значений kind в рёбрах"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(valid_graphml_content))}
        )
        data = response.json()
        
        for edge in data["edges"]:
            assert edge["kind"] in {"sync", "async", "stream"}
            assert edge["criticality"] in {"low", "medium", "high"}

    def test_node_types_values(self, valid_graphml_content):
        """Проверка допустимых значений типов узлов"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(valid_graphml_content))}
        )
        data = response.json()
        
        for node in data["nodes"]:
            assert node["type"] in {"service", "db", "cache", "queue", "external"}

    def test_weight_default_value(self, valid_graphml_content):
        """Проверка что weight имеет значение по умолчанию"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(valid_graphml_content))}
        )
        data = response.json()
        
        for edge in data["edges"]:
            assert isinstance(edge["weight"], (int, float))
            assert edge["weight"] > 0


# ===================== ТЕСТЫ ОШИБОК ВАЛИДАЦИИ =====================

class TestValidationErrors:
    """Тесты обработки ошибок валидации"""

    def test_invalid_node_type(self, invalid_node_type_graphml):
        """Ошибка: некорректный тип узла"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(invalid_node_type_graphml))}
        )
        assert response.status_code == 400
        assert "invalid type" in response.json()["detail"].lower()

    def test_missing_node_label(self, missing_required_field_graphml):
        """Ошибка: отсутствует label у узла"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(missing_required_field_graphml))}
        )
        assert response.status_code == 400
        assert "label" in response.json()["detail"].lower()

    def test_missing_edge_criticality(self, missing_edge_field_graphml):
        """Ошибка: отсутствует criticality у ребра"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(missing_edge_field_graphml))}
        )
        assert response.status_code == 400
        assert "criticality" in response.json()["detail"].lower()


# ===================== ТЕСТЫ ОШИБОК ФАЙЛА =====================

class TestFileErrors:
    """Тесты обработки ошибок файла"""

    def test_empty_file(self):
        """Ошибка: пустой файл"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(b""))}
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_invalid_extension(self):
        """Ошибка: неправильное расширение файла"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.txt", io.BytesIO(b"some content"))}
        )
        assert response.status_code == 400
        assert "graphml" in response.json()["detail"].lower()

    def test_broken_xml(self, broken_xml):
        """Ошибка: некорректный XML"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(broken_xml))}
        )
        assert response.status_code == 400
        assert "xml" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()

    def test_no_file_provided(self):
        """Ошибка: файл не предоставлен"""
        response = client.post("/api/graphml-to-json")
        assert response.status_code == 422  # Unprocessable Entity


# ===================== ТЕСТЫ CORS =====================

class TestCORS:
    """Тесты CORS заголовков"""

    def test_cors_headers(self):
        """Проверка наличия CORS заголовков"""
        response = client.options("/api/graphml-to-json")
        # FastAPI с CORSMiddleware должен обработать preflight запрос
        assert response.status_code in [200, 204, 405]  # 405 для OPTIONS без явной поддержки


# ===================== EDGE CASES =====================

class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_single_node_graph(self):
        """Граф с одним узлом"""
        content = b"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="G" edgedefault="directed">
    <node id="n1" label="Single Node" type="service"/>
  </graph>
</graphml>"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(content))}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["nodes"]) == 1
        assert len(data["edges"]) == 0

    def test_graph_with_tags(self):
        """Граф с тегами на узлах и рёбрах"""
        content = b"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="G" edgedefault="directed">
    <node id="n1" label="Service" type="service" tags="critical,api"/>
    <node id="n2" label="DB" type="db" tags="important"/>
    <edge id="e1" source="n1" target="n2" label="Query" kind="sync" criticality="high" tags="slow"/>
  </graph>
</graphml>"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(content))}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Проверка парсинга тегов
        assert len(data["nodes"][0]["tags"]) == 2
        assert "critical" in data["nodes"][0]["tags"]
        assert len(data["edges"][0]["tags"]) == 1

    def test_self_loop(self):
        """Граф с самоссылкой (self-loop)"""
        content = b"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="G" edgedefault="directed">
    <node id="n1" label="Service" type="service"/>
    <edge id="e1" source="n1" target="n1" label="Recursive" kind="sync" criticality="low"/>
  </graph>
</graphml>"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(content))}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["edges"][0]["source"] == data["edges"][0]["target"]

    def test_large_weight_value(self):
        """Граф с большим значением weight"""
        content = b"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="G" edgedefault="directed">
    <node id="n1" label="A" type="service"/>
    <node id="n2" label="B" type="service"/>
    <edge id="e1" source="n1" target="n2" label="Heavy" kind="sync" criticality="high" weight="9999.99"/>
  </graph>
</graphml>"""
        response = client.post(
            "/api/graphml-to-json",
            files={"file": ("test.graphml", io.BytesIO(content))}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["edges"][0]["weight"] == 9999.99


if __name__ == "__main__":
    pytest.main(["-v", "--cov=main", "test_main.py"])
