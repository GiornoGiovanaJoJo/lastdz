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

## Frontend тесты (React/Vitest)

### Установка зависимостей

```bash
cd frontend
npm install
```

### Запуск тестов

```bash
# Запуск всех тестов
npm test

# Запуск с UI интерфейсом
npm run test:ui

# Запуск с покрытием кода
npm run test:coverage

# Запуск в watch режиме (автоперезагрузка при изменении)
npm test -- --watch

# Запуск конкретного файла тестов
npm test -- App.test.tsx
```

### Структура frontend тестов

```
Frontend Tests (App.test.tsx)
├── Rendering
│   ├── should render the header
│   ├── should render upload section
│   └── should render empty state when no graph is loaded
├── File Upload
│   ├── should handle successful file upload
│   ├── should display error message on upload failure
│   └── should show loading state during upload
├── Filters
│   ├── should display filter section after graph loads
│   ├── should filter by environment
│   ├── should filter by node type
│   └── should filter by criticality
└── Tag Search
    └── should filter nodes by tags
```

### Примеры тестов

**Тест рендеринга:**
```typescript
it('should render the header', () => {
  render(<App />);
  expect(screen.getByText(/GraphML Visualizer/i)).toBeInTheDocument();
});
```

**Тест загрузки файла:**
```typescript
it('should handle successful file upload', async () => {
  const mockGraphData = { nodes: [...], edges: [...] };
  mockedAxios.post.mockResolvedValueOnce({ data: mockGraphData });

  render(<App />);
  const fileInput = screen.getByLabelText(/Choose File/i);
  await userEvent.upload(fileInput, file);

  await waitFor(() => {
    expect(screen.getByText(/Loaded: test.graphml/i)).toBeInTheDocument();
  });
});
```

## Запуск тестов в Docker

### Backend тесты в Docker

```bash
# Запуск контейнера backend с тестами
docker-compose -f docker-compose.test.yml up backend-test
```

### Frontend тесты в Docker

```bash
# Запуск контейнера frontend с тестами
docker-compose -f docker-compose.test.yml up frontend-test
```

## Покрытие кода (Code Coverage)

### Backend покрытие

```bash
cd backend
pytest --cov=main --cov-report=html --cov-report=term-missing

# Откройте htmlcov/index.html в браузере
```

### Frontend покрытие

```bash
cd frontend
npm run test:coverage

# Откройте coverage/index.html в браузере
```

## Лучшие практики тестирования

### ✅ DO (Делай)

1. **Тестируй поведение, не реализацию**
   ```typescript
   ✓ expect(screen.getByText('Error')).toBeInTheDocument();
   ✗ expect(component.state.error).toBe(true);
   ```

2. **Используй описательные имена тестов**
   ```typescript
   ✓ should display error message when file upload fails
   ✗ test upload error
   ```

3. **Тестируй граничные случаи (edge cases)**
   ```python
   - Empty input
   - Very large files
   - Invalid characters
   - Null/undefined values
   ```

4. **Мокируй внешние зависимости**
   ```typescript
   vi.mock('axios');
   mockedAxios.post.mockResolvedValueOnce({ data: {...} });
   ```

5. **Используй fixtures для общих данных**
   ```python
   @pytest.fixture
   def valid_graphml_content():
       return b"""<graphml>...</graphml>"""
   ```

### ❌ DON'T (Не делай)

1. **Не полагайся на внешние сервисы в тестах**
   ```python
   ✗ response = requests.get('http://real-api.com')
   ✓ mock_api = vi.mock('requests')
   ```

2. **Не используй жёсткие паузы (sleep)**
   ```python
   ✗ time.sleep(2)  # Плохо
   ✓ await waitFor(() => { ... })  # Хорошо
   ```

3. **Не тестируй приватные методы напрямую**
   ```python
   ✗ obj._private_method()
   ✓ obj.public_method() # который использует _private_method
   ```

4. **Не создавай зависимости между тестами**
   ```python
   ✗ test_a_must_run_before_test_b = True
   ✓ Каждый тест независим
   ```

## Отладка тестов

### Backend отладка

```bash
# Используй pytest -s чтобы видеть print statements
pytest -s test_main.py

# Используй --pdb для запуска отладчика при ошибке
pytest --pdb test_main.py
```

### Frontend отладка

```bash
# Используй screen.debug() для вывода DOM
screen.debug();

# Используй test:ui для визуального интерфейса
npm run test:ui
```

## CI/CD интеграция

Тесты должны запускаться автоматически при каждом commit/push:

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: cd frontend && npm install
      - run: cd frontend && npm test
```

## Полезные ресурсы

- [Pytest документация](https://docs.pytest.org/)
- [Vitest документация](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
