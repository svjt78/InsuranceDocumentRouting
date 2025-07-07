// frontend/pages/configuration.js
import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { FaSave, FaTrashAlt } from "react-icons/fa";

/* --------------------------------------------------------------------------
   Subcomponent: BucketMappingRow
-------------------------------------------------------------------------- */
function BucketMappingRow({ mapping, departmentData, onSave, onDelete, onUpdate }) {
  const [bucketName, setBucketName] = useState(mapping.bucket_name || "");
  const [department, setDepartment] = useState(mapping.department || "");
  const [category, setCategory] = useState(mapping.category || "");
  const [subcategory, setSubcategory] = useState(mapping.subcategory || "");
  const [nameError, setNameError] = useState("");

  const selectedDept = departmentData.find((d) => d.department === department);
  const categories = selectedDept ? selectedDept.categories : [];
  const selectedCat = categories.find((c) => c.category === category);
  const subcategories = selectedCat ? selectedCat.subcategories : [];

  // Propagate changes up
  useEffect(() => {
    onUpdate({
      ...mapping,
      bucket_name: bucketName,
      department,
      category,
      subcategory,
    });
  }, [bucketName, department, category, subcategory]);

  // Validate bucket name
  useEffect(() => {
    const valid = /^[a-z0-9-]+$/.test(bucketName);
    setNameError(
      bucketName && !valid
        ? "S3 bucket names may only contain lowercase letters, digits, and hyphens."
        : ""
    );
  }, [bucketName]);

  return (
    <tr className="border-b border-gray-700">
      <td className="p-2">
        <input
          type="text"
          className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1"
          value={bucketName}
          onChange={(e) => setBucketName(e.target.value)}
          placeholder="S3 Bucket Name"
        />
        {nameError && <p className="text-red-400 text-sm mt-1">{nameError}</p>}
      </td>
      <td className="p-2">
        <select
          className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1"
          value={department}
          onChange={(e) => {
            setDepartment(e.target.value);
            setCategory("");
            setSubcategory("");
          }}
        >
          <option value="">Select Department</option>
          {departmentData.map((d) => (
            <option key={d.department} value={d.department}>
              {d.department}
            </option>
          ))}
        </select>
      </td>
      <td className="p-2">
        <select
          className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1"
          value={category}
          onChange={(e) => {
            setCategory(e.target.value);
            setSubcategory("");
          }}
          disabled={!department}
        >
          <option value="">Select Category</option>
          {categories.map((c) => (
            <option key={c.category} value={c.category}>
              {c.category}
            </option>
          ))}
        </select>
      </td>
      <td className="p-2">
        <select
          className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1"
          value={subcategory}
          onChange={(e) => setSubcategory(e.target.value)}
          disabled={!category}
        >
          <option value="">Select Subcategory</option>
          {subcategories.map((sc) => (
            <option key={sc} value={sc}>
              {sc}
            </option>
          ))}
        </select>
      </td>
      <td className="p-2 flex space-x-4">
        <FaSave
          title="Save S3 mapping"
          className={`text-green-400 hover:text-green-600 cursor-pointer ${
            nameError ? "opacity-50 cursor-not-allowed" : ""
          }`}
          onClick={() => !nameError && onSave(mapping.id)}
        />
        <FaTrashAlt
          title="Delete S3 mapping"
          className="text-red-400 hover:text-red-600 cursor-pointer"
          onClick={() => onDelete(mapping.id)}
        />
      </td>
    </tr>
  );
}

/* --------------------------------------------------------------------------
   Subcomponent: EmailSettingsRow
-------------------------------------------------------------------------- */
function EmailSettingsRow({ setting, departmentData, onSave, onDelete, onUpdate }) {
  const [department, setDepartment] = useState(setting.department || "");
  const [emailAddresses, setEmailAddresses] = useState(setting.email_addresses || "");

  useEffect(() => {
    onUpdate({ ...setting, department, email_addresses: emailAddresses });
  }, [department, emailAddresses]);

  return (
    <tr className="border-b border-gray-700">
      <td className="p-2">
        <select
          className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1"
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
        >
          <option value="">Select Department</option>
          {departmentData.map((d) => (
            <option key={d.department} value={d.department}>
              {d.department}
            </option>
          ))}
        </select>
      </td>
      <td className="p-2">
        <input
          type="text"
          className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1"
          placeholder="Enter email(s), separated by commas"
          value={emailAddresses}
          onChange={(e) => setEmailAddresses(e.target.value)}
        />
      </td>
      <td className="p-2 flex space-x-4">
        <FaSave
          title="Save email setting"
          className="text-green-400 hover:text-green-600 cursor-pointer"
          onClick={() => onSave(setting.id)}
        />
        <FaTrashAlt
          title="Delete email setting"
          className="text-red-400 hover:text-red-600 cursor-pointer"
          onClick={() => onDelete(setting.id)}
        />
      </td>
    </tr>
  );
}

/* --------------------------------------------------------------------------
   Main Configuration Component
-------------------------------------------------------------------------- */
export default function Configuration() {
  const [departmentData, setDepartmentData] = useState([]);
  const staticData = [
    {
      department: "Policy Management / Underwriting",
      categories: [
        {
          category: "Policy Applications",
          subcategories: [
            "New Policy Applications",
            "Application Forms",
            "Proof of Identity and Address",
            "Vehicle Registration Documents"
          ]
        },
        {
          category: "Renewals",
          subcategories: ["Policy Renewal Notices"]
        },
        {
          category: "Endorsements",
          subcategories: ["Policy Amendments/Endorsements"]
        }
      ]
    },
    {
      department: "Claims",
      categories: [
        {
          category: "Claims Filing",
          subcategories: [
            "Claim Forms",
            "Accident Reports",
            "Police Reports",
            "Photos of Damages"
          ]
        },
        {
          category: "Claims Investigation",
          subcategories: [
            "Accident Reports",
            "Medical Records (for injury claims)",
            "Repair Estimates",
            "Photos of Damages"
          ]
        },
        {
          category: "Claims Settlement",
          subcategories: ["Medical Bills", "Repair Estimates"]
        }
      ]
    }
  ];

  const [bucketMappings, setBucketMappings] = useState([]);
  const [loadingBucket, setLoadingBucket] = useState(true);
  const [errorBucket, setErrorBucket] = useState("");

  const [emailSettings, setEmailSettings] = useState([]);
  const [loadingEmail, setLoadingEmail] = useState(true);
  const [errorEmail, setErrorEmail] = useState("");

  const [ingestionMode, setIngestionMode] = useState("realtime");

  /* Fetch hierarchy */
  useEffect(() => {
    async function fetchHierarchy() {
      try {
        const res = await fetch("http://localhost:8000/lookup/doc-hierarchy");
        if (!res.ok) throw new Error("Failed to fetch hierarchy");
        const raw = await res.json();
        const transformed = Object.entries(raw).map(([dept, cats]) => ({
          department: dept,
          categories: Object.entries(cats).map(([cat, subs]) => ({
            category: cat,
            subcategories: subs
          }))
        }));
        setDepartmentData(transformed);
      } catch {
        setDepartmentData(staticData);
      }
    }
    fetchHierarchy();
  }, []);

  /* Fetch bucket mappings */
  useEffect(() => {
    async function fetchBuckets() {
      try {
        const res = await fetch("http://localhost:8000/bucket-mappings");
        if (!res.ok) throw new Error("Failed to fetch bucket mappings");
        const data = await res.json();
        setBucketMappings(data);
      } catch {
        setErrorBucket("Unable to load bucket mappings.");
      } finally {
        setLoadingBucket(false);
      }
    }
    fetchBuckets();
  }, []);

  /* Fetch email settings */
  useEffect(() => {
    async function fetchEmailSettings() {
      try {
        const res = await fetch("http://localhost:8000/email-settings");
        if (!res.ok) throw new Error("Failed to fetch email settings");
        const data = await res.json();
        setEmailSettings(data);
      } catch {
        setErrorEmail("Unable to load email settings.");
      } finally {
        setLoadingEmail(false);
      }
    }
    fetchEmailSettings();
  }, []);

  /* Bucket mapping handlers */
  const handleBucketRowUpdate = (updatedRow) => {
    setBucketMappings(prev =>
      prev.map((row) => (row.id === updatedRow.id ? updatedRow : row))
    );
  };
  const handleBucketSaveRow = async (id) => {
    const row = bucketMappings.find((r) => r.id === id);
    if (!row) return;
    const payload = {
      bucket_name: row.bucket_name,
      department: row.department,
      category: row.category,
      subcategory: row.subcategory
    };
    try {
      if (row.isNew) {
        const res = await fetch("http://localhost:8000/bucket-mappings", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("POST failed");
        const newRow = await res.json();
        setBucketMappings((prev) =>
          prev.map((r) => (r.id === id ? newRow : r))
        );
      } else {
        const res = await fetch(
          `http://localhost:8000/bucket-mappings/${id}`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          }
        );
        if (!res.ok) throw new Error("PUT failed");
        const newRow = await res.json();
        setBucketMappings((prev) =>
          prev.map((r) => (r.id === id ? newRow : r))
        );
      }
    } catch {
      alert("Failed to save bucket mapping row.");
    }
  };
  const handleBucketDeleteRow = async (id) => {
    const row = bucketMappings.find((r) => r.id === id);
    if (!row) return;
    if (row.isNew) {
      setBucketMappings((prev) => prev.filter((r) => r.id !== id));
      return;
    }
    try {
      const res = await fetch(
        `http://localhost:8000/bucket-mappings/${id}`,
        { method: "DELETE" }
      );
      if (!res.ok) throw new Error("DELETE failed");
      setBucketMappings((prev) => prev.filter((r) => r.id !== id));
    } catch {
      alert("Failed to delete bucket mapping row.");
    }
  };
  const handleAddBucketMapping = () => {
    setBucketMappings((prev) => [
      ...prev,
      {
        id: Date.now(),
        bucket_name: "",
        department: "",
        category: "",
        subcategory: "",
        isNew: true
      }
    ]);
  };

  /* Email settings handlers */
  const handleEmailRowUpdate = (updatedRow) => {
    setEmailSettings((prev) =>
      prev.map((row) => (row.id === updatedRow.id ? updatedRow : row))
    );
  };
  const handleEmailSaveRow = async (id) => {
    const row = emailSettings.find((r) => r.id === id);
    if (!row) return;
    const payload = {
      department: row.department,
      email_addresses: row.email_addresses
    };
    try {
      if (row.isNew) {
        const res = await fetch("http://localhost:8000/email-settings", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("POST failed");
        const newRow = await res.json();
        setEmailSettings((prev) =>
          prev.map((r) => (r.id === id ? newRow : r))
        );
      } else {
        const res = await fetch(
          `http://localhost:8000/email-settings/${id}`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          }
        );
        if (!res.ok) throw new Error("PUT failed");
        const newRow = await res.json();
        setEmailSettings((prev) =>
          prev.map((r) => (r.id === id ? newRow : r))
        );
      }
    } catch {
      alert("Failed to save email settings row.");
    }
  };
  const handleEmailDeleteRow = async (id) => {
    const row = emailSettings.find((r) => r.id === id);
    if (!row) return;
    if (row.isNew) {
      setEmailSettings((prev) => prev.filter((r) => r.id !== id));
      return;
    }
    try {
      const res = await fetch(
        `http://localhost:8000/email-settings/${id}`,
        { method: "DELETE" }
      );
      if (!res.ok) throw new Error("DELETE failed");
      setEmailSettings((prev) => prev.filter((r) => r.id !== id));
    } catch {
      alert("Failed to delete email settings row.");
    }
  };
  const handleAddEmailSetting = () => {
    setEmailSettings((prev) => [
      ...prev,
      { id: Date.now(), department: "", email_addresses: "", isNew: true }
    ]);
  };

  /* Ingestion mode handler */
  const handleSaveIngestionMode = async () => {
    try {
      const res = await fetch("http://localhost:8000/ingestion-mode", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: ingestionMode })
      });
      if (!res.ok) throw new Error("Failed to update ingestion mode");
      alert("Ingestion mode saved successfully!");
    } catch {
      alert("Failed to save ingestion mode.");
    }
  };

  return (
    <Layout title="Configuration">
      <div className="min-h-screen flex flex-col bg-[#0c0d15] text-white">
        <div className="p-4 space-y-6">
          <h1 className="text-2xl font-bold mb-4">Configuration</h1>

          {/* AWS S3 Bucket Mapping Section */}
          <div className="bg-[#051530] p-4 rounded mb-6">
            <h2 className="text-xl font-semibold mb-4">AWS S3 Bucket Mapping</h2>
            {loadingBucket ? (
              <p>Loading bucket mappings...</p>
            ) : errorBucket ? (
              <p className="text-red-400">{errorBucket}</p>
            ) : (
              <div>
                <table className="min-w-full text-sm mb-2">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="p-2 text-left">S3 Bucket Name</th>
                      <th className="p-2 text-left">Department</th>
                      <th className="p-2 text-left">Category</th>
                      <th className="p-2 text-left">Subcategory</th>
                      <th className="p-2 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bucketMappings.map((mapping) => (
                      <BucketMappingRow
                        key={mapping.id}
                        mapping={mapping}
                        departmentData={departmentData}
                        onSave={handleBucketSaveRow}
                        onDelete={handleBucketDeleteRow}
                        onUpdate={handleBucketRowUpdate}
                      />
                    ))}
                  </tbody>
                </table>
                <button
                  onClick={handleAddBucketMapping}
                  className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                >
                  Add Mapping
                </button>
              </div>
            )}
          </div>

          {/* Email Notification Settings Section */}
          <div className="bg-[#051530] p-4 rounded mb-6">
            <h2 className="text-xl font-semibold mb-4">Email Notification Settings</h2>
            {loadingEmail ? (
              <p>Loading email settings...</p>
            ) : errorEmail ? (
              <p className="text-red-400">{errorEmail}</p>
            ) : (
              <div>
                <table className="min-w-full text-sm mb-2">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="p-2 text-left">Department</th>
                      <th className="p-2 text-left">Emails</th>
                      <th className="p-2 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {emailSettings.map((setting) => (
                      <EmailSettingsRow
                        key={setting.id}
                        setting={setting}
                        departmentData={departmentData}
                        onSave={handleEmailSaveRow}
                        onDelete={handleEmailDeleteRow}
                        onUpdate={handleEmailRowUpdate}
                      />
                    ))}
                  </tbody>
                </table>
                <button
                  onClick={handleAddEmailSetting}
                  className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                >
                  Add Email Settings
                </button>
              </div>
            )}
          </div>

          {/* Ingestion Mode Section */}
          <div className="bg-[#051530] p-4 rounded">
            <h2 className="text-xl font-semibold mb-4">Ingestion Mode</h2>
            <div className="space-y-2">
              <div className="flex items-center">
                <input
                  type="radio"
                  id="realtime"
                  name="ingestionMode"
                  value="realtime"
                  checked={ingestionMode === "realtime"}
                  onChange={(e) => setIngestionMode(e.target.value)}
                  className="mr-2"
                />
                <label htmlFor="realtime">Real-Time</label>
              </div>
              <div className="flex items-center">
                <input
                  type="radio"
                  id="batch"
                  name="ingestionMode"
                  value="batch"
                  checked={ingestionMode === "batch"}
                  onChange={(e) => setIngestionMode(e.target.value)}
                  className="mr-2"
                />
                <label htmlFor="batch">Mini-Batch</label>
              </div>
              <button
                onClick={handleSaveIngestionMode}
                className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 mt-2"
              >
                Save Ingestion Mode
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
