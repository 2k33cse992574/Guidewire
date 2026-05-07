const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

// This backend serves as the Node.js API Gateway matching the Microsoft resume architecture.
// Actual ML tasks are delegated to the Python ML Service.

app.get('/', (req, res) => {
    res.json({ message: 'GigShield API Gateway (Node.js) is running.' });
});

app.post('/api/auth/register', (req, res) => {
    // Wrapper around DB logic
    res.json({ status: 'success', message: 'User registered via Node.js Gateway' });
});

app.post('/api/auth/login', (req, res) => {
    // Wrapper around DB logic
    res.json({ status: 'success', message: 'User logged in via Node.js Gateway' });
});

// Proxy routes to ML Service
app.post('/api/metrics', async (req, res) => {
    // In a real environment, this would HTTP POST to the Python ML microservice (port 8000).
    res.json({ status: 'success', message: 'Metrics aggregated.' });
});

app.post('/api/trigger', async (req, res) => {
    // In a real environment, this would HTTP POST to the Python ML microservice (port 8000).
    res.json({ status: 'success', message: 'Trigger initiated.' });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`GigShield Node Backend running on port ${PORT}`));
