import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
    if (req.method === 'GET') {
        const filePath = path.join(process.cwd(), 'src/app/llm4Cypher/lchain2cypher.py');
        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) {
                res.status(500).json({ error: 'Failed to read file' });
                return;
            }
            res.status(200).json({ result: data });
        });
    } else {
        res.status(405).json({ error: 'Method not allowed' });
    }
}