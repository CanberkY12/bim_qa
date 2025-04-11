// This js file is responsible of sending the Ifc file to corresponding parsing scripts.
// Specifically to neo4j graph db and xeokit bim viewer tool.

export default async function sendIFC(ifcImport) {
    console.log("ifcImport in sendIFC: ");
    
    try {
      const formData = new FormData();
      formData.append('file', new Blob([ifcImport], { type: 'application/octet-stream' }));
      //formData.append('file', ifcImport);
      console.log("IFC path string in sendIFC: ");
  
      const response = await fetch('/api/runIfc2Neo', {
        method: 'POST',
        body: ifcImport,
    }).then(response => {
        console.log("Response:", response);
    });
    
      const data = await response.json();
      console.log("Response from ifcRec ifcImport||/:", data);
  } catch (error) {
      console.error("Error from ifcRec ifcImport||/:", error);
  }

  try {
    const formData = new FormData();
      formData.append('file', new Blob([ifcImport], { type: 'application/octet-stream' }));
      //formData.append('file', ifcImport);
      console.log("IFC path string in sendIFC: ");
  
      /*const response = await fetch('/api/runifc2xkt', {
        method: 'POST',
        body: ifcImport,
    }).then(response => {
        console.log("Response:", response);
    });*/
    
      const data = await response.json();
      //console.log("Response from ifcRec ifcImport||/:", data);
  } catch (error) {
      console.error("Error from ifcxkt ifcImport||/:", error);
  }
    
}