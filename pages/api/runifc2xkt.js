// This file is part of the xeokit-bim-viewer project.
// It is not runnimng automatically at the moment.
// The conversion to xkt has some bugs to solve.


import { exec } from 'child_process';
import path from 'path';
import fs from 'fs';
//import { convert2xkt } from '.../node_modules/@xeokit/xeokit-convert';

//console.log("convert2xkt in runIfc2xkt.js: ", convert2xkt);
export default async function handler(req, res) {
    if (req.method === 'POST') {
        const userInput = req.body;
        const uploadedFilePath = path.join('.../data/projects/rawModel/rawModel.ifc');
        fs.writeFileSync(uploadedFilePath, userInput);
        console.log("The ifc file type in runIfc2xkt.js : ", typeof userInput);
        try {
            // Step 1: Extract file from the request
            //const uploadedFilePath = userInput // Path of the uploaded IFC file (sent from the frontend)
            const fileName = "xeokitModel"; // Get the file name without extension
            // Define paths for output files
            const OUTPUT_FOLDER = path.resolve('.../xeokit-bim-viewer/app/data/projects/XeokitviewerModel');
            console.log("OUTPUT_FOLDER in runIfc2xkt.js: ", OUTPUT_FOLDER);
            const daePath = path.join(OUTPUT_FOLDER, `${fileName}.dae`);
            const gltfPath = path.join(OUTPUT_FOLDER, `${fileName}.gltf`);
            const jsonPath = path.join(OUTPUT_FOLDER, `${fileName}.json`);
            const xktPath = path.join(OUTPUT_FOLDER, `${fileName}.xkt`);
            const metadataJsonPath = path.join(OUTPUT_FOLDER, `${fileName}_metadata.json`);

            // Ensure the output folder exists
            if (!fs.existsSync(OUTPUT_FOLDER)) {
                fs.mkdirSync(OUTPUT_FOLDER, { recursive: true });
            }

            // Step 2: Execute conversion pipeline
            console.log('Starting IFC to DAE conversion...');
            await runCommand(`ifcConvert ${uploadedFilePath} ${daePath}`);
            console.log('IFC to DAE conversion completed.');

            console.log('Starting DAE to glTF conversion...');
            await runCommand(`COLLADA2GLTF-bin -i ${daePath} -o ${gltfPath}`);
            console.log('DAE to glTF conversion completed.');

            console.log('Extracting metadata...');
            await runCommand(`xeokit-metadata extract -i ${uploadedFilePath} -o ${jsonPath}`);
            console.log('Metadata extraction completed.');

            console.log('Converting glTF and JSON to XKT...');
            await runCommand(`convert2xkt -g ${gltfPath} -m ${jsonPath} -o ${xktPath}`);
            console.log('glTF and JSON to XKT conversion completed.');

            // Step 3: Send response with the path to the XKT file
            res.status(200).json({
                message: 'File successfully converted',
                xktFile: `/converted_files/${fileName}.xkt`,
            });
        } catch (error) {
            console.error('Error during conversion pipeline:', error);
            res.status(500).json({ error: 'An error occurred during the file conversion process.' });
        }
    } else {
        res.status(405).send('Method Not Allowed');
    }
}

// Utility function to execute shell commands
function runCommand(command) {
    return new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error(`Command failed: ${command}`);
                console.error(stderr);
                reject(error);
            } else {
                console.log(stdout);
                resolve(stdout);
            }
        });
    });
}