// PropertiesPanel.tsx
import React, { useState } from 'react';

interface PropertiesPanelProps {
  propertiesTable: any; // Replace 'any' with the actual type if known
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({ propertiesTable }) => {
  const [queryString, setQueryString] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<boolean>(false);

  // Handle search input change
  const onTextInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQueryString(value !== '' ? value : null);
    propertiesTable.queryString = queryString;
  };

  // Handle expand/collapse toggle
  const expandTable = () => {
    setExpanded(!expanded);
    propertiesTable.expanded = !propertiesTable.expanded;
  };

  // Handle copying properties as TSV
  const copyAsTSV = async () => {
    if (propertiesTable.tsv) {
      await navigator.clipboard.writeText(propertiesTable.tsv);
      alert("Copied properties as TSV to clipboard!");
    }
  };

  return (
    <div className="properties-panel">
      <div className="panel-header">
        <h3>Properties</h3>
        <button onClick={expandTable}>
          {expanded ? 'Collapse' : 'Expand'}
        </button>
        <button onClick={copyAsTSV}>Copy as TSV</button>
      </div>

      <div className="panel-section">
        <input
          type="text"
          placeholder="Search Property"
          onChange={onTextInput}
          className="search-input"
        />
      </div>
      
      {expanded && (
        <div className="properties-table">
          {/* Render properties table or list here */}
          {propertiesTable.render()}
        </div>
      )}
    </div>
  );
};

export default PropertiesPanel;
