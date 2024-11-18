import * as jQuery from 'jquery';
import $ from 'jquery';
import { use } from 'react';



export default async function sendInput(userInput) {
    
  try {
    const response = await fetch('/api/runPython', {
      method: 'POST',
      headers: {
      'Content-Type': 'application/json',
      },
      body: JSON.stringify({ userInput }),
      
    });

    const data = await response.json();
    console.log(typeof userInput);
    console.log("Response from Python||/:", data);
} catch (error) {
    console.error("Error||/:", error);
}
}
  
  
  /*
    const data_to_pass_in = {
      data_sent: userInput,
      data_return: undefined
    };
    console.log("Data is received in promptreceiver.js: ", data_to_pass_in);
    callPythonScript(data_to_pass_in);
    $.ajax({
      type: "POST",
      url: "http://localhost:3000",
      data: data_to_pass_in,
      success: function(response) {
          //console.log(jQuery.parseJSON(response).msg);
          console.log("Success||: ", response);
      },
      error: function (response) {
          //console.log(jQuery.parseJSON(response).msg);
          console.log("Error||: ", response);
          alert("Ajax error!");
      }
});*/

    //const pythonProcess = spawner('python', ['C:/Users/berky/oxide/src/app/llmGraphQL/lchain2cypher.py', JSON.stringify(data_to_pass_in)]);
    
    //pythonProcess.stdout.on('data', (data) => {
      //console.log("Data returned from python: ", data.toString());
      //data_to_pass_in.data_return = data.toString();
    //})