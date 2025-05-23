import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { FaSave, FaTrashAlt } from "react-icons/fa";

/* --------------------------------------------------------------------------
   Subcomponent: BucketMappingRow
-------------------------------------------------------------------------- */
function BucketMappingRow({ mapping, departmentData, onSave, onDelete, onUpdate }) {
  // Initialize state using backend's key name "bucket_name"
  const [bucketName, setBucketName] = useState(mapping.bucket_name || "");
  const [department, setDepartment] = useState(mapping.department || "");
  const [category, setCategory] = useState(mapping.category || "");
  const [subcategory, setSubcategory] = useState(mapping.subcategory || "");
  // validation state
  const [nameError, setNameError] = useState("");

  // Derive available categories and subcategories based on selected department/category.
  const selectedDept = departmentData.find((d) => d.department === department);
  const categories = selectedDept ? selectedDept.categories : [];
  const selectedCat = categories.find((c) => c.category === category);
  const subcategories = selectedCat ? selectedCat.subcategories : [];

  // inform parent of any field changes
  useEffect(() => {
    onUpdate({ ...mapping, bucket_name: bucketName, department, category, subcategory });
  }, [bucketName, department, category, subcategory]);

  // bucket-name format check
  useEffect(() => {
    const valid = /^[a-z0-9-]+$/.test(bucketName);
    setNameError(
      bucketName && !valid
        ? "Bucket names may only contain lowercase letters, digits, and hyphens."
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
          placeholder="Bucket Name"
        />
        {nameError && (
          <p className="text-red-400 text-sm mt-1">{nameError}</p>
        )}
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
          {departmentData.map((dept) => (
            <option key={dept.department} value={dept.department}>
              {dept.department}
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
          {categories.map((cat) => (
            <option key={cat.category} value={cat.category}>
              {cat.category}
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
          className={`text-green-400 hover:text-green-600 cursor-pointer ${
            nameError ? "opacity-50 cursor-not-allowed" : ""
          }`}
          onClick={() => {
            if (!nameError) onSave(mapping.id);
          }}
        />
        <FaTrashAlt
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
  // Initialize state using backend key "email_addresses"
  const [department, setDepartment] = useState(setting.department || "");
  const [emailAddresses, setEmailAddresses] = useState(setting.email_addresses || "");

  useEffect(() => {
    // Update using the expected key "email_addresses"
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
          {departmentData.map((dept) => (
            <option key={dept.department} value={dept.department}>
              {dept.department}
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
          className="text-green-400 hover:text-green-600 cursor-pointer"
          onClick={() => onSave(setting.id)}
        />
        <FaTrashAlt
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
  // Dynamic department hierarchy fetched from /lookup endpoint.
  const [departmentData, setDepartmentData] = useState([]);
  // Fallback static hierarchy if dynamic data is unavailable.
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
    // ... add remaining department entries as needed.
  ];

  // State for MinIO Bucket Mappings.
  const [bucketMappings, setBucketMappings] = useState([]);
  const [loadingBucket, setLoadingBucket] = useState(true);
  const [errorBucket, setErrorBucket] = useState("");

  // State for Email Notification Settings.
  const [emailSettings, setEmailSettings] = useState([]);
  const [loadingEmail, setLoadingEmail] = useState(true);
  const [errorEmail, setErrorEmail] = useState("");

  // State for Ingestion Mode (default "realtime").
  const [ingestionMode, setIngestionMode] = useState("realtime");

  // Fetch document hierarchy from /lookup endpoint.
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
      } catch (err) {
        console.error("Failed to fetch department hierarchy", err);
        // Use static data as fallback.
        setDepartmentData(staticData);
      }
    }
    fetchHierarchy();
  }, []);

  // Fetch existing Bucket Mappings.
  useEffect(() => {
    async function fetchBuckets() {
      try {
        const res = await fetch("http://localhost:8000/bucket-mappings");
        if (!res.ok) throw new Error("Failed to fetch bucket mappings");
        const data = await res.json();
        setBucketMappings(data);
      } catch (err) {
        setErrorBucket("Unable to load bucket mappings.");
      } finally {
        setLoadingBucket(false);
      }
    }
    fetchBuckets();
  }, []);

  // Fetch existing Email Settings.
  useEffect(() => {
    async function fetchEmailSettings() {
      try {
        const res = await fetch("http://localhost:8000/email-settings");
        if (!res.ok) throw new Error("Failed to fetch email settings");
        const data = await res.json();
        setEmailSettings(data);
      } catch (err) {
        setErrorEmail("Unable to load email settings.");
      } finally {
        setLoadingEmail(false);
      }
    }
    fetchEmailSettings();
  }, []);

  // Handlers for Bucket Mapping updates.
  const handleBucketRowUpdate = (updatedRow) => {
    setBucketMappings((prev) =>
      prev.map((row) => (row.id === updatedRow.id ? updatedRow : row))
    );
  };

  const handleBucketSaveRow = async (id) => {
    const rowData = bucketMappings.find((r) => r.id === id);
    if (!rowData) return;
    try {
      // Construct payload using the consistent keys from the mapping object.
      const payload = {
        bucket_name: rowData.bucket_name, // use the updated key
        department: rowData.department,
        category: rowData.category,
        subcategory: rowData.subcategory,
      };
      console.log("Saving bucket mapping payload:", payload);
      if (rowData.isNew) {
        const res = await fetch("http://localhost:8000/bucket-mappings", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error("POST failed");
        const savedRow = await res.json();
        setBucketMappings((prev) =>
          prev.map((row) => (row.id === id ? savedRow : row))
        );
      } else {
        const res = await fetch(`http://localhost:8000/bucket-mappings/${id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error("PUT failed");
        const savedRow = await res.json();
        setBucketMappings((prev) =>
          prev.map((row) => (row.id === id ? savedRow : row))
        );
      }
    } catch (err) {
      alert("Failed to save bucket mapping row.");
    }
  };

  const handleBucketDeleteRow = async (id) => {
    const rowData = bucketMappings.find((r) => r.id === id);
    if (!rowData) return;
    if (rowData.isNew) {
      setBucketMappings((prev) => prev.filter((r) => r.id !== id));
      return;
    }
    try {
      const res = await fetch(`http://localhost:8000/bucket-mappings/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("DELETE failed");
      setBucketMappings((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      alert("Failed to delete bucket mapping row.");
    }
  };

  const handleAddBucketMapping = () => {
    const newMapping = {
      id: Date.now(), // Temporary ID
      bucket_name: "", // use bucket_name here for consistency
      department: "",
      category: "",
      subcategory: "",
      isNew: true,
    };
    setBucketMappings([...bucketMappings, newMapping]);
  };

  // Handlers for Email Settings rows.
  const handleEmailRowUpdate = (updatedRow) => {
    setEmailSettings((prev) =>
      prev.map((row) => (row.id === updatedRow.id ? updatedRow : row))
    );
  };

  const handleEmailSaveRow = async (id) => {
    const rowData = emailSettings.find((r) => r.id === id);
    if (!rowData) return;
    try {
      // Construct payload: convert emails to email_addresses
      const payload = {
        department: rowData.department,
        email_addresses: rowData.email_addresses || rowData.emails,
      };
      if (rowData.isNew) {
        const res = await fetch("http://localhost:8000/email-settings", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error("POST failed");
        const savedRow = await res.json();
        setEmailSettings((prev) =>
          prev.map((row) => (row.id === id ? savedRow : row))
        );
      } else {
        const res = await fetch(`http://localhost:8000/email-settings/${id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error("PUT failed");
        const savedRow = await res.json();
        setEmailSettings((prev) =>
          prev.map((row) => (row.id === id ? savedRow : row))
        );
      }
    } catch (err) {
      alert("Failed to save email settings row.");
    }
  };

  const handleEmailDeleteRow = async (id) => {
    const rowData = emailSettings.find((r) => r.id === id);
    if (!rowData) return;
    if (rowData.isNew) {
      setEmailSettings((prev) => prev.filter((r) => r.id !== id));
      return;
    }
    try {
      const res = await fetch(`http://localhost:8000/email-settings/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("DELETE failed");
      setEmailSettings((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      alert("Failed to delete email settings row.");
    }
  };

  const handleAddEmailSetting = () => {
    const newSetting = {
      id: Date.now(),
      department: "",
      email_addresses: "", // use email_addresses for consistency
      isNew: true,
    };
    setEmailSettings([...emailSettings, newSetting]);
  };

  // Handler for saving Ingestion Mode.
  const handleSaveIngestionMode = async () => {
    try {
      const res = await fetch("http://localhost:8000/ingestion-mode", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: ingestionMode }),
      });
      if (!res.ok) throw new Error("Failed to update ingestion mode");
      alert("Ingestion mode saved successfully!");
    } catch (err) {
      alert("Failed to save ingestion mode.");
    }
  };

  return (
    <Layout title="Configuration">
      <div className="min-h-screen flex flex-col bg-[#0c0d15] text-white">
        <div className="p-4 space-y-6">
          <h1 className="text-2xl font-bold mb-4">Configuration</h1>

          {/* MinIO Bucket Mapping Section */}
          <div className="bg-[#051530] p-4 rounded mb-6">
            <h2 className="text-xl font-semibold mb-4">MinIO Bucket Mapping</h2>
            {loadingBucket ? (
              <p>Loading bucket mappings...</p>
            ) : errorBucket ? (
              <p className="text-red-400">{errorBucket}</p>
            ) : (
              <div>
                <table className="min-w-full text-sm mb-2">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="p-2 text-left">Bucket</th>
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
                        departmentData={departmentData.length ? departmentData : staticData}
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
                        departmentData={departmentData.length ? departmentData : staticData}
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
