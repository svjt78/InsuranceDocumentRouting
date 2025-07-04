```markdown
# 🏢 Insurance Document Management (InsDocRouting)

An intelligent, AI-driven document management and routing system for insurance operations. This application automates the ingestion, classification, and routing of unstructured documents—whether uploaded manually, sent via email, or dropped into AWS S3 buckets. It extracts key information from document contents and email metadata using OCR and LLMs, classifies documents into a configurable hierarchy, and routes them to destination buckets. Real-time dashboards, admin tools, and override capabilities enable transparency and operational control.

---

## 📦 Features

### 🔍 Document Ingestion & Classification
- Upload documents (PDF, image, etc.) via:
  - Frontend interface
  - AWS S3 bucket watch
  - Email (IMAP-based ingestion of attachments)
- Extract text using OCR worker (Tesseract + OpenCV).
- Classify documents using LLM against configurable hierarchy.
- Auto-route to appropriate AWS S3 destination bucket.

### 📧 Email-Based Ingestion & Metadata Extraction
- Fetch documents directly from a configured email inbox.
- Extract and OCR attachments (PDF, images).
- Parse **email subject**, **body**, and **attachment content** to extract:
  - 🧾 **Account Number**
  - 👤 **Policyholder Name**
  - 🪪 **Policy Number**
  - 🧷 **Claim Number**
- Store extracted metadata in PostgreSQL alongside the document record.
- Use metadata for enhanced classification, matching, or routing logic.

### 🧠 Hierarchical Document Classification
- Three-tier structure: **Department → Category → Subcategory**
- Tree-view UI for managing hierarchy.
- Editable and expandable by admin users.

### ⚙️ Bucket Mapping & Overrides
- Map subcategories to AWS S3 destination buckets.
- Auto-create destination buckets if not already present.
- Admin override of classification and rerouting.
- View parsed metadata during override for informed decision-making.

### 📊 Real-Time Dashboard & Metrics
- Visual widgets for:
  - Document status: Pending, Processed, Failed, Overridden, Rerouted
  - Daily volume trends
  - Latency analysis
  - Failure types
  - Override and reroute percentages
- Filter and drill down by department, date, or status.

---

## 🏗️ Tech Stack

| Layer           | Tech Stack                                 |
|------------------|---------------------------------------------|
| **Frontend**     | Next.js, React.js, Tailwind CSS, Recharts   |
| **Backend**      | FastAPI, Python, SQLAlchemy, Pydantic       |
| **OCR**          | Tesseract, OpenCV                           |
| **AI Classification** | OpenAI GPT (or compatible LLM)          |
| **Storage**      | AWS S3 (Document Buckets), PostgreSQL       |
| **Messaging (optional)** | RabbitMQ (for async processing)        |
| **Deployment**   | Docker, Docker Compose                      |

---

## 🚀 How It Works

1. **Ingestion**  
   - Documents arrive via UI, AWS S3 bucket, or email inbox.
2. **OCR & Text Extraction**  
   - `ocr_worker.py` converts scanned PDFs/images into raw text.
3. **Classification**  
   - `classifier.py` uses LLM to assign Department, Category, Subcategory.
4. **Email Parsing**  
   - Email subject and body parsed for account and policy metadata.
5. **Routing**  
   - `destination_service.py` maps subcategory to AWS S3 destination.
6. **Monitoring & Overrides**  
   - Admin dashboard displays statuses, allows rerouting, and shows metrics.

---

## 📁 Project Structure (Simplified)

```

backend/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── db.py
│   ├── classifier.py
│   ├── ocr\_worker.py
│   ├── email\_ingestor.py
│   ├── destination\_service.py
│   └── ...
frontend/
├── pages/
├── components/
├── metrics/widgets/
├── styles/
└── ...
docker-compose.yml
README.md

````

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/insurance-doc-mgmt.git
cd insurance-doc-mgmt
````

### 2. Configure Environment Variables

Create `.env` files for backend and frontend:

```env
# Backend (.env)
POSTGRES_URL=postgresql://user:pass@db:5432/docs
S3_ENDPOINT=https://s3.amazonaws.com
S3_BUCKET_PREFIX=ins-docs
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
OPENAI_API_KEY=your_openai_key
IMAP_SERVER=imap.mailserver.com
EMAIL_USERNAME=docrouter@yourdomain.com
EMAIL_PASSWORD=your_email_password
```

### 3. Start the App with Docker

```bash
docker-compose up --build
```

### 4. Access the App

* **Frontend UI**: `http://localhost:3000`
* **FastAPI Backend Docs**: `http://localhost:8000/docs`

---

## 📊 Sample Dashboard Widgets

* **StatusDonut** – Visualize processed vs failed vs rerouted documents
* **LatencyBars** – Highlight processing delays
* **DailyVolumeLine** – Track documents ingested daily
* **BacklogBig** – Real-time pending backlog display
* **RerouteDonut** – Show proportion of manually rerouted documents

---

## 🧪 Future Enhancements

* 🔄 Feedback-based LLM retraining on misclassifications
* 📨 Automated alerts on high failure rates or latency spikes
* 📥 Drag-and-drop local uploads into S3-backed staging area
* 🔐 Role-based access with audit trails
* 📎 PDF form field extraction & structured ingestion

---

## 👨‍💻 Maintainers

**Suvojit Dutta** – Insurance Domain Architect & AI Solutions Leader
*Contributions welcome!*
See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

---

## 📜 License

This project is licensed under the MIT License.
See the [`LICENSE`](LICENSE) file for details.

