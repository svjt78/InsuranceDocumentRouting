import React, { useEffect, useState } from "react";
import BucketMappingRow from "../components/BucketMappingRow";

export default function Configuration() {
  const [bucketMappings, setBucketMappings] = useState([]);
  const [departmentsOptions, setDepartmentsOptions] = useState([]);

  // For demonstration, we load the mapping options from a static JSON.
  // In production, you could fetch these options via an API.
  useEffect(() => {
    const data = [
      {
        "department": "Policy Management / Underwriting",
        "categories": [
          {
            "category": "Policy Applications",
            "subcategories": [
              "New Policy Applications",
              "Application Forms",
              "Proof of Identity and Address",
              "Vehicle Registration Documents"
            ]
          },
          {
            "category": "Renewals",
            "subcategories": ["Policy Renewal Notices"]
          },
          {
            "category": "Endorsements",
            "subcategories": ["Policy Amendments/Endorsements"]
          }
        ]
      },
      {
        "department": "Claims",
        "categories": [
          {
            "category": "Claims Filing",
            "subcategories": [
              "Claim Forms",
              "Accident Reports",
              "Police Reports",
              "Photos of Damages"
            ]
          },
          {
            "category": "Claims Investigation",
            "subcategories": [
              "Accident Reports",
              "Medical Records (for injury claims)",
              "Repair Estimates",
              "Photos of Damages"
            ]
          },
          {
            "category": "Claims Settlement",
            "subcategories": ["Medical Bills", "Repair Estimates"]
          }
        ]
      },
      {
        "department": "Underwriting",
        "categories": [
          {
            "category": "Risk Assessment",
            "subcategories": [
              "Risk Evaluation Reports",
              "Driving Records",
              "Credit Reports",
              "Vehicle Inspection Reports"
            ]
          },
          {
            "category": "Policy Issuance",
            "subcategories": ["Premium Calculation Documents"]
          }
        ]
      },
      {
        "department": "Customer Service",
        "categories": [
          {
            "category": "General Inquiries",
            "subcategories": [
              "Billing Queries",
              "Coverage Clarifications",
              "Email Correspondence",
              "Call Logs"
            ]
          },
          {
            "category": "Complaints",
            "subcategories": [
              "Billing Queries",
              "Email Correspondence",
              "Call Logs"
            ]
          },
          {
            "category": "Feedback",
            "subcategories": ["Feedback Forms"]
          }
        ]
      },
      {
        "department": "Legal & Compliance",
        "categories": [
          {
            "category": "Regulatory Compliance",
            "subcategories": ["Compliance Reports", "Regulatory Filings"]
          },
          {
            "category": "Dispute Resolution",
            "subcategories": ["Legal Notices", "Subpoenas"]
          }
        ]
      },
      {
        "department": "Finance & Billing",
        "categories": [
          {
            "category": "Payments",
            "subcategories": ["Premium Payments", "Payment Receipts"]
          },
          {
            "category": "Refunds",
            "subcategories": ["Refund Requests", "Payment Receipts"]
          },
          {
            "category": "Financial Reporting",
            "subcategories": ["Bank Statements"]
          }
        ]
      },
      {
        "department": "Marketing & Sales",
        "categories": [
          {
            "category": "Promotions",
            "subcategories": ["Marketing Campaigns", "Brochures"]
          },
          {
            "category": "New Business Acquisition",
            "subcategories": ["Sales Proposals", "Proposal Documents"]
          }
        ]
      }
    ];
    setDepartmentsOptions(data);
  }, []);

  // Fetch existing bucket mappings from backend API (assumes GET /bucket-mappings exists).
  useEffect(() => {
    async function fetchBucketMappings() {
      try {
        const res = await fetch("http://localhost:8000/bucket-mappings");
        const data = await res.json();
        setBucketMappings(data);
      } catch (error) {
        console.error("Failed to fetch bucket mappings", error);
      }
    }
    fetchBucketMappings();
  }, []);

  // Handlers for Save and Delete actions.
  const handleSaveMapping = async (mapping) => {
    try {
      let res;
      if (mapping.id) {
        res = await fetch(`http://localhost:8000/bucket-mappings/${mapping.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(mapping),
        });
      } else {
        res = await fetch("http://localhost:8000/bucket-mappings", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(mapping),
        });
      }
      if (res.ok) {
        const updatedMapping = await res.json();
        setBucketMappings((prev) => {
          const index = prev.findIndex((m) => m.id === updatedMapping.id);
          if (index !== -1) {
            const newMappings = [...prev];
            newMappings[index] = updatedMapping;
            return newMappings;
          } else {
            return [...prev, updatedMapping];
          }
        });
      }
    } catch (error) {
      console.error("Failed to save mapping", error);
    }
  };

  const handleDeleteMapping = async (id, unsavedMapping = null) => {
    if (id) {
      try {
        const res = await fetch(`http://localhost:8000/bucket-mappings/${id}`, {
          method: "DELETE",
        });
        if (res.ok) {
          setBucketMappings((prev) => prev.filter((m) => m.id !== id));
        }
      } catch (error) {
        console.error("Failed to delete mapping", error);
      }
    } else if (unsavedMapping) {
      // Remove unsaved row from UI.
      setBucketMappings((prev) => prev.filter((m) => m !== unsavedMapping));
    }
  };

  const addNewMappingRow = () => {
    setBucketMappings((prev) => [...prev, { bucketName: "", department: "", category: "", subcategory: "" }]);
  };

  return (
    <div className="container mx-auto p-4 bg-[#0c0d15] text-white">
      <h1 className="text-2xl font-bold mb-4">MinIO Bucket Mappings</h1>
      <div className="space-y-2">
        {bucketMappings.map((mapping, index) => (
          <BucketMappingRow
            key={mapping.id || index}
            mapping={mapping}
            departmentsOptions={departmentsOptions}
            onSave={handleSaveMapping}
            onDelete={handleDeleteMapping}
          />
        ))}
      </div>
      <button
        onClick={addNewMappingRow}
        className="mt-4 px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition-colors"
      >
        Add New Mapping
      </button>
    </div>
  );
}
