const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const PORT = 4000;

app.use(cors({ origin: 'http://localhost:3000' }));
app.use(express.json());

// Функция для запуска Python-скрипта
async function runPythonScript(scriptName, args = []) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', [
      path.join(__dirname, 'Neiro_chat', scriptName),
      ...args,
    ]);

    let dataBuffer = '';
    let errorBuffer = '';

    pythonProcess.stdout.on('data', (data) => {
      dataBuffer += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorBuffer += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(`Python process exited with code ${code}. Error: ${errorBuffer}`);
      } else {
        try {
          const result = JSON.parse(dataBuffer);
          resolve(result);
        } catch (error) {
          reject(`JSON parsing error: ${error}. Raw data: ${dataBuffer}`);
        }
      }
    });
  });
}

// Обработчик для /api/query
app.post('/api/query', async (req, res) => {
  const { query, alternative } = req.body;
  console.log('Received query:', query);

  try {
    const args = alternative ? [query, 'alternative'] : [query];
    const result = await runPythonScript('Run.py', args);
    console.log('Response from Python (JSON):', result);
    res.json(result);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ answer: 'An error occurred while processing your request. Please try again.' });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});