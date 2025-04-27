// frontend/metrics/widgets/OverrideDonut.js
import React from 'react';
import { PieChart, Pie, Cell, Tooltip } from 'recharts';

export default function OverrideDonut({ pct }) {
  const data = [
    { label: 'Overridden', count: pct },
    { label: 'Others', count: 100 - pct },
  ];
  const COLORS = ['#FF8042', '#666'];

  return (
    <div className="bg-[#051530] p-6 rounded-lg shadow-lg flex flex-col items-center">
      <h3 className="text-lg font-medium mb-2">Override Rate</h3>
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
