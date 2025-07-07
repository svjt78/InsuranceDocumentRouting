// frontend/metrics/widgets/StatusDonut.js
import React from 'react';
import { PieChart, Pie, Cell, Tooltip } from 'recharts';

const COLORS = {
  Pending:        '#0088FE',
  Processed:      '#00C49F',
  Failed:         '#FF8042',
  'No Destination':'#FFBB28',
};

const STATUS_ORDER = ['Pending', 'Processed', 'Failed', 'No Destination'];

export default function StatusDonut({ data }) {
  // Ensure we always have a slice for each status, including "Failed"
  const chartData = STATUS_ORDER.map((label) => {
    const found = data.find((d) => d.label === label);
    return { label, count: found ? found.count : 0 };
  });

  return (
    <div className="bg-[#051530] p-6 rounded-lg shadow-lg flex flex-col items-center">
      <h3 className="text-lg font-medium mb-2">Status Breakdown</h3>
      <PieChart width={200} height={200}>
        <Pie
          data={chartData}
          dataKey="count"
          nameKey="label"
          outerRadius={80}
          innerRadius={40}
          paddingAngle={4}
        >
          {chartData.map((entry) => (
            <Cell key={entry.label} fill={COLORS[entry.label]} />
          ))}
        </Pie>
        <Tooltip formatter={(value, name) => [`${value} docs`, name]} />
      </PieChart>
    </div>
  );
}
