// File: pages/api/runPython.js
import { spawn } from 'child_process';


export default function handler(req, res) {
    if (req.method === 'POST') {
        const userInput = req.body.userInput;
        const inputTest = "How many windows are there in the building?";
        console.log("User input is in runPython: ", typeof userInput);
        // Spawn a Python process
        const pythonProcess = spawn('python', ['src/app/llmGraphQL/lchain2cypher.py', userInput]);

        let result = '';
        pythonProcess.stdout.on('data', (data) => {
            result += data.toString();
            console.log("Data in runPython stringified: ", data.toString());
        });

        pythonProcess.stderr.on('data', (error) => {
            console.error("Python error:", error.toString());
        });

        pythonProcess.on('close', (code) => {
            console.log(`Python process exited with code ${code}`);
            if (code === 0) {
                console.log("Final result in runPython: ", result);
                res.status(200).json({ result });
            } else {
                res.status(500).json({ error: 'Python script failed' });
            }
        });
    } else {
        res.status(405).send('Method Not Allowed');
    }
}