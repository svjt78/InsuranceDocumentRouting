Insurance Document Routing
# AI-powered intake, classification, and routing that turns every insurance document into instant, actionable data.

## Why InsDocRouting?

Insurance carriers and TPAs handle **tens of thousands of unstructured documents** every day—policies, endorsements, claim photos, correspondence, and more.  
Manual triage slows down service, drives up cost, and risks compliance gaps.  

**InsDocRouting** turns that paper flood into a friction-free, API-driven workflow:

* **Ingest anywhere** – UI upload, S3 drop, or email feed.  
* **Understand** – OCR & LLM extract key facts (account, policy, claim).  
* **Decide** – AI classifier slots each doc into a configurable 3-tier taxonomy.  
* **Deliver** – Routed to the correct S3 bucket and downstream system—zero clicks.

All activity is surfaced in real-time dashboards with full audit trails.

---

## Feature Highlights

| Domain | What you get |
|-----------|--------------|
| **Multi-Channel Intake** | Drag-and-drop UI, S3 landing bucket watcher, high-volume email attachment capture |
| **Smart Extraction** | Tesseract + OpenCV OCR, GPT-powered entity parsing (Account #, Policy #, Claim #, Insured Name) |
| **Guidewire-Friendly Model** | Account → Policy → Claim hierarchy stored in PostgreSQL for instant lookup |
| **Configurable Classification** | Admin UI to manage Department › Category › Subcategory tree; overrides in one click |
| **Autonomous Routing** | Subcategory ↦ destination S3 bucket with auto-creation, retries, and DLQ |
| **Reliable Async Core** | Outbox table + RabbitMQ ensures at-least-once delivery without race conditions |
| **Operational Visibility** | Live backlog, SLA latency heatmaps, reroute ratios, failure breakdowns |
| **Security & PII** | SSN masking, RBAC, TLS-only comms, full audit logs |

---

## At-a-Glance Architecture

```mermaid
flowchart LR
    subgraph Intake
        UI[User Upload] --> OB
        Email[Email Worker] --> OB
        S3[S3 Watcher] --> OB
    end
    OB[Outbox Table] --> MQ((RabbitMQ))
    MQ --> OCR[OCR / Metadata Worker]
    OCR --> CLS[LLM Classifier]
    CLS --> RTR[Router]
    RTR --> S3DST[(Destination S3)]
    RTR --> DB[(PostgreSQL)]
    DB --> DASH[Metrics Dashboard]

Everything ships in one docker-compose up.

## Tech Stack
Layer	Tech
Backend	FastAPI • Python 3.11 • SQLAlchemy • Pydantic
Frontend	Next.js (React 18) • Tailwind CSS • Recharts
AI / NLP	OpenAI GPT (pluggable)
OCR	Tesseract • OpenCV
Messaging	RabbitMQ (Outbox pattern)
Storage	AWS S3 • PostgreSQL
Container	Docker & Compose
 
## Get Started in 5 Minutes
bash
CopyEdit
# 1. Clone
git clone https://github.com/your-org/insurance-doc-mgmt.git
cd insurance-doc-mgmt

# 2. Configure
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# → fill in AWS keys, DB creds, OpenAI key, etc.

# 3. Launch
docker-compose up --build

# 4. Explore
# UI         → http://localhost:3000
# API docs   → http://localhost:8000/docs
 
## Security & PII
•	Masking – SSNs and other PII are stored only in redacted form.
•	RBAC – Admins may override routing; every action is timestamped and logged.
•	Transport Security – All external endpoints (API, email, S3) require TLS.
•	Compliance Ready – Architecture aligns with SOC 2 “Security” and “Confidentiality” controls.
 
## Roadmap (selected)
•	Feedback-loop retraining for the classifier
•	SLA breach alerts via Slack / Teams
•	Resumable bulk uploads with client-side checksum
•	Fine-grained tenant isolation & audit export
•	ACORD / ISO smart-form parsing
 
## Contributing
1.	Fork the repo & create your branch: git checkout -b feature/my-feature
2.	Commit with Conventional Commits (feat: …, fix: …)
3.	Push & open a PR – the CI pipeline will lint, test, and build containers.
See CONTRIBUTING.md for full guidelines.
 
 
## License
Released under the MIT License. Commercial support available—contact the maintainer for details.


