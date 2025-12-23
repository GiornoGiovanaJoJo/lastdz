import { useEffect, useRef } from 'react';
import { Network } from 'vis-network/standalone/esm/vis-network.js';
import { DataSet } from 'vis-data/standalone/esm/vis-data.js';

interface Node {
  id: string;
  label: string;
  type: string;
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
  kind: string;
  criticality: string;
  protocol?: string;
  weight: number;
  env?: string;
  tags?: string[];
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

interface GraphViewProps {
  graph: GraphData | null;
}

const typeColors: { [key: string]: string } = {
  service: '#2563eb',
  db: '#16a34a',
  cache: '#22c55e',
  queue: '#a855f7',
  external: '#6b7280',
};

const criticalityColors: { [key: string]: string } = {
  high: '#dc2626',
  medium: '#f59e0b',
  low: '#10b981',
};

const GraphView = ({ graph }: GraphViewProps) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const networkRef = useRef<Network | null>(null);

  useEffect(() => {
    if (!containerRef.current || !graph) return;

    // Подготовка узлов
    const nodesWithPos = graph.nodes.map((n) => ({
      id: n.id,
      label: n.label,
      group: n.type,
      x: n.x ?? undefined,
      y: n.y ?? undefined,
      fixed: n.x != null && n.y != null,
      title: `
        <div style="font-size: 13px; min-width: 200px;">
          <b>${n.label}</b><br/>
          <hr style="border: none; border-top: 1px solid #ddd; margin: 6px 0;"/>
          <div><strong>Type:</strong> ${n.type}</div>
          ${n.env ? `<div><strong>Env:</strong> ${n.env}</div>` : ''}
          ${n.domain ? `<div><strong>Domain:</strong> ${n.domain}</div>` : ''}
          ${n.tier ? `<div><strong>Tier:</strong> ${n.tier}</div>` : ''}
          ${n.tags && n.tags.length > 0 ? `<div><strong>Tags:</strong> ${n.tags.join(', ')}</div>` : ''}
        </div>
      `,
      font: {
        size: 14,
        face: 'system-ui',
        color: '#ffffff',
        bold: {
          color: '#ffffff',
          size: 14,
        },
      },
    }));

    // Подготовка рёбер
    const edgesData = graph.edges.map((e) => ({
      id: e.id,
      from: e.source,
      to: e.target,
      label: e.label,
      title: `
        <div style="font-size: 13px; min-width: 200px;">
          <b>${e.label}</b><br/>
          <hr style="border: none; border-top: 1px solid #ddd; margin: 6px 0;"/>
          <div><strong>Kind:</strong> ${e.kind}</div>
          <div><strong>Criticality:</strong> <span style="color: ${criticalityColors[e.criticality]}; font-weight: bold;">${e.criticality}</span></div>
          ${e.protocol ? `<div><strong>Protocol:</strong> ${e.protocol}</div>` : ''}
          <div><strong>Weight:</strong> ${e.weight}</div>
          ${e.env ? `<div><strong>Env:</strong> ${e.env}</div>` : ''}
          ${e.tags && e.tags.length > 0 ? `<div><strong>Tags:</strong> ${e.tags.join(', ')}</div>` : ''}
        </div>
      `,
      arrows: {
        to: {
          enabled: true,
          scaleFactor: 0.5,
        },
      },
      width: (e.weight || 1) * 1.5,
      color: {
        color: criticalityColors[e.criticality] || '#6b7280',
        opacity: 0.8,
      },
      font: {
        size: 12,
        face: 'system-ui',
        color: '#1f2937',
        background: {
          enabled: true,
          color: 'white',
        },
      },
      smooth: {
        type: 'continuous',
        roundness: 0.5,
      },
    }));

    // Подготовка данных
    const data = {
      nodes: new DataSet(nodesWithPos),
      edges: new DataSet(edgesData),
    };

    // Опции сети
    const options: any = {
      autoResize: true,
      physics: {
        enabled: true,
        stabilization: {
          iterations: 200,
          fit: true,
        },
        barnesHut: {
          gravitationalConstant: -50000,
          centralGravity: 0.3,
          springLength: 200,
          springConstant: 0.05,
        },
      },
      nodes: {
        shape: 'box',
        margin: 10,
        widthConstraint: {
          maximum: 200,
        },
        borderWidth: 2,
        borderWidthSelected: 3,
        shadow: {
          enabled: true,
          color: 'rgba(0,0,0,0.2)',
          size: 10,
          x: 5,
          y: 5,
        },
      },
      groups: {
        service: {
          color: {
            background: typeColors.service,
            highlight: {
              background: '#1d4ed8',
            },
          },
        },
        db: {
          color: {
            background: typeColors.db,
            highlight: {
              background: '#15803d',
            },
          },
        },
        cache: {
          color: {
            background: typeColors.cache,
            highlight: {
              background: '#16a34a',
            },
          },
        },
        queue: {
          color: {
            background: typeColors.queue,
            highlight: {
              background: '#9333ea',
            },
          },
        },
        external: {
          color: {
            background: typeColors.external,
            highlight: {
              background: '#4b5563',
            },
          },
        },
      },
      edges: {
        smooth: true,
      },
      interaction: {
        hover: true,
        navigationButtons: true,
        keyboard: true,
        tooltipDelay: 200,
        hideEdgesOnDrag: true,
      },
      layout: {
        randomSeed: 42,
      },
    };

    if (networkRef.current) {
      networkRef.current.destroy();
    }

    networkRef.current = new Network(containerRef.current, data, options);
  }, [graph]);

  return (
    <div className="graph-container">
      <h2>📊 Graph Visualization</h2>
      <div id="graph-visualization" ref={containerRef} />
      <div className="legend">
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: typeColors.service }} />
          <span>Service</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: typeColors.db }} />
          <span>Database</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: typeColors.cache }} />
          <span>Cache</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: typeColors.queue }} />
          <span>Queue</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: typeColors.external }} />
          <span>External</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: criticalityColors.high }} />
          <span>Critical</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: criticalityColors.medium }} />
          <span>Medium</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: criticalityColors.low }} />
          <span>Low</span>
        </div>
      </div>
    </div>
  );
};

export default GraphView;
