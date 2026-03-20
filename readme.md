# GigShield — AI-Powered Parametric Insurance for India's Gig Economy

> Guidewire DEVTrails 2026 | University Hackathon

---

## Problem Statement

India's food delivery partners (Zomato, Swiggy) are the backbone of our fast-paced digital economy. External disruptions such as extreme weather, pollution, floods, and curfews can reduce their working hours and cause them to lose 20–30% of their monthly earnings. Currently, gig workers have no income protection against these uncontrollable events. When disruptions occur, they bear the full financial loss with no safety net.

---

## Our Solution

**GigShield** is an AI-enabled parametric insurance platform that safeguards food delivery partners against income loss caused by external disruptions. The platform provides automated coverage and payouts, incorporates intelligent fraud detection, and operates on a simple **weekly pricing model** aligned with the typical earnings cycle of gig workers.

> Coverage Scope: **Loss of income only.** Health, life, accident, and vehicle repair are strictly excluded.

---

## Persona: Meet Arjun

**Arjun**, 24, is a Swiggy delivery partner based in Mumbai. He works 6 days a week, earns approximately ₹700/day, and makes around ₹4,200 per week doing 8–10 deliveries daily across Andheri and Bandra zones.

**Scenario 1 — Heavy Rain:**
Mumbai receives 60mm of rainfall in 3 hours during monsoon season. Visibility drops below 1km. Swiggy halts deliveries in Arjun's zone. GigShield's weather trigger detects the threshold breach, automatically creates a claim, runs fraud detection, and credits 70% of his estimated lost income to his UPI — without Arjun doing anything.

**Scenario 2 — Extreme Heat:**
A heatwave pushes Mumbai temperatures to 44°C with a heat index of 46°C for 3 consecutive hours. Arjun cannot safely work outdoors during peak afternoon hours. GigShield detects the heat trigger, calculates his inactive hours, and processes a payout of 50% of his lost hourly income.

**Scenario 3 — Flood / Waterlogging:**
Rainfall exceeds 110mm in a day and Arjun's zone has a high flood risk score of 0.8. Deliveries are completely shut down. GigShield auto-triggers a flood claim and pays 80% of his daily income directly to his UPI.

**Scenario 4 — Zone Curfew:**
An unplanned curfew is imposed in Arjun's delivery zone. Zone status flips to "Restricted." GigShield's curfew trigger activates instantly, verifies Arjun's location is inside the affected zone, and processes 90% of his daily income as a payout.

---

## Application Workflow

🚀 Frontend Flow
The frontend of our application is designed to simulate a seamless user journey—from onboarding to automated claim processing—using HTML, CSS, JavaScript, and Chart.js. It is fully responsive and leverages localStorage for real-time data simulation.

🔄 Application Flow
Landing Page (index.html)
        ↓
Signup (signup.html)
        ↓
Select Plan (policy.html)
        ↓
Dashboard (dashboard.html)
        ↓
Trigger Disruption (claim.html)
        ↓
Auto Claim → Back to Dashboard
        ↓
Admin View (admin.html)

🏠 1. Landing Page 
🎯 Purpose:
Entry point of the application
Introduces the product in a simple and user-friendly way
📝 2. Signup (signup.html)
🎯 Purpose:
Collect user (worker) details
📥 Data Collected:
Name
Phone Number
Platform (e.g., Swiggy, Zomato, etc.)
💼 3. Plan Selection
🎯 Purpose:
Allows users to select a weekly premium plan
💡 Sample Plans:
₹49 → ₹1000 coverage
₹99 → ₹2500 coverage
₹199 → ₹5000 coverage

📊 4. Dashboard 
🎯 Purpose:
Central user interface after login
Displays protection and claim status
📊 Features:
Selected plan details
Coverage amount
Claim analytics using Chart.js

⚡ 5. Claim Simulation 
🎯 Purpose:
Simulates real-world disruptions to trigger claims
🔘 Trigger Options:
Rain 🌧
Traffic 🚦
Network Outage 📡
➡️ Automatically processes claims and redirects back to the dashboard

🛠 6. Admin Dashboard 
🎯 Purpose:
Provides system-level insights and analytics
📊 Features:
Total claims overview
Claim distribution (Pie Chart using Chart.js)
Risk pattern visualization
User Journey:
👤 User: Ramesh (Delivery Partner – Zomato)
Landing PageRamesh opens the website and understands how the platform provides financial protection against disruptions.
SignupHe enters:
Name: Ramesh
Phone: 9876543210
Platform: Zomato
Plan SelectionRamesh selects the ₹99 plan, which provides ₹2500 coverage.
DashboardHe is redirected to the dashboard where he sees:
His active plan (₹99)
Coverage amount (₹2500)
Claim analytics chart
Disruption OccursDuring work, heavy rain starts.Ramesh clicks on “Rain 🌧” in the claim section.
Auto Claim Processing
The system automatically detects disruption
Claim is triggered instantly
Compensation is credited (simulated via localStorage)
Updated DashboardRamesh returns to the dashboard and sees:
Claim recorded
Updated analytics (Chart.js graph reflects new claim)
Admin MonitoringOn the admin side:
Ramesh’s claim is added to total claims
Rain-related claims increase in the pie chart
Risk patterns update accordingly


```
Worker Registers on GigShield
          ↓
Inputs: city, daily income, active days per week, work zone
          ↓
AI Risk Scoring (weather, AQI, zone risk, work pattern, disruption history)
          ↓
Weekly Premium Calculated → WI × R × 0.05
          ↓
Worker Buys Weekly Policy via UPI
          ↓
Policy Active for 7 Days
          ↓
Trigger Engine polls APIs every 30 minutes
          ↓
Disruption Detected (rain / heat / AQI / flood / curfew)
          ↓
Multi-Signal Validation → Movement Check → Activity Check → Active Policy Check → Duplicate Check
          ↓-
Claim Auto-Created (zero worker action required)
          ↓
Fraud Detection Model runs instantly
          ↓
If Approved → Payout = affected_hours × hourly_income × payout_rate
          ↓
Worker Dashboard updates with payout confirmation
```

---

## Weekly Premium Model

Premiums are structured on a **weekly basis** to match the earnings cycle of gig workers who think and earn week-to-week.

### Step 1 — Estimate Weekly Income

```
Weekly Income (WI) = Avg Daily Income × Active Days per Week

Example: ₹700/day × 6 days = ₹4,200/week
```

The premium is income-linked, not fixed — ensuring it stays affordable across all income levels.

### Step 2 — Calculate Risk Score (AI-Based)

A Risk Score **R ∈ [0, 1]** is computed using a weighted combination of:

| Factor | Description |
|--------|-------------|
| Weather risk | Rain probability, temperature forecasts |
| Pollution level | AQI readings for the worker's city |
| Area risk | Flood-prone zone classification |
| Work pattern | Peak hour dependency, active working hours |
| Historical disruptions | Past disruption frequency in the zone |

```
Risk Score = Weighted combination of all risk factors

Safe area      → R ≈ 0.3
High-risk area → R ≈ 0.7
```

### Step 3 — Weekly Premium Calculation

```
Weekly Premium = WI × R × 0.05

Example:
  Weekly Income = ₹5,000
  Risk Score    = 0.6
  Premium       = 5000 × 0.6 × 0.05 = ₹150/week
```

### Step 4 — Why the 5% Factor?

- Keeps premium affordable in the ₹50–₹200/week range
- Matches gig worker cash flow (weekly earnings cycle)
- Ensures insurance sustainability (not loss-making for the insurer)

### Step 5 — Dynamic Weekly Adjustment

Premium is recalculated every week based on:
- Updated weather forecasts for the worker's zone
- Recent disruption trends in the city
- Worker's own activity patterns

```
If risk ↑ → premium slightly ↑
If risk ↓ → premium ↓
```

### Step 6 — Coverage and Payout Cap

- Coverage = loss of income during verified disruption events only
- Maximum payout capped at **60–70% of weekly income**
- Prevents misuse and keeps the system financially viable

### End-to-End Example

```
Weekly Income  = ₹6,000
Risk Score     = 0.5
Premium        = 6000 × 0.5 × 0.05 = ₹150/week

Disruption occurs → Lost income = ₹2,000
Payout = ₹2,000 × 0.7 = ₹1,400 credited to UPI instantly
```

---

## Parametric Triggers

Five measurable external events automatically trigger claims. No manual filing required by the worker.

### Trigger 1 — Heavy Rain

**Data Source:** OpenWeatherMap API

| Parameter | Threshold |
|-----------|-----------|
| Rainfall | ≥ 50mm in 3 hours |
| Rainfall rate | ≥ 20mm/hr |
| Visibility | < 1km |

```
IF (rainfall >= 50mm in 3hrs OR rainfall_rate >= 20mm/hr)
AND visibility < 1km
AND user_verified_location ∈ affected_zone
THEN trigger = ACTIVE
```

**Impact:** 60–80% income drop

```
hourly_income = weekly_income / total_working_hours
payout = affected_hours × hourly_income × 0.7
```

---

### Trigger 2 — Extreme Heat

**Data Source:** OpenWeatherMap API

| Parameter | Threshold |
|-----------|-----------|
| Temperature | ≥ 42°C |
| Heat Index | ≥ 45°C |
| Duration | ≥ 2 hours |

```
IF (temperature >= 42°C AND heat_index >= 45°C for 2+ hours)
AND user_verified_location ∈ affected_zone
THEN trigger = ACTIVE
```

**Impact:** 40–60% income drop

```
hourly_income = weekly_income / total_working_hours
payout = inactive_hours × hourly_income × 0.5
```

---

### Trigger 3 — Severe Air Pollution (AQI)

**Data Source:** AQICN / WAQI API

| Parameter | Threshold |
|-----------|-----------|
| AQI Index | ≥ 300 |
| Duration | ≥ 4 consecutive hours |

```
IF (AQI >= 300 for 4+ consecutive hours)
AND user_verified_location ∈ affected_zone
THEN trigger = ACTIVE
```

**Impact:** 30–50% income drop

```
hourly_income = weekly_income / total_working_hours
payout = affected_hours × hourly_income × 0.4
```

---

### Trigger 4 — Flood / Waterlogging

**Data Source:** OpenWeatherMap API + Historical flood zone dataset

| Parameter | Threshold |
|-----------|-----------|
| Rainfall | > 100mm/day |
| Area risk score | > 0.7 |
| Flood probability | > 70% |

```
IF ((rainfall > 100mm/day AND area_risk_score > 0.7)
OR flood_probability > 70%)
AND user_verified_location ∈ affected_zone
THEN trigger = ACTIVE
```

**Impact:** 80–100% income drop

```
payout = daily_income × 0.8
```

---

### Trigger 5 — Curfew / Zone Restriction

**Data Source:** Government APIs / News APIs / Mock data

| Parameter | Threshold |
|-----------|-----------|
| Zone status | "Restricted" or "Curfew" |

```
IF (zone_status == "restricted" OR zone_status == "curfew")
AND user_verified_location ∈ affected_zone
THEN trigger = ACTIVE
```

**Impact:** 90–100% income drop

```
payout = daily_income × 0.9
```

---

### Unified Trigger Execution Engine

```python
FOR each active_policy_user:
    fetch real-time data (weather, AQI, zone_status)
    IF any trigger condition == TRUE:
        validate user location
        calculate affected duration
        compute payout amount
        run fraud detection checks
        IF fraud_check == PASSED:
            auto-initiate claim
            process payout to UPI
```

### Validation Layer (Before Every Payout)

```
IF user_verified_location ∈ affected_zone
AND user_policy_status == ACTIVE
AND no duplicate claim detected for same trigger today
THEN payout → APPROVED
ELSE payout → REJECTED
```

---

## AI/ML Integration Plan
🎯 Objective

To integrate AI/ML across the system to enable:
	•	Dynamic premium calculation
	•	Predictive risk assessment
	•	Automated claim triggering
	•	Intelligent fraud detection

⸻

🔗 1. End-to-End AI Workflow
Data Collection → Feature Engineering → AI Models → Decision Engine → Trigger System → Fraud Check → Payout
📊 2. Data Collection Layer (Input to AI)

External Data
	•	Weather APIs → rainfall, temperature
	•	AQI APIs → pollution levels
	•	Traffic/zone data (mock)

Internal/User Data
	•	Location (zone-level via browser)
	•	Working hours (self-reported/mock)
	•	Weekly earnings

⸻

🔧 3. Feature Engineering

Raw data is transformed into meaningful features:
rain_risk = rainfall intensity
heat_risk = temperature + duration
pollution_risk = AQI / scale
area_risk = historical disruption score
user_dependency = peak_hours / total_hours
 These features feed all AI models.

⸻

🧠 4. AI Models Integration

⸻

🧠 A. Dynamic Premium Model (Risk Scoring)

Purpose

Calculate personalized weekly premium

Model
	•	Regression (Linear / XGBoost)

Input
	•	Weather risk
	•	Location risk
	•	User work pattern
Risk Score (0–1)
Premium = Weekly Income × Risk Score × 0.05
🧠 B. Predictive Risk Model

Purpose

Forecast disruptions in next 24–72 hours

Model
	•	Time-series / Logistic Regression

Input
	•	Historical weather + trigger data
Output:-
Disruption Probability (0–1)
Usage:-
IF probability > threshold:
    notify user
    adjust next week's premium
🧠 C. Trigger Validation Logic (AI-assisted)

Purpose

Ensure disruption actually affects the user

Input
	•	Trigger data
	•	User zone
	•	Area risk

Output
Impact Validity (True/False)
Usage:-
IF trigger_active AND impact_valid:
    initiate claim
🧠 D. Fraud Detection Model

Purpose

Detect fake or manipulated claims

Model
	•	Hybrid:
	•	Rule-based checks
	•	Isolation Forest (anomaly detection)

Input
	•	Location consistency
	•	Activity logs
	•	Claim frequency
Output
Fraud Score (0–1)
Usage
IF fraud_score > 0.7:
    reject payout
ELSE:
    approve payout
⚡ 5. Real-Time Trigger Integration

AI works alongside rule-based triggers:
IF (rain / heat / AQI trigger fires):
    validate user zone
    compute loss
    send to fraud model
👉 Ensures:
	•	Automatic claim initiation
	•	Zero manual intervention
💰 6. Automated Payout Workflow
Trigger → Risk validation → Fraud check → Payout calculation → Payment API
•⁠  ⁠Payment via Razorpay / UPI (test mode)

⸻

🔐 7. Continuous Learning Loop
System improves over time:
New data → retrain models → better risk prediction → better pricing
•⁠  ⁠Store:
	•	Trigger history
	•	Claim outcomes
	•	Fraud patterns


🛡️ Adversarial Defense & Anti-Spoofing Strategy
🎯 Problem
Coordinated fraud attacks such as GPS spoofing allow users to fake their location and trigger mass payouts without actual disruption exposure. A single-signal system (GPS-only) is insufficient.
🔍 Multi-Signal Location Verification
We replace GPS-only validation with a multi-signal approach:

location_valid = (
    GPS_location ≈ Network_location
    AND IP_location ≈ Registered_city
)
GPS alone can be spoofed
Network and IP consistency make spoofing significantly harder
🚶 Movement & Behavior Validation
We verify whether the worker is genuinely active:

IF (user_speed < threshold for long duration)
AND (no movement pattern detected)
THEN suspicious_activity = TRUE

Detects stationary users falsely claiming disruption
Prevents “at-home” fraud scenarios
📦 Platform Activity Verification
We cross-check delivery activity (simulated):

IF (no deliveries OR no active sessions during disruption window)
THEN activity_mismatch = TRUE
Ensures user was actually working during the disruption
Strong signal against coordinated fake claims

fraud_score =
    w1 × location_mismatch +
    w2 × movement_anomaly +
    w3 × activity_mismatch +
    w4 × claim_frequency +
    w5 × device_behavior

    Decision Thresholds
Score
Decision
0–19  Auto-approve
20–49 Soft flag → payout delayed
50–100  Reject

 # Claim Validation Flow

Trigger Detected
        ↓
Multi-Signal Validation (GPS + Network + IP)
        ↓
Movement Validation
        ↓
Activity Validation
        ↓
Policy + Duplicate Check
        ↓
Fraud Detection Model
        ↓
Decision Engine
        ↓
Payout / Hold / Reject

# Architecture Update
Trigger Engine
        ↓
Multi-Signal Validation Layer   ← NEW
        ↓
Fraud Detection Model
        ↓
Payout System


Note:
A soft-flag system ensures genuine users are not penalized due to network drops or temporary inconsistencies.
**Rule-based layer (5 checks):**
- Duplicate claim detection — same trigger already claimed today
- Claim frequency analysis — sliding 7-day and 30-day windows
- City/zone mismatch — trigger city vs worker's registered city
- Policy validity — was the policy active when disruption occurred
- Income vs claim ratio — claim amount vs declared weekly income

**ML layer — Isolation Forest (scikit-learn):**
- Trained on 900 legitimate + 100 fraudulent synthetic claims
- Learns what normal claim behaviour looks like
- Flags statistically anomalous claims even when rules don't catch them
- Combined with rule scores into a final fraud score (0–100)

**Decision thresholds:**

| Score | Decision |
|-------|----------|
| 0–19 | Auto-approve, instant payout |
| 20–49 | Flag for human review, payout held |
| 50–100 | Reject, no payout, event logged |

### Model 3 — Predictive Disruption Analytics (`predictive_analytics.py`)

Uses 30 days of historical weather and disruption data per city to forecast next week's disruption probability. Shown on the admin dashboard so insurers can predict expected claim volumes and manage loss ratios proactively.

---

## Platform Choice: Web App (React)

We chose a React web application over a mobile app because:

- Accessible on any phone browser — no app download or storage needed
- Works on low-end Android devices that delivery partners typically use
- Faster to build and deploy within the hackathon timeline
- Admin dashboard for insurers is better suited to a browser interface
- Single codebase serves both workers and insurer admins

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React.js + Tailwind CSS | Worker app and admin dashboard |
| Backend | Node.js + Express | REST API gateway and business logic |
| Database | MongoDB Atlas (free tier) | Workers, Policies, Claims, Trigger logs |
| ML Models | Python + scikit-learn + Flask | Fraud detection, risk scoring, predictions |
| Weather API | OpenWeatherMap (free tier) | Rain, temperature, flood triggers |
| AQI API | AQICN / WAQI (free tier) | Pollution trigger |
| Payments | Razorpay test mode | Simulated UPI payouts |
| Hosting | Vercel (frontend) + Render (backend) | Free tier deployment |

---

## Development Plan

### Phase 1 — Ideation and Foundation (March 4–20) ✅
- [x] Define persona and real-world disruption scenarios
- [x] Design weekly premium model with income-linked formula
- [x] Define 5 parametric triggers with thresholds and payout formulas
- [x] Build fraud detection ML model (Isolation Forest — scikit-learn)
- [x] Define system architecture and tech stack
- [x] Set up GitHub repository and README

### Phase 2 — Automation and Protection (March 21–April 4)
- [ ] Worker registration and login (JWT auth)
- [ ] AI risk scoring at onboarding → dynamic weekly premium generated
- [ ] Policy buy flow with mock UPI payment (7-day validity)
- [ ] Trigger engine — cron job polling weather and AQI APIs every 30 mins
- [ ] Auto-claim creation when any trigger threshold is crossed
- [ ] Fraud detection integrated into claims pipeline
- [ ] Mock payout via Razorpay test mode
- [ ] Worker dashboard — policy status, active coverage, claims history

### Phase 3 — Scale and Optimise (April 5–17)
- [ ] Predictive disruption analytics model for admin dashboard
- [ ] Advanced fraud checks — GPS spoof detection, pattern analysis
- [ ] Admin dashboard — loss ratio, city disruption map, fraud flags
- [ ] Full Razorpay sandbox payout simulation
- [ ] 5-minute demo video showing simulated disruption → auto payout
- [ ] Final pitch deck (PDF)

---

---

## Critical Constraints

1. **Income loss only** — GigShield covers lost earnings during verified disruption events only. Health, life, accident, and vehicle repair coverage are strictly excluded. Enforced at claim creation level — only the 5 parametric triggers above can generate a claim.

2. **Weekly pricing** — All premiums, policies, and billing are structured on a 7-day basis matching the gig worker earnings cycle. Workers buy, renew, or let policies lapse weekly.

---

*Guidewire DEVTrails 2026 — University Hackathon*
