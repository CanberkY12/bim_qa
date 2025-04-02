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
  
  
