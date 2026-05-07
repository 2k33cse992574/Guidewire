# GigShield — AI-Powered Parametric Insurance

> Designed for India's Gig Economy | Hackathon Project

---

## Executive Summary

**GigShield: AI-Powered Parametric Insurance** | *React.js, Node.js, scikit-learn, MongoDB*
* **Product Vision:** Architected a "zero-touch" parametric insurance platform for India's gig economy, automating claim processing to protect an average of ₹4,200 weekly income at risk.
* **Technical Implementation:** Engineered a real-time trigger engine monitoring 5 disruption events (weather, AQI, curfew) and developed a fraud detection system using an Isolation Forest ML model via scikit-learn.
* **Dynamic Pricing:** Created a dynamic premium calculator utilizing an AI-driven risk-scoring formula (`Premium = Weekly Income × Risk Score × 0.05`) to ensure sustainable, income-linked pricing.
* **Design Excellence:** Built a high-fidelity, futuristic 3D interface to significantly enhance user trust and accessibility for non-technical gig partners.

---

## 🏗 Microservices Architecture

To handle real-time data ingestion, seamless user interactions, and heavy machine learning processing, GigShield uses a modern microservices architecture:

### 1. `frontend/` (React.js + 3D Interface)
The client application used by Delivery Partners and Admins.
- Built with **React.js (Vite)**.
- Integrates **React Three Fiber** and **Three.js** for the futuristic 3D UI gateway.
- Contains the legacy HTML/JS dashboard under `public/` for backward compatibility.
- **To run:** `cd frontend && npm run dev`

### 2. `backend/` (Node.js API Gateway)
The core backend serving as the orchestrator for user data and API requests.
- Built with **Node.js, Express, and MongoDB (Mongoose)**.
- Manages User Auth, Claims Storage, and routes ML requests.
- **To run:** `cd backend && node server.js`

### 3. `ml_service/` (Python AI Engine)
Dedicated service for Machine Learning and complex calculations.
- Built with **Python, FastAPI, and scikit-learn**.
- Contains the **Isolation Forest** ML model for fraud detection and risk scoring.
- Processes the real-time trigger engine (Weather APIs, AQI, Traffic).
- **To run:** `cd ml_service && pip install -r requirements.txt && uvicorn api:app --reload`

---

## ⚙️ How It Works (End-to-End Workflow)

```text
Worker Registers on GigShield
          ↓
AI Risk Scoring (weather, AQI, zone risk, work pattern)
          ↓
Weekly Premium Calculated → WI × R × 0.05
          ↓
Trigger Engine polls APIs every 30 minutes
          ↓
Disruption Detected (rain / heat / AQI / flood / curfew)
          ↓
Multi-Signal Validation → Movement Check → Active Policy Check
          ↓
Fraud Detection Model (Isolation Forest) runs instantly
          ↓
If Approved → Payout credited to UPI instantly!
```

---

## 🚀 Running the Project Locally

To run the full stack locally, you need to spin up all three services:

1. **Start the ML Service (Port 8000)**
   ```bash
   cd ml_service
   pip install -r requirements.txt
   python main.py  # Or run `uvicorn api:app --reload`
   ```

2. **Start the Node.js Backend (Port 5000)**
   ```bash
   cd backend
   npm install
   node server.js
   ```

3. **Start the React Frontend (Port 5173)**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---
*Developed for DEVTrails 2026*
