import React, { useEffect, useState } from "react";
import { FaSave, FaTrashAlt } from "react-icons/fa";

export default function BucketMappingRow({ mapping, departmentsOptions, onSave, onDelete }) {
  const [bucketName, setBucketName] = useState(mapping.bucketName || "");
  const [selectedDepartment, setSelectedDepartment] = useState(mapping.department || "");
  const [selectedCategory, setSelectedCategory] = useState(mapping.category || "");
  const [selectedSubcategory, setSelectedSubcategory] = useState(mapping.subcategory || "");
  const [categoriesOptions, setCategoriesOptions] = useState([]);
  const [subcategoriesOptions, setSubcategoriesOptions] = useState([]);

  // When department changes, update categories and reset dependent selections.
  useEffect(() => {
    const dept = departmentsOptions.find((d) => d.department === selectedDepartment);
    if (dept) {
      setCategoriesOptions(dept.categories);
    } else {
      setCategoriesOptions([]);
    }
    setSelectedCategory("");
    setSubcategoriesOptions([]);
    setSelectedSubcategory("");
  }, [selectedDepartment, departmentsOptions]);

  // When category changes, update subcategories.
  useEffect(() => {
    if (selectedDepartment && selectedCategory) {
      const dept = departmentsOptions.find((d) => d.department === selectedDepartment);
      if (dept) {
        const cat = dept.categories.find((c) => c.category === selectedCategory);
        if (cat) {
          setSubcategoriesOptions(cat.subcategories);
        } else {
          setSubcategoriesOptions([]);
        }
      }
    } else {
      setSubcategoriesOptions([]);
    }
    setSelectedSubcategory("");
  }, [selectedCategory, selectedDepartment, departmentsOptions]);

  const handleSave = () => {
    const newMapping = {
      id: mapping.id, // This could be undefined for a new mapping
      bucket_name: bucketName,  // updated key
      department: selectedDepartment,
      category: selectedCategory,
      subcategory: selectedSubcategory,
    };
    onSave(newMapping);
  };

  const handleDelete = () => {
    if (mapping.id) {
      onDelete(mapping.id);
    } else {
      // If the mapping is new and unsaved, simply remove it from the list in the parent.
      onDelete(null, mapping);
    }
  };

  return (
    <div className="flex items-center space-x-4 p-2 border-b border-gray-700">
      <input
        type="text"
        placeholder="Bucket Name"
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
        className="bg-[#0c0d15] border border-gray-600 p-2 text-white rounded"
        disabled={!selectedDepartment}
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
        className="bg-[#0c0d15] border border-gray-600 p-2 text-white rounded"
        disabled={!selectedCategory}
      >
        <option value="">Select Subcategory</option>
        {subcategoriesOptions.map((subcat, index) => (
          <option key={index} value={subcat}>
            {subcat}
          </option>
        ))}
      </select>
      <button onClick={handleSave} className="text-green-500 hover:text-green-700">
        <FaSave size={20} />
      </button>
      <button onClick={handleDelete} className="text-red-500 hover:text-red-700">
        <FaTrashAlt size={20} />
      </button>
    </div>
  );
}
