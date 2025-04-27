// frontend/metrics/widgets/DailyVolumeLine.js
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

export default function DailyVolumeLine({ data }) {
  return (
    <div className="bg-[#051530] p-6 rounded-lg shadow-lg">
      <h3 className="text-lg font-medium mb-2">Daily Volume</h3>
      <LineChart width={350} height={250} data={data}>
        <CartesianGrid stroke="#333" strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          tick={{ fill: '#aaa' }}
          tickFormatter={str => {
            const d = new Date(str);
            return `${d.getMonth()+1}/${d.getDate()}`;
          }}
        />
        <YAxis stroke="#aaa" />
        <Tooltip formatter={value => `${value} docs`} />
        <Line
          type="monotone"
          dataKey="count"
          stroke="#8884d8"
          strokeWidth={2}
          dot={{ r: 4 }}
        />
      </LineChart>
    </div>
  );
}
