// frontend/metrics/widgets/StatusDonut.js
import React from 'react';
import { PieChart, Pie, Cell, Tooltip } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function StatusDonut({ data }) {
  return (
    <div className="bg-[#051530] p-6 rounded-lg shadow-lg flex flex-col items-center">
      <h3 className="text-lg font-medium mb-2">Status Breakdown</h3>
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
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(value, name) => [`${value} docs`, name]} />
      </PieChart>
    </div>
  );
}
