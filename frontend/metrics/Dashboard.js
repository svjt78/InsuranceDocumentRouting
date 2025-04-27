// frontend/metrics/Dashboard.js

import { useMetrics } from "./hooks";
import StatusDonut       from "./widgets/StatusDonut";
import DailyVolumeLine   from "./widgets/DailyVolumeLine";
import BacklogBig        from "./widgets/BacklogBig";
import LatencyBars       from "./widgets/LatencyBars";
import OverrideDonut     from "./widgets/OverrideDonut";
import RerouteDonut      from "./widgets/RerouteDonut";

export default function Dashboard() {
  const { data, isLoading, isError, error } = useMetrics();

  if (isError) {
    console.error("Failed to load metrics:", error);
    return <p className="text-red-500">Error loading metrics</p>;
  }

  if (isLoading || !data) {
    return <p>Loading…</p>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      <StatusDonut     data={data.status} />
      <DailyVolumeLine data={data.daily} />
      <BacklogBig      value={data.backlog} />
      <LatencyBars     stats={data.latency} />
      <OverrideDonut   pct={data.overrides} />
      <RerouteDonut    pct={data.reroute} />
    </div>
  );
}
