# 📌 Project FIND — AI Face Recognition Surveillance System

🚨 **Project FIND** is an AI-powered real-time face recognition surveillance and communication system designed to assist police and security teams in identifying missing persons during large public gatherings.

It provides a public reporting portal, live monitoring system, human verification workflow, audit trail logging, and automated alert escalation using n8n.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Project Overview

Project FIND combines cutting-edge computer vision, real-time video processing, and workflow automation to create a comprehensive missing person identification system. The system features a human-in-the-loop verification process to ensure accuracy and accountability while leveraging AI for rapid face matching.

---

## 🧠 Key Features

### ✅ Missing Person Reporting Portal
- **Upload Missing Person Photo**: Simple interface for image submission
- **Enter Details**: Name, Age, Notes, and other identifying information
- **Face Embedding Generation**: Uses InsightFace (buffalo_l model) for high-accuracy embeddings
- **Secure Storage**: All data stored securely in SQLite database

### ✅ Real-Time Surveillance Matching
- **Live Face Detection**: Webcam-based continuous monitoring using OpenCV
- **Database Matching**: Compares detected faces against registered missing persons
- **Confidence-Based Detection**: Three-tier classification system
  - 🟩 **Strong Match** (≥ 0.80)
  - 🟨 **Probable Match** (0.65 – 0.80)
  - 🟥 **Unknown** (< 0.65)

### ✅ Human-in-the-Loop Verification
- **Operator Confirmation**: Manual review of AI-suggested matches
- **False Alert Prevention**: Reduces false positives through human oversight
- **Accountability**: Every decision is logged and traceable

### ✅ Comprehensive Audit Trail
Every match is logged with:
- Confidence score
- Camera location
- Operator decision (confirmed/rejected)
- Timestamp
- Escalation level
- Acknowledgment status

### ✅ Automated Alert System (n8n Integration)
- **Conditional Alerts**: Triggered only on confirmed matches
- **Webhook Integration**: RESTful API for alert dispatch
- **Multi-Channel Notifications**: Email / SMS / WhatsApp via Twilio, Gmail, etc.
- **Escalation Levels**: Configurable alert priority system

### ✅ Admin Control Panel
- View and manage missing persons database
- Review complete match log history
- Delete/update missing person entries
- Real-time dashboard UI
- System status monitoring

---

## 🏗️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend UI** | Streamlit |
| **AI Model** | InsightFace (buffalo_l) |
| **Face Detection** | ONNX Runtime |
| **Database** | SQLite |
| **Automation** | n8n Webhooks |
| **Video Engine** | OpenCV |
| **Matching Logic** | Cosine Similarity |
| **Backend Language** | Python 3.8+ |

---

## 📂 Project Structure

```
face_surveillance_system/
│
├── main.py                          # Streamlit entry point
│
├── app/
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── admin_controller.py      # Admin panel logic
│   │   ├── camera_controller.py     # Camera control
│   │   ├── monitor_controller.py    # Monitoring logic
│   │   └── report_controller.py     # Report submission
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── face_service.py          # Face detection & embedding
│   │   ├── matching_service.py      # Face matching algorithms
│   │   ├── db_service.py            # Database operations
│   │   ├── alert_service.py         # n8n webhook integration
│   │   ├── status_service.py        # System status management
│   │   └── storage_service.py       # File storage handling
│   │
│   ├── views/
│   │   ├── __init__.py
│   │   ├── report_view.py           # Report missing person UI
│   │   ├── monitor_view.py          # Live monitoring UI
│   │   ├── admin_view.py            # Admin dashboard UI
│   │   ├── analytics_view.py        # Analytics dashboard
│   │   ├── home_view.py             # Landing page
│   │   └── ui_utils.py              # Shared UI components
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── person_model.py          # Missing person data model
│   │   └── match_log_model.py       # Match log data model
│   │
│   ├── data/
│   │   ├── embeddings/              # Stored face embeddings
│   │   ├── uploaded_faces/          # Uploaded images
│   │   ├── test_faces/              # Test dataset
│   │   └── logs/                    # System logs
│   │
│   ├── db/
│   │   ├── app.db                   # SQLite database
│   │   └── backups/                 # Database backups
│   │
│   ├── runtime/
│   │   └── camera_status.json       # Camera sync status
│   │
│   └── config/                       # Configuration files
│
├── tests/                            # Unit and integration tests
├── temp_uploads/                     # Temporary file storage
├── venv/                             # Virtual environment
│
├── requirements.txt                  # Python dependencies
├── .env                              # Environment variables
├── .gitignore                        # Git ignore rules
├── secrets.toml                      # Streamlit secrets
├── vision_engine.py                  # OpenCV camera engine
├── debug_sth.py                      # Debug utilities
├── force_clear_all.py                # Database reset utility
└── README.md                         # This file
```

---

## ⚙️ Setup Instructions

### ✅ 1. Clone Repository
```bash
git clone <your-repo-link>
cd face_surveillance_system
```

### ✅ 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### ✅ 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `streamlit` - Web application framework
- `insightface` - Face recognition model
- `onnxruntime` - Model inference
- `opencv-python` - Video processing
- `numpy` - Numerical operations
- `pillow` - Image processing
- `requests` - HTTP client for webhooks

### ✅ 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# n8n Webhook Configuration
N8N_WEBHOOK_URL=http://localhost:5678/webhook/confirmed-match

# Database Configuration
DB_PATH=app/db/app.db

# Camera Configuration
DEFAULT_CAMERA_ID=0
CAMERA_LOCATION=Main Gate Camera

# Confidence Thresholds
STRONG_MATCH_THRESHOLD=0.80
PROBABLE_MATCH_THRESHOLD=0.65

# Alert Configuration
ENABLE_ALERTS=True
MAX_ESCALATION_LEVEL=3
```

### ✅ 5. Initialize Database

The database will automatically initialize on first run. To manually reset:

```bash
python force_clear_all.py
```

### ✅ 6. Run Streamlit App
```bash
streamlit run main.py
```

**App will run at:** `http://localhost:8501`

---

## 🗄️ Database Schema

### MISSING_PERSONS Table
```sql
CREATE TABLE MISSING_PERSONS (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER,
    notes TEXT,
    image_path TEXT,
    embedding BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active'
);
```

### MATCH_LOGS Table
```sql
CREATE TABLE MATCH_LOGS (
    id TEXT PRIMARY KEY,
    person_id TEXT,
    confidence REAL,
    camera_location TEXT,
    match_time TIMESTAMP,
    operator_decision TEXT,
    escalation_level INTEGER,
    acknowledged BOOLEAN DEFAULT FALSE,
    notes TEXT,
    FOREIGN KEY (person_id) REFERENCES MISSING_PERSONS(id)
);
```

**Database Location:** `app/db/app.db`

---

## 📸 How the System Works

### 1️⃣ Report Missing Person
1. User navigates to "Report Missing Person" page
2. Uploads photo of missing person
3. Enters details (Name, Age, Notes)
4. AI generates face embedding using InsightFace
5. Data stored in SQLite database
6. Confirmation message displayed

### 2️⃣ Live Monitoring
1. Operator starts camera from Streamlit UI
2. OpenCV engine (`vision_engine.py`) launches in separate process
3. Real-time face detection on webcam feed
4. Face embeddings extracted for each detected face
5. Embeddings compared against database using cosine similarity
6. Matches above threshold logged as "pending"

### 3️⃣ Pending Match Logging
- High-confidence matches (≥ 0.65) stored as pending
- Match details include:
  - Person ID
  - Confidence score
  - Camera location
  - Timestamp
  - Frame capture (optional)

### 4️⃣ Human Verification
1. Pending matches appear in control room dashboard
2. Operator reviews side-by-side comparison
3. Operator confirms or rejects match
4. Decision logged in audit trail
5. Rejected matches archived for review

### 5️⃣ Automated Alerts
**On Confirmation:**
1. n8n webhook triggered with match data
2. Alert payload sent to configured endpoints
3. Email/SMS/WhatsApp notifications dispatched
4. Escalation workflow initiated based on level
5. Alert acknowledgment tracked

---

## 🔔 n8n Integration (Webhook Alerts)

### Webhook Endpoint
```
http://localhost:5678/webhook/confirmed-match
```

### Payload Structure
```json
{
  "person_id": "abcd-1234-5678-efgh",
  "name": "John Doe",
  "age": 28,
  "confidence": 0.88,
  "camera_location": "Main Gate Camera",
  "match_time": "2026-01-25T12:30:00",
  "escalation_level": 2,
  "acknowledged": false,
  "operator": "Officer Smith",
  "notes": "Confirmed match with high confidence"
}
```

### Sample n8n Workflow
1. **Webhook Trigger**: Receive confirmed match data
2. **Condition Node**: Check escalation level
3. **Email Node**: Send alert to supervisor
4. **SMS Node**: Send SMS via Twilio (escalation level ≥ 2)
5. **Database Node**: Log alert in external system
6. **HTTP Response**: Return acknowledgment

---

## 🎥 Running the Camera System

### Starting Camera
1. Navigate to "Live Monitoring" page in Streamlit
2. Click "Start Camera" button
3. OpenCV window launches showing live feed
4. Face detection boxes appear in real-time
5. Matches displayed with confidence scores

### Stopping Camera
- **Method 1**: Press `Q` key in OpenCV window
- **Method 2**: Click "Stop Camera" in Streamlit UI

### Camera Configuration
Edit `vision_engine.py` to customize:
- Camera ID (default: 0)
- Detection frequency
- Frame resolution
- Face detection parameters

---

## 🟡 Confidence Level System

| Confidence Range | Label | Color | Action |
|-----------------|-------|-------|--------|
| **≥ 0.80** | Strong Match | 🟩 Green | Immediate notification |
| **0.65 – 0.80** | Probable Match | 🟨 Yellow | Requires verification |
| **< 0.65** | Unknown | 🟥 Red | No action (logged only) |

---

## 🛡️ Security & Privacy Notes

⚠️ **Important Disclaimer:**

This prototype is intended for **educational and demonstration purposes only**.

### For Production Deployment, Implement:

#### Data Security
- **Encryption**: Encrypt stored images and embeddings
- **Secure Transmission**: HTTPS for all communications
- **Access Control**: Role-based permissions (RBAC)
- **Data Retention**: Automated deletion policies

#### Authentication & Authorization
- **User Authentication**: Multi-factor authentication (MFA)
- **Session Management**: Secure session handling
- **API Security**: API key management and rate limiting

#### Legal Compliance
- **GDPR Compliance**: Data protection regulations
- **Privacy Laws**: Local surveillance laws
- **Consent Management**: Informed consent for image capture
- **Data Subject Rights**: Right to deletion, access, correction

#### System Security
- **Input Validation**: Prevent SQL injection, XSS
- **Secure Camera Feeds**: Encrypted video streams
- **Audit Logs**: Tamper-proof logging
- **Backup & Recovery**: Regular automated backups

---

## 📊 Future Enhancements

### 🚀 Planned Features

#### Multi-Camera Support
- Manage multiple camera feeds simultaneously
- Camera grid view dashboard
- Zone-based monitoring
- Camera health monitoring

#### Advanced AI Capabilities
- **Face Mask Detection**: Identify partially occluded faces
- **Age Progression**: Match aged photos
- **Demographic Analysis**: Age/gender estimation
- **Emotion Detection**: Distress signals

#### Cloud Deployment
- AWS/Azure/GCP deployment
- Scalable architecture
- Load balancing
- CDN for static assets

#### Analytics Dashboard
- Real-time statistics
- Historical trend analysis
- Heatmaps of detection locations
- Performance metrics

#### Enhanced Workflow
- **Geo-location Alerts**: Location-based notifications
- **Supervisor Escalation**: Multi-tier approval workflow
- **Scheduled Reports**: Automated daily/weekly summaries
- **Mobile App**: iOS/Android companion app

#### Integration Enhancements
- **CCTV Integration**: Connect to existing surveillance systems
- **Third-party APIs**: Government databases, Amber Alert systems
- **Export Functionality**: PDF reports, CSV exports
- **Backup Automation**: Cloud backup integration

---

## 🏆 Project Highlights

This project demonstrates advanced skills in:

✅ **Computer Vision**
- Face detection and recognition
- Real-time video processing
- Embedding-based similarity matching

✅ **AI & Machine Learning**
- Deep learning model integration (InsightFace)
- ONNX model optimization
- Threshold-based classification

✅ **Full-Stack Development**
- Frontend: Streamlit UI
- Backend: Python services architecture
- Database: SQLite schema design

✅ **System Architecture**
- MVC pattern implementation
- Service-oriented architecture
- Modular, maintainable codebase

✅ **Workflow Automation**
- n8n webhook integration
- Alert escalation logic
- Multi-channel notifications

✅ **DevOps & Deployment**
- Environment configuration
- Database migration scripts
- Debug and testing utilities

---

## 🛠️ Troubleshooting

### Common Issues

#### Camera Not Starting
```bash
# Check camera permissions
# Try different camera ID
python vision_engine.py --camera-id 1
```

#### Database Connection Error
```bash
# Reset database
python force_clear_all.py
```

#### n8n Webhook Not Triggering
- Verify n8n is running on port 5678
- Check webhook URL in `.env`
- Test webhook manually:
```bash
curl -X POST http://localhost:5678/webhook/confirmed-match \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

#### Low Detection Accuracy
- Ensure good lighting conditions
- Adjust confidence thresholds in config
- Update to higher resolution camera
- Retrain with more training data

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit your changes
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. Push to the branch
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request

### Contribution Guidelines
- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation
- Test thoroughly before submitting

---

## 📝 License

This project is open-source and available under the **MIT License**.

---


### Get in Touch
- **GitHub Issues**: For bug reports and feature requests
- **Email**: [kishoreachennai@gmail.com]
- **LinkedIn**: [https://www.linkedin.com/in/kishore-a-95b9052b4/]

---

## 🎓 Acknowledgments

### Technologies & Libraries
- **InsightFace**: State-of-the-art face recognition
- **Streamlit**: Rapid web app development
- **OpenCV**: Computer vision library
- **n8n**: Workflow automation platform

### Inspiration
This project was inspired by real-world needs in public safety and the potential of AI to assist in humanitarian efforts.

---

## ⭐ Support

If you found this project useful or interesting:
- ⭐ **Star this repository** on GitHub
- 🍴 **Fork** and contribute
- 📢 **Share** with others
- 💬 **Provide feedback** via issues

---

## 📚 Additional Resources

### Documentation
- [InsightFace Documentation](https://github.com/deepinsight/insightface)
- [Streamlit Docs](https://docs.streamlit.io/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [n8n Documentation](https://docs.n8n.io/)


**⚖️ Ethical Use Statement**

This system is designed to aid in finding missing persons and should be used responsibly, ethically, and in compliance with all applicable laws and regulations. Always obtain proper authorization and consent before deploying surveillance systems.

---

<div align="center">

**Project FIND** - Helping reunite families through AI 💙

*Built with ❤️ and cutting-edge AI technology*

</div>
