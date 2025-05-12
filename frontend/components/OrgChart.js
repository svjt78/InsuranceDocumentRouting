// frontend/components/OrgChart.js

import React, { useState, useEffect, useRef } from 'react';
import Tree from 'react-d3-tree';

export default function OrgChart() {
  const [treeData, setTreeData] = useState(null);
  const [dims, setDims] = useState({ width: 0, height: 0 });
  const containerRef = useRef(null);
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

  // 1. Load the hierarchy once
  useEffect(() => {
    fetch(`${API_BASE}/lookup/doc-hierarchy`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(raw => {
        setTreeData([
          {
            name: 'Organizational Hierarchy',
            children: Object.entries(raw).map(([dept, cats]) => ({
              name: dept,
              children: Object.entries(cats).map(([cat, subs]) => ({
                name: cat,
                children: subs.map(sub => ({ name: sub })),
              })),
            })),
          },
        ]);
      })
      .catch(err => console.error('Hierarchy load failed:', err));
  }, [API_BASE]);

  // 2. Measure container size
  useEffect(() => {
    const measure = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        setDims({ width, height });
      }
    };
    measure();
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, []);

  // 3. Loading state
  if (!treeData || dims.width === 0) {
    return (
      <div
        ref={containerRef}
        style={{
          width: '100%',
          height: '600px',
          backgroundColor: '#0c0d15',
        }}
      >
        {!treeData && <p className="text-white p-4">Loading hierarchy…</p>}
      </div>
    );
  }

  // 4. Render the tree
  return (
    <div
      ref={containerRef}
      className="rd3t-container"
      style={{
        width: '100%',
        height: '600px',
        backgroundColor: '#0c0d15',
        position: 'relative',
        overflow: 'auto',
      }}
    >
      {/* Global CSS overrides for white text & white links */}
      <style jsx global>{`
        .rd3t-container svg text {
          fill: #fff !important;
          stroke: none !important;
        }
        .rd3t-container svg path.rd3t-link {
          stroke: #fff !important;
          stroke-width: 2px !important;
        }
        .rd3t-container {
          cursor: grab;
        }
        .rd3t-container:active {
          cursor: grabbing;
        }
      `}</style>

      <Tree
        data={treeData}
        orientation="vertical"
        translate={{ x: dims.width / 2, y: 50 }}
        pathFunc="elbow"
        collapsible
        zoomable
        separation={{ siblings: 1.5, nonSiblings: 2.5 }}
        scaleExtent={{ min: 0.5, max: 2 }}
        linkSvgProps={{ stroke: '#fff', strokeWidth: 2 }}
        renderCustomNodeElement={({ nodeDatum, toggleNode }) => {
          const name = nodeDatum.name;
          // dynamic width based on label length
          const boxWidth = Math.max(name.length * 8, 100);
          return (
            <g onClick={toggleNode} style={{ cursor: 'pointer' }}>
              <rect
                x={-boxWidth / 2}
                y={-15}
                width={boxWidth}
                height={30}
                rx={8}
                ry={8}
                fill="#1e1e2f"
                stroke="#fff"
                strokeWidth={1}
              />
              <text
                x={0}
                y={5}
                textAnchor="middle"
                style={{ fontSize: '12px', fontWeight: 600 }}
              >
                {name}
              </text>
            </g>
          );
        }}
      />
    </div>
  );
}
