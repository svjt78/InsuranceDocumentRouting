import Layout from '../components/Layout';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid
} from 'recharts';

const pieData = [
  { name: 'Pending', value: 30 },
  { name: 'Processed', value: 50 },
  { name: 'Overridden', value: 10 },
  { name: 'Failed', value: 10 },
];

const lineData = [
  { date: '2025-01-01', volume: 20 },
  { date: '2025-01-02', volume: 35 },
  { date: '2025-01-03', volume: 40 },
  { date: '2025-01-04', volume: 55 },
  { date: '2025-01-05', volume: 50 },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function Metrics() {
  return (
    <Layout title="Metrics">
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Metrics & KPIs</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h2 className="text-xl font-semibold mb-2">Document Status Breakdown</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={100} fill="#8884d8" label>
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div>
            <h2 className="text-xl font-semibold mb-2">Document Volume Trends</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={lineData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
                <XAxis dataKey="date" stroke="#fff" />
                <YAxis stroke="#fff" />
                <Tooltip />
                <Line type="monotone" dataKey="volume" stroke="#8884d8" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </Layout>
  );
}
