import React, { useEffect, useState } from "react";
import { FaSave, FaTrashAlt } from "react-icons/fa";

export default function BucketMappingRow({
  mapping,
  departmentsOptions,
  onSave,
  onDelete
}) {
  const [bucketName, setBucketName] = useState(mapping.bucket_name || "");
  const [selectedDepartment, setSelectedDepartment] = useState(
    mapping.department || ""
  );
  const [selectedCategory, setSelectedCategory] = useState(
    mapping.category || ""
  );
  const [selectedSubcategory, setSelectedSubcategory] = useState(
    mapping.subcategory || ""
  );
  const [categoriesOptions, setCategoriesOptions] = useState([]);
  const [subcategoriesOptions, setSubcategoriesOptions] = useState([]);

  // Update category/subcategory options when department changes
  useEffect(() => {
    const dept = departmentsOptions.find(
      (d) => d.department === selectedDepartment
    );
    setCategoriesOptions(dept ? dept.categories : []);
    setSelectedCategory("");
    setSubcategoriesOptions([]);
    setSelectedSubcategory("");
  }, [selectedDepartment, departmentsOptions]);

  // Update subcategories when category changes
  useEffect(() => {
    if (selectedDepartment && selectedCategory) {
      const dept = departmentsOptions.find(
        (d) => d.department === selectedDepartment
      );
      const cat = dept?.categories.find(
        (c) => c.category === selectedCategory
      );
      setSubcategoriesOptions(cat ? cat.subcategories : []);
    } else {
      setSubcategoriesOptions([]);
    }
    setSelectedSubcategory("");
  }, [selectedCategory, selectedDepartment, departmentsOptions]);

  // Notify parent that this row’s values have changed
  useEffect(() => {
    if (mapping.onUpdate) {
      mapping.onUpdate({
        ...mapping,
        bucket_name: bucketName,
        department: selectedDepartment,
        category: selectedCategory,
        subcategory: selectedSubcategory
      });
    }
  }, [bucketName, selectedDepartment, selectedCategory, selectedSubcategory]);

  const handleSave = () => {
    onSave(mapping.id);
  };

  const handleDelete = () => {
    onDelete(mapping.id);
  };

  return (
    <div className="flex items-center space-x-4 p-2 border-b border-gray-700">
      <input
        type="text"
        placeholder="S3 Bucket Name"
        value={bucketName}
        onChange={(e) => setBucketName(e.target.value)}
        className="bg-[#0c0d15] border border-gray-600 p-2 text-white rounded w-40"
      />

      <select
        value={selectedDepartment}
        onChange={(e) => setSelectedDepartment(e.target.value)}
        className="bg-[#0c0d15] border border-gray-600 p-2 text-white rounded"
      >
        <option value="">Select Department</option>
        {departmentsOptions.map((dept) => (
          <option key={dept.department} value={dept.department}>
            {dept.department}
          </option>
        ))}
      </select>

      <select
        value={selectedCategory}
        onChange={(e) => setSelectedCategory(e.target.value)}
        disabled={!selectedDepartment}
        className="bg-[#0c0d15] border border-gray-600 p-2 text-white rounded"
      >
        <option value="">Select Category</option>
        {categoriesOptions.map((cat) => (
          <option key={cat.category} value={cat.category}>
            {cat.category}
          </option>
        ))}
      </select>

      <select
        value={selectedSubcategory}
        onChange={(e) => setSelectedSubcategory(e.target.value)}
        disabled={!selectedCategory}
        className="bg-[#0c0d15] border border-gray-600 p-2 text-white rounded"
      >
        <option value="">Select Subcategory</option>
        {subcategoriesOptions.map((subcat, idx) => (
          <option key={idx} value={subcat}>
            {subcat}
          </option>
        ))}
      </select>

      <button
        title="Save S3 mapping"
        onClick={handleSave}
        className="text-green-500 hover:text-green-700"
      >
        <FaSave size={20} />
      </button>
      <button
        title="Delete S3 mapping"
        onClick={handleDelete}
        className="text-red-500 hover:text-red-700"
      >
        <FaTrashAlt size={20} />
      </button>
    </div>
  );
}
