// frontend/metrics/widgets/RerouteDonut.js
import React from 'react';
import { PieChart, Pie, Cell, Tooltip } from 'recharts';

export default function RerouteDonut({ pct }) {
  const data = [
    { label: 'Rerouted', count: pct },
    { label: 'Failed', count: 100 - pct },
  ];
  const COLORS = ['#00C49F', '#666'];

  return (
    <div className="bg-[#051530] p-6 rounded-lg shadow-lg flex flex-col items-center">
      <h3 className="text-lg font-medium mb-2">Reroute Success</h3>
      <PieChart width={200} height={200}>
        <Pie
          data={data}
          dataKey="count"
          nameKey="label"
          outerRadius={80}
          innerRadius={40}
          paddingAngle={4}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i]} />
          ))}
        </Pie>
        <Tooltip formatter={value => `${value}%`} />
      </PieChart>
    </div>
  );
}
