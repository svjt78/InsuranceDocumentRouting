import Layout from "../../components/Layout";
import HierarchyManager from "../../components/hierarchy/HierarchyManager";

export default function HierarchyPage() {
  return (
    <Layout title="Configuration / Hierarchy">
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Organizational Hierarchy</h1>
        <HierarchyManager />
      </div>
    </Layout>
  );
}
