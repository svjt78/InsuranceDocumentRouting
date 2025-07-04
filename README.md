# 🏢 Insurance Document Management (InsDocRouting)

An intelligent, AI-driven document management and routing system purpose-built for insurance organizations. This application ingests unstructured documents, classifies them into a structured hierarchy, and routes them automatically to the appropriate processing buckets. Designed with modular microservices and a responsive admin dashboard, the platform empowers operations teams to configure document types, monitor metrics, and handle overrides—all in real-time.

---

## 📦 Features

### 🔍 Document Ingestion & Classification

* Upload documents (PDF, image, etc.) via frontend or AWS S3 bucket.
* Extract text using OCR worker (Tesseract + OpenCV).
* Classify documents using LLM (e.g., GPT-based) against a configurable document hierarchy.
* Auto-route documents to mapped destination buckets.

### 🧠 Hierarchical Doc Classification

* Hierarchy defined as **Department → Category → Subcategory**
* Admin interface to view, add, and edit hierarchy nodes.
* Each node supports routing configuration and labeling overrides.

### ⚙️ Bucket Mapping & Overrides

* Map subcategories to AWS S3 destination buckets.
* Override document classification manually via admin dashboard.
* Auto-create buckets if they don’t exist during routing.

### 📊 Real-Time Metrics & Dashboard

* Visual widgets: Donut charts, bar charts, volume trends, backlog counters.
* Track document status (Pending, Processed, Failed, Rerouted, Overridden).
* View latency, daily volumes, failure distribution, and more.

### 🔐 Configuration & Admin UI

* Upload & manage the document hierarchy (`doc_hierarchy.json`)
* Manage bucket mappings and email settings.
* Responsive UI with Tailwind CSS and Recharts.
* Tree view for browsing hierarchy.
* Document cards with actions (view, reroute, delete).

---

## 🏗️ Tech Stack

| Layer          | Tech                                      |
| -------------- | ----------------------------------------- |
| **Frontend**   | React.js, Next.js, Tailwind CSS, Recharts |
| **Backend**    | FastAPI, Python, Pydantic, SQLAlchemy     |
| **Storage**    | AWS S3, PostgreSQL                        |
| **OCR Worker** | Tesseract, OpenCV                         |
| **AI**         | OpenAI GPT / LLM for classification       |
| **Messaging**  | RabbitMQ (planned or future)              |
| **Deployment** | Docker, Docker Compose                    |

---

## 🚀 How It Works

1. **Document Upload**: User uploads a document or it's added to an AWS S3 bucket.
2. **OCR Processing**: Text extracted using `ocr_worker.py`.
3. **Classification**: Text passed to `classifier.py` to determine Department, Category, Subcategory.
4. **Routing**: `destination_service.py` routes it to the configured bucket.
5. **Status Update**: Document status updated in PostgreSQL and reflected in frontend.
6. **Dashboard Monitoring**: Admins monitor volumes, reroute failures, override misclassified items.

---

## 📁 Project Structure (Simplified)

```
backend/
  ├── app/
  │   ├── main.py
  │   ├── models.py
  │   ├── db.py
  │   ├── classifier.py
  │   ├── ocr_worker.py
  │   ├── destination_service.py
  │   └── ...
frontend/
  ├── pages/
  ├── components/
  ├── metrics/widgets/
  ├── styles/
  └── ...
docker-compose.yml
README.md
```

---

## ⚙️ Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/insurance-doc-mgmt.git
   cd insurance-doc-mgmt
   ```

2. **Environment Variables**
   Create `.env` files for frontend and backend with necessary values for:

   * PostgreSQL
   * AWS S3 credentials and bucket details
   * OpenAI API key
   * Milvus (if vector search enabled)

3. **Run with Docker**

   ```bash
   docker-compose up --build
   ```

4. **Access App**

   * Frontend: `http://localhost:3000`
   * Backend (FastAPI docs): `http://localhost:8000/docs`

---

## 🧪 Future Enhancements

* ✅ Intelligent reclassification on override feedback
* 📬 Email ingestion support via IMAP/SMTP
* 🧾 PDF form field extraction for structured documents
* 👥 Role-based access and audit trail
* 🔁 Scheduled OCR reprocessing and latency alerts

---

## 👨‍💻 Maintainers

* **Suvojit Dutta** – Insurance Domain Architect, AI Enthusiast
* Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
