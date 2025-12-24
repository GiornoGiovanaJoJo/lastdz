import { useState, useMemo } from 'react';
import axios from 'axios';
import GraphView from './GraphView';

type NodeType = 'service' | 'db' | 'cache' | 'queue' | 'external';
type EdgeKind = 'sync' | 'async' | 'stream';
type Criticality = 'low' | 'medium' | 'high';

interface Node {
  id: string;
  label: string;
  type: NodeType;
  env?: string;
  domain?: string;
  tags?: string[];
  tier?: string;
  x?: number | null;
  y?: number | null;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  label: string;
  kind: EdgeKind;
  criticality: Criticality;
  protocol?: string;
  weight: number;
  env?: string;
  tags?: string[];
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

const API_BASE = 'http://127.0.0.1:8000';

function App() {
  const [graph, setGraph] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  // Filters
  const [envFilter, setEnvFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [criticalityFilter, setCriticalityFilter] = useState<string>('all');
  const [tagQuery, setTagQuery] = useState<string>('');

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setFileName(file.name);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post<GraphData>(
        `${API_BASE}/api/graphml-to-json`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      );
      setGraph(res.data);
    } catch (err: any) {
      console.error(err);
      const errorMessage =
        err?.response?.data?.detail ||
        err?.message ||
        'Failed to upload and parse file';
      setError(errorMessage);
      setGraph(null);
    } finally {
      setLoading(false);
    }
  };

  // Filtering logic
  const filteredGraph = useMemo(() => {
    if (!graph) return null;

    const tagQ = tagQuery.trim().toLowerCase();

    const nodes = graph.nodes.filter((n) => {
      if (envFilter !== 'all' && n.env !== envFilter) return false;
      if (typeFilter !== 'all' && n.type !== typeFilter) return false;
      if (tagQ) {
        const tags = n.tags || [];
        const match = tags.some((t) => t.toLowerCase().includes(tagQ));
        if (!match) return false;
      }
      return true;
    });

    const nodeIds = new Set(nodes.map((n) => n.id));
    const edges = graph.edges.filter((e) => {
      if (!nodeIds.has(e.source) || !nodeIds.has(e.target)) return false;
      if (criticalityFilter !== 'all' && e.criticality !== criticalityFilter)
        return false;
      if (envFilter !== 'all' && e.env && e.env !== envFilter) return false;
      if (tagQ) {
        const tags = e.tags || [];
        const match = tags.some((t) => t.toLowerCase().includes(tagQ));
        if (!match) return false;
      }
      return true;
    });

    return { nodes, edges };
  }, [graph, envFilter, typeFilter, criticalityFilter, tagQuery]);

  return (
    <div>
      <div className="header">
        <div className="container">
          <h1>📄 GraphML Visualizer</h1>
          <p>Upload and visualize your GraphML files with interactive graph visualization</p>
        </div>
      </div>

      <div className="container">
        {/* Upload Section */}
        <div className="card">
          <h2>📋 Upload GraphML File</h2>
          <div className="upload-section">
            <div className="file-input-wrapper">
              <label htmlFor="file-input" className="file-label">
                📁 Choose File
              </label>
              <input
                id="file-input"
                type="file"
                accept=".graphml"
                onChange={handleFileChange}
                disabled={loading}
              />
            </div>
            {loading && <span className="status-text loading">⚠️ Loading...</span>}
            {error && <span className="status-text error">❌ Error: {error}</span>}
            {graph && fileName && (
              <span className="status-text success">
                ✅ Loaded: {fileName} ({graph.nodes.length} nodes, {graph.edges.length} edges)
              </span>
            )}
          </div>
        </div>

        {/* Filters Section */}
        {graph && (
          <>
            <div className="card">
              <h2>🗐️ Filters</h2>
              <div className="filters-section">
                <div className="filter-group">
                  <label htmlFor="env-filter">Environment</label>
                  <select
                    id="env-filter"
                    value={envFilter}
                    onChange={(e) => setEnvFilter(e.target.value)}
                  >
                    <option value="all">All</option>
                    <option value="prod">Production</option>
                    <option value="stage">Staging</option>
                    <option value="dev">Development</option>
                  </select>
                </div>

                <div className="filter-group">
                  <label htmlFor="type-filter">Node Type</label>
                  <select
                    id="type-filter"
                    value={typeFilter}
                    onChange={(e) => setTypeFilter(e.target.value)}
                  >
                    <option value="all">All</option>
                    <option value="service">Service</option>
                    <option value="db">Database</option>
                    <option value="cache">Cache</option>
                    <option value="queue">Queue</option>
                    <option value="external">External</option>
                  </select>
                </div>

                <div className="filter-group">
                  <label htmlFor="criticality-filter">Edge Criticality</label>
                  <select
                    id="criticality-filter"
                    value={criticalityFilter}
                    onChange={(e) => setCriticalityFilter(e.target.value)}
                  >
                    <option value="all">All</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>

                <div className="filter-group">
                  <label htmlFor="tag-search">Search Tags</label>
                  <input
                    id="tag-search"
                    type="text"
                    value={tagQuery}
                    onChange={(e) => setTagQuery(e.target.value)}
                    placeholder="Search by tag..."
                  />
                </div>
              </div>
            </div>

            {/* Graph Section */}
            <GraphView graph={filteredGraph || graph} />
          </>
        )}

        {/* Empty State */}
        {!graph && (
          <div className="card empty-state">
            <h3>🔍 No Graph Loaded</h3>
            <p>Upload a GraphML file to get started. The file should contain nodes and edges definitions.</p>
            <p style={{ marginTop: '12px', fontSize: '12px', color: '#9ca3af' }}>
              Example: service nodes with type: service, db, cache, queue, external<br />
              Edge connections with kind: sync, async, stream
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
