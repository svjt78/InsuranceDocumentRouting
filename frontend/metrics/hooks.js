import useSWR from "swr";
const fetcher = (url) => fetch(url).then(r => r.json());
export const useMetrics = () =>
  useSWR("http://localhost:8000/metrics/overview", fetcher, { refreshInterval: 15000 });
