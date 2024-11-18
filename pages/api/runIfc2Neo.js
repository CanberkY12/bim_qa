import { spawn } from 'child_process';

export default function handler(req, res) {
    if (req.method === 'POST') {
        // Get the user input from the request body
        const userInput = req.body.userInput;
        console.log("The ifc file type in runIfc2Neo.js : ", userInput);
        // Spawn a Python process
        const pythonProcess = spawn('python', ['src/app/IfcGraphInterface/script_parseIfc2Graph.py', userInput]);

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
            res.status(200).json({ result });
        });
    } else {
        res.status(405).send('Method Not Allowed');
    }
}