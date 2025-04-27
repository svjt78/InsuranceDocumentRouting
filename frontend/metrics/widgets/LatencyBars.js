// frontend/metrics/widgets/LatencyBars.js
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function LatencyBars({ stats }) {
  const data = [
    { name: 'Avg', value: stats.avg },
    { name: 'P90', value: stats.p90 },
    { name: 'P99', value: stats.p99 },
  ];

  return (
    <div className="bg-[#051530] p-6 rounded-lg shadow-lg">
      <h3 className="text-lg font-medium mb-2">Latency (sec)</h3>
      <BarChart width={300} height={200} data={data}>
        <CartesianGrid stroke="#333" strokeDasharray="3 3" />
        <XAxis dataKey="name" stroke="#aaa" />
        <YAxis stroke="#aaa" />
        <Tooltip formatter={value => `${value} sec`} />
        <Bar dataKey="value" barSize={30} fill="#0088FE" />
      </BarChart>
    </div>
  );
}
