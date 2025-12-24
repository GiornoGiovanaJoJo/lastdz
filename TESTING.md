# 🧪 Тестирование GraphML Visualizer

Полное руководство по запуску и разработке тестов для приложения.

## Backend тесты (Python/pytest)

### Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### Запуск тестов

```bash
# Запуск всех тестов
pytest -v

# Запуск с покрытием кода
pytest --cov=main --cov-report=html

# Запуск конкретного класса тестов
pytest test_main.py::TestValidGraphML -v

# Запуск с вывод информации о производительности
pytest -v --durations=10
```

### Структура backend тестов

```
Backend Tests (test_main.py)
├── TestHealthCheck
│   └── test_root_endpoint - Проверка GET /
├── TestValidGraphML (успешный парсинг)
│   ├── test_graphml_to_json_success - Основной тест парсинга
│   ├── test_nodes_structure - Структура узлов
│   ├── test_edges_structure - Структура рёбер
│   ├── test_edge_kind_values - Валидные значения kind
│   ├── test_node_types_values - Валидные типы узлов
│   └── test_weight_default_value - Значение weight по умолчанию
├── TestValidationErrors (ошибки валидации)
│   ├── test_invalid_node_type - Неверный тип узла
│   ├── test_missing_node_label - Отсутствует label
│   └── test_missing_edge_criticality - Отсутствует criticality
├── TestFileErrors (ошибки файла)
│   ├── test_empty_file - Пустой файл
│   ├── test_invalid_extension - Неправильное расширение
│   ├── test_broken_xml - Некорректный XML
│   └── test_no_file_provided - Файл не предоставлен
├── TestCORS
│   └── test_cors_headers - CORS заголовки
└── TestEdgeCases (граничные случаи)
    ├── test_single_node_graph - Граф с одним узлом
    ├── test_graph_with_tags - Граф с тегами
    ├── test_self_loop - Самоссылка
    └── test_large_weight_value - Большое значение weight
```

### Примеры тестов

**Тест успешного парсинга:**
```python
def test_graphml_to_json_success(self, valid_graphml_content):
    response = client.post(
        "/api/graphml-to-json",
        files={"file": ("test.graphml", io.BytesIO(valid_graphml_content))}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) == 3
    assert len(data["edges"]) == 2
```

**Тест обработки ошибок:**
```python
def test_invalid_node_type(self, invalid_node_type_graphml):
    response = client.post(
        "/api/graphml-to-json",
        files={"file": ("test.graphml", io.BytesIO(invalid_node_type_graphml))}
    )
    assert response.status_code == 400
    assert "invalid type" in response.json()["detail"].lower()
```



## Запуск тестов в Docker

### Backend тесты в Docker

```bash
# Запуск контейнера backend с тестами
docker-compose -f docker-compose.test.yml up backend-test
```

## Покрытие кода (Code Coverage)

### Backend покрытие

```bash
cd backend
pytest --cov=main --cov-report=html --cov-report=term-missing

# Откройте htmlcov/index.html в браузере
```
