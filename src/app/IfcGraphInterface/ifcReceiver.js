export default async function sendIFC(ifcImport) {
    console.log("ifcImport in sendIFC: ", ifcImport);
    
    try {
      const formData = new FormData();
      formData.append('file', new Blob([ifcImport], { type: 'application/octet-stream' }));
      //formData.append('file', ifcImport);
      console.log("IFC path string in sendIFC: ", ifcImport);
  
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
    
    
}