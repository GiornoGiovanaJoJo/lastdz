# 🐛 API Testing Guide

## 📮 Health Check

```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "status": "ok",
  "message": "GraphML Visualizer API v1.0.0",
  "endpoint": "/api/graphml-to-json"
}
```

---

## 📄 Upload GraphML File

### Using curl

```bash
curl -X POST http://localhost:8000/api/graphml-to-json \
  -F "file=@backend/sample.graphml"
```

### Using Python

```python
import requests

with open('backend/sample.graphml', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/api/graphml-to-json',
        files=files
    )
    print(response.json())
```

### Using JavaScript (axios)

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const formData = new FormData();
formData.append('file', fs.createReadStream('backend/sample.graphml'));

axios.post('http://localhost:8000/api/graphml-to-json', formData, {
  headers: formData.getHeaders()
}).then(response => {
  console.log(response.data);
});
```

---

## ✅ Success Response (200)

```json
{
  "nodes": [
    {
      "id": "api-gateway",
      "label": "API Gateway",
      "type": "service",
      "env": "prod",
      "domain": "platform",
      "tags": [
        "entrypoint",
        "auth",
        "rate-limit"
      ],
      "tier": "edge",
      "x": 0.0,
      "y": 0.0
    },
    {
      "id": "auth-service",
      "label": "Auth Service",
      "type": "service",
      "env": "prod",
      "domain": "security",
      "tags": [
        "oauth",
        "jwt"
      ],
      "tier": "core",
      "x": 200.0,
      "y": -120.0
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "api-gateway",
      "target": "auth-service",
      "label": "login/refresh",
      "kind": "sync",
      "criticality": "high",
      "protocol": "http",
      "weight": 2.0,
      "env": "prod",
      "tags": [
        "auth",
        "entry"
      ]
    }
  ]
}
```

---

## ❌ Error Response (400)

### Invalid file type
```bash
curl -X POST http://localhost:8000/api/graphml-to-json \
  -F "file=@README.md"
```

**Response (400):**
```json
{
  "detail": "File must have .graphml extension"
}
```

### Missing required field
```bash
# If GraphML node is missing 'label'
```

**Response (400):**
```json
{
  "detail": "Node 'api-gateway' missing required field: label"
}
```

### Invalid field value
```bash
# If node.type is not in {service, db, cache, queue, external}
```

**Response (400):**
```json
{
  "detail": "Node 'api-gateway' has invalid type 'invalid_type'. Allowed: service, db, cache, queue, external"
}
```

### Invalid edge reference
```bash
# If edge references non-existent node
```

**Response (400):**
```json
{
  "detail": "Edge service-1->unknown-node references missing node(s)"
}
```

### Invalid XML
```bash
curl -X POST http://localhost:8000/api/graphml-to-json \
  -F "file=@invalid.graphml"
```

**Response (400):**
```json
{
  "detail": "Invalid XML: syntax error: line 1, column 0"
}
```

---

## 📐 Interactive API Documentation

### Swagger UI
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

---

## 📛 Valid Enum Values

### Node Types
```
service | db | cache | queue | external
```

### Edge Kind
```
sync | async | stream
```

### Criticality
```
low | medium | high
```

### Environment
```
prod | stage | dev
```

---

## 📊 Sample GraphML Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns/graphml">
  <graph id="G" edgedefault="directed">
    <!-- Node with all fields -->
    <node id="api-gateway">
      <data key="label">API Gateway</data>
      <data key="type">service</data>
      <data key="env">prod</data>
      <data key="domain">platform</data>
      <data key="tier">edge</data>
      <data key="tags">entrypoint,auth,rate-limit</data>
      <data key="x">0</data>
      <data key="y">0</data>
    </node>

    <!-- Edge with all fields -->
    <edge source="api-gateway" target="auth-service">
      <data key="label">login/refresh</data>
      <data key="kind">sync</data>
      <data key="protocol">http</data>
      <data key="criticality">high</data>
      <data key="weight">2.0</data>
      <data key="env">prod</data>
      <data key="tags">auth,entry</data>
    </edge>
  </graph>
</graphml>
```

---

## 📚 Performance Notes

- **File size limit:** No hard limit (limited by uvicorn settings)
- **Max nodes:** Tested with 1000+ nodes
- **Max edges:** Tested with 5000+ edges
- **Response time:** <100ms for typical graphs
- **Memory usage:** ~50MB for sample graph

---

## 🔧 Debugging

### Enable detailed logging

```bash
uvicorn main:app --reload --port 8000 --log-level debug
```

### Check request/response

1. Open Browser DevTools (F12)
2. Go to Network tab
3. Upload file
4. Click request and inspect:
   - Request: multipart/form-data
   - Response: JSON with nodes and edges

### Test with simple GraphML

```bash
cat > /tmp/test.graphml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns/graphml">
  <graph id="G" edgedefault="directed">
    <node id="n1">
      <data key="label">Node 1</data>
      <data key="type">service</data>
    </node>
    <node id="n2">
      <data key="label">Node 2</data>
      <data key="type">db</data>
    </node>
    <edge source="n1" target="n2">
      <data key="label">calls</data>
      <data key="kind">sync</data>
      <data key="criticality">high</data>
    </edge>
  </graph>
</graphml>
EOF

curl -X POST http://localhost:8000/api/graphml-to-json \
  -F "file=@/tmp/test.graphml" | jq
```

---

## 🚀 Next Steps

- [📄 Main README](./README.md)
- [💱 Quickstart Guide](./QUICKSTART.md)
- [💻 Frontend Code](./frontend/src/)
- [💻 Backend Code](./backend/)
