# Insurance Document Management System ................................................................... 1
## Value Prop and Features ................................................................................................................ 1
## Technologies Used ................................................................................................. 2
## Architecture ........................................................................................................... 3
## Setup and Installation ............................................................................................ 3
### Prerequisites ........................................................................................................ 3
### Getting Started ..................................................................................................... 3
1. **Clone the Repository:** ................................................................................... 4
2. **Project Structure:** ......................................................................................... 4
3. **Environment Configuration (`.env`):** .............................................................. 5
4. **Run with Docker Compose:** ........................................................................... 6
5. **Access the Services:** ..................................................................................... 6
## Configuration ......................................................................................................... 6
## Contributing and Future Enhancements .................................................................. 7

## Value prop and Features

1. Industry Problem Addressed
The insurance industry faces significant challenges in managing the high volume and diverse formats of incoming documents and correspondence. Traditional manual processes for document handling, analysis, classification, and routing are time-consuming, prone to human error, and limit scalability, especially during peak periods like those following natural disasters. Furthermore, extracting key information, summarizing content, identifying action items, and ensuring the secure handling of sensitive personal information (PII) within these documents adds complexity and cost. These inefficiencies can lead to delays in processing, increased operational costs, and potential compliance risks.

2. Solutions Offered
Our AI-based insurance document routing application provides a comprehensive, automated solution to address these problems. Key features and components include:

    •	Automated Document Ingestion & Processing: The application automatically retrieves incoming documents (PDFs, images, scanned documents, Word files, emails) via a notification service. It processes documents using OCR (specifically Tesseract + OpenCV, with preprocessing for poor quality images) to extract text and metadata.
    
    •	Intelligent Classification & Routing: Leveraging a Large Language Model (LLM), the system performs hierarchical classification, identifying the correct Department, Category, and Subcategory for each document based on pre-defined rules and a lookup table. Based on this classification, documents are automatically routed to the appropriate MinIO buckets configured for specific department/category/subcategory combinations.
    
    •	AI-Generated Summaries & Action Items: The LLM also generates concise bullet-point summaries of the document's key content and provides a checklist of recommended action items for recipients. PII is masked in these outputs.
    
    •	Human-in-the-Loop Dashboard: A user-friendly dashboard (built with React) provides a central control panel. It displays a real-time document queue, allows users (Document Management Specialists) to view document details (extracted text, classification, summary, action items), and offers the capability to manually override AI classifications and trigger re-processing. The dashboard also supports bulk actions for overrides/reclassification.
    
    •	Configuration Capabilities: The dashboard includes screens for dynamically managing organizational hierarchy (departments, categories, subcategories), configuring MinIO bucket mappings, and setting email notification recipients based on classification.
    
    •	Email Notifications: Configured email addresses receive automated notifications containing document details (classification, extracted text, summary, action items) and a link to the document in its destination bucket after successful processing. Manual overrides also trigger notifications with updated information.
    
    •	Metrics and Monitoring: The dashboard tracks key performance indicators such as average processing time, classification accuracy, summary usage, and documents requiring human re-routes, providing visibility into system performance. Audit logs are maintained for document routing and summaries.
    
    •	Modular Architecture: The solution is designed as a microservice architecture using Python (FastAPI) and containerization (Docker Compose for initial deployment, Kubernetes for scaling). This ensures flexibility, scalability, and ease of maintenance.

3. Quantitative Benefit for Insurers
Implementing this solution offers several quantitative benefits:
    •	Increased Processing Speed: Automating ingestion, OCR, classification, and routing allows for significant reduction in document processing time compared to manual methods,     supporting configurable real-time or near-real-time workflows. The ability to handle 5000 documents/day and factor in peak volumes ensures high throughput.

    •	Improved Operational Efficiency: Automated routing reduces the manual effort required to sort and deliver documents to the correct departments, freeing up staff for higher-value tasks. Features like bulk overrides further enhance efficiency for human review.

    •	Enhanced Accuracy: While starting with prompting, the system allows for collecting human feedback via overrides to continuously improve the AI model's accuracy over time through retraining, leading to more precise classification and fewer manual corrections in the long run. Classification accuracy is a tracked KPI.
    •	Reduced Costs: Streamlining document handling processes and reducing manual labor translates directly into lower operational costs.

    •	Faster Access to Information: Summaries and action items provide immediate insights into document content, accelerating downstream processing in policy, claims, underwriting, and other departments.

    •	Improved Compliance & Security: Masking PII like SSN/National ID directly addresses the requirement for handling sensitive data securely. Encrypting documents at rest adds another layer of security.


4. Architecture is designed with future-proofing in mind using open-source technology stack:
    1.	Microservices Architecture and Containerization: The solution is based on a containerized microservices design. This modular approach allows components (like the ingestion service, OCR worker (Tesseract), LLM classification service, database, and dashboard) to be developed, deployed, and scaled independently. Using Docker/Kubernetes for containerization facilitates migration between on-premises and cloud environments and supports scaling out workloads. Docker Compose is used for initial development, with a plan to move to Kubernetes for scalable production environments.
    
    2.	Environment Agnosticism: The architecture aims to be adaptable to both on-premises and cloud environments (AWS, Azure, Google Cloud). This is supported by the containerized design and the use of S3-compatible storage (MinIO initially), which allows for a smooth transition to cloud storage services like AWS S3. The potential future use of Infrastructure as Code tools like Terraform was also considered for managing resources in different environments.
    
    3.	Scalability and Performance: The design incorporates a queue-based system (RabbitMQ) to handle document processing asynchronously, which helps manage high volumes and potential peaks after events like natural disasters. The microservices design inherently supports scaling specific services that experience higher load. While auto-scaling wasn't required initially, the architecture can accommodate it for components like OCR, classification, and summarization workloads. The ability to switch between real-time and near-real-time (batch) ingestion modes via configuration provides flexibility in processing speed and resource usage.
    
    4.	Flexible AI/ML Pipeline:
        o	The plan starts with prompt engineering (zero/few-shot learning) using the OpenAI API to get the system running quickly and collect user feedback.

      	o	User feedback captured through manual overrides is saved to build a labeled dataset for future model retraining or fine-tuning. Options for retraining cadence (scheduled or event-triggered) were discussed.

      	o	The system is designed to dynamically look up the organizational hierarchy (departments, categories, subcategories) from the doc_hierarchy table for LLM classification. The LLM caches this hierarchy periodically, ensuring that the classification logic stays updated with configuration changes without requiring code modifications to the LLM worker.

      	o	The architecture is flexible enough to potentially transition to different LLMs or hybrid approaches (like embedding + ML classifiers) as needed.
    
    5.	Extensibility for Future Features:
        o	The architecture is designed to facilitate adding new functionalities later, such as automated claim settlement suggestions, fraud detection, or other insurance use cases. Tagging suspicious documents was considered for a future fraud pipeline.

      	o	Multi-language support is planned as a future enhancement, with the architecture designed to easily integrate language detection, translation, or multi-lingual NLP models. Specialized OCR engines often offer multi-language support.

      	o	The email notification functionality is planned as a separate, isolated capability to minimize impact on existing modules, using a modern email service (Resend) and background tasks for non-blocking operation.
        
    6.	Adaptable User Interface: The dashboard is built using Next.js with React and TailwindCSS, which are modern frameworks known for building responsive and performant single-page applications that can scale in complexity.
        o	The UI is explicitly designed to be fully responsive using TailwindCSS utilities, adapting to different screen sizes.

      	o	The inclusion of a configuration area in the dashboard allows administrators to dynamically manage settings like organizational hierarchy, MinIO bucket mappings, email notification settings, and ingestion mode, with changes stored in the database. This allows administrators to adapt the system to evolving business needs without developer intervention.

      	o	The authentication layer is designed to be pluggable, allowing a future switch from simple username/password to SSO integration.

      	o	Real-time updates via WebSockets are supported for the dashboard, providing users with up-to-date information on document processing status.

These design choices contribute to an application that is not only functional for the initial requirements but also flexible, scalable, and adaptable to future changes in technology, business needs, and user expectations.


List of Key Features:

* **Document Upload:** Upload insurance documents either via a dedicated API
endpoint or through system integrations.
* **Automated Processing:** Documents undergo Optical Character Recognition
(OCR), LLM-based classification, summarization, and action item extraction.
* **Document Storage:** Uploaded documents are stored in MinIO object storage.
* **Metadata Management:** Document metadata, extracted text, and processing
results are stored in a PostgreSQL database.
* **Hierarchical Classification:** Documents are classified into a predefined
organizational hierarchy (Department, Category, Subcategory).
* **Dashboard Overview:** A user-friendly dashboard (built with Next.js and
TailwindCSS) provides oversight of documents.
* **Document Listing & Detail View:** View a list of all processed documents and
detailed information for each.
* **Manual Classification Override:** Users can manually correct or override the
automated classification results via the dashboard.
* **Metrics Dashboard:** View key metrics such as document status breakdown, daily
processing volume, backlog, average latency, override rate, and reroute success rate.
* **Organizational Hierarchy Visualization:** View the document classification
hierarchy (Department, Category, Subcategory) on the dashboard, possibly as an
interactive org chart.
* **Real-time Updates:** The dashboard receives real-time updates on document
status changes via WebSockets.
* **Configuration Management:** Manage settings like bucket mappings and email
settings via dedicated endpoints/sections.

## Technologies Used
**Backend (FastAPI)**:
* **Framework:** FastAPI (Python)
* **Database:** PostgreSQL with SQLAlchemy (ORM)
* **Object Storage:** MinIO (S3-compatible) with boto3 client
* **Message Queue:** RabbitMQ with pika (or aio-pika)
* **OCR:** Tesseract + OpenCV
* **LLM Integration:** OpenAI API (or other models)
* **Dependency Management:** `requirements.txt` and pip
* **Web Server:** Uvicorn
* **Logging:** Standard Python logging
* **Configuration:** Environment variables managed via `.env` and `os.getenv`
**Frontend (Next.js)**:
* **Framework:** Next.js (React)
* **Styling:** TailwindCSS
* **State Management/Data Fetching:** Data integrated from FastAPI backend via
REST endpoints.
* **Real-time Communication:** WebSockets for live updates.
**Containerization & Orchestration:**
* **Development:** Docker Compose
* **Production (Future):** Kubernetes
**Other Tools:**
* **Development Environment:** VS Code
* **Version Control:** Git/GitHub
* **API Documentation:** Swagger UI (auto-generated by FastAPI)
  
## Architecture
The application follows a microservice-like architecture. The core components include:
* **FastAPI Backend:** Handles API requests (uploads, document retrieval, overrides),
interacts with the database and storage, and publishes messages to the queue.
* **Workers (OCR, Classification, PII Masking):** Separate logical components (initially
part of the backend service in the provided structure) that consume messages from
RabbitMQ to perform processing tasks.
* **PostgreSQL Database:** Stores document metadata, classification results,
summaries, action items, and configuration data (like bucket mappings and hierarchy).
* **MinIO Storage:** Stores the raw document files.
* **RabbitMQ Message Queue:** Decouples the upload/ingestion process from the
processing workers.
* **Next.js Frontend (Dashboard):** Provides the user interface for uploading, viewing,
managing documents, and seeing metrics.
The flow typically involves a user uploading a document via the `/upload` endpoint or via
system integrations, the backend saving it to MinIO and creating a database record, and
then publishing a message to RabbitMQ to trigger the processing OCR workers for
information extraction, classification and processing.

## Setup and Installation
These instructions guide you through setting up and running the project locally using
Docker Compose.

### Prerequisites
* Docker and Docker Compose
* Python 3.9+ (for local development outside Docker, if needed)
* Node.js (for local frontend development outside Docker, if needed)
* VS Code (Recommended IDE)
* 
### Getting Started
1. **Clone the Repository:**
```bash
git clone https://github.com/svjt78/InsuranceDocumentRouting.git
cd InsDocRouting
```
2. **Project Structure:**
Ensure your project follows a structure similar to this:
```
project-root/
├── backend/
│ ├── app/
│ │ ├── __init__.py
│ │ ├── main.py
│ │ ├── config.py
│ │ ├── database.py
│ │ ├── models.py
│ │ ├── rabbitmq.py
│ │ ├── ocr_worker.py # Worker logic (could be separate service)
│ │ ├── llm_classifier.py # Worker logic (could be separate service)
│ │ ├── pii_masker.py # Worker logic (could be separate service)
│ │ ├── bucket_mappings.py # Backend endpoint/logic
│ │ ├── email_settings.py # Backend endpoint/logic
│ │ ├── seed_data/ # Data seeding scripts/files
│ │ │ ├── __init__.py
│ │ │ ├── seed_hierarchy.py
│ │ │ └── doc_hierarchy.json
│ │ ├── routes/ # Separate routers (e.g., doc_hierarchy)
│ │ │ ├── __init__.py
│ │ │ └── doc_hierarchy.py
│ │ ├── metrics/ # Metrics module
│ │ │ ├── __init__.py
│ │ │ ├── router.py
│ │ │ ├── service.py
│ │ │ └── schemas.py
│ │ └── logging_config.py # If separate logging setup used
│ ├── requirements.txt
│ └── Dockerfile # or Dockerfile.dev, Dockerfile.prod etc.
├── frontend/
│ ├── public/
│ ├── src/
│ │ ├── pages/
│ │ ├── components/
│ │ └── styles/
│ ├── package.json
│ └── Dockerfile
├── .env # Contains all environment variables
├── docker-compose.yml
└── .gitignore # Prevents .env and other sensitive files from being committed
```
3. **Environment Configuration (`.env`):**
Create a file named `.env` in the **project root** directory (at the same level as
`docker-compose.yml` and the `backend` and `frontend` folders). Populate it with the
necessary variables.
```env
# === DATABASE CONFIG ===
POSTGRES_USER=user # User for the PostgreSQL service within Docker
POSTGRES_PASSWORD=pass # Password for the PostgreSQL service within
Docker
POSTGRES_DB=db_name # Database name for the PostgreSQL service within
Docker
DATABASE_URL=postgresql://user:pass@db:5432/db_name # Connection URL for
the backend
# === RABBITMQ CONFIG ===
RABBITMQ_URL=amqp://rabbitmq:5672/ # Connection URL for the backend
# === MINIO CONFIG ===
MINIO_URL=http://minio:9000 # Connection URL for the backend
AWS_ACCESS_KEY_ID=minioadmin # Access Key for backend to connect to MinIO
(using boto3 naming)
AWS_SECRET_ACCESS_KEY=minioadmin # Secret Key for backend to connect to
MinIO (using boto3 naming)
MINIO_ROOT_USER=minioadmin # Root user for the MinIO service itself
MINIO_ROOT_PASSWORD=minioadmin # Root password for the MinIO service
itself
MINIO_BUCKET=documents # Default bucket name
# === OPENAI CONFIG ===
OPENAI_API_KEY=your_openai_api_key_here # Replace with your OpenAI API key
# === TESSERACT CONFIG ===
TESSERACT_CMD=/usr/bin/tesseract # Command for Tesseract (likely this path
within the Docker container)
# === FRONTEND CONFIG ===
# URL for the frontend to connect to the backend API. Use the service name
'backend'
# if the frontend is running inside the same Docker network, or localhost if run
outside.
NEXT_PUBLIC_API_URL=http://backend:8000 # Use http://localhost:8000 if frontend
is not in Docker
```
**Note:** Ensure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
are present and match the MinIO credentials used by the backend service. The
`MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` are used by the MinIO
service container itself.
4. **Run with Docker Compose:**
Navigate to the project root directory in your terminal and run:
```bash
docker-compose down -v --remove-orphans # Clean up previous runs and volumes
docker-compose build --no-cache # Rebuild all services
docker-compose up # Start all services
```
*(Optional: Add `-d` to `docker-compose up` to run in detached mode)*.
5. **Access the Services:**
Once the services are running, you can access them at the following URLs:
* **Frontend Dashboard:** `http://localhost:3000` (or `http://localhost:3001` if
configured to run on port 3001)
* **Backend API Documentation (Swagger UI):** `http://localhost:8000/docs`
* **RabbitMQ Management Dashboard:** `http://localhost:15672` (Default
guest/guest credentials)
* **MinIO Console:** `http://localhost:9000` (or `http://localhost:9001` if configured
with `--console-address`) (Use the credentials from your `.env` file, e.g.,
`minioadmin`/`minioadmin`)
On startup, the backend will automatically create the necessary database tables and
seed the document hierarchy if the table is empty, and ensure the MinIO bucket exists.

## Configuration
All application configuration is managed via environment variables, typically loaded from
the `.env` file at the project root.
* Database credentials and connection URL.
* RabbitMQ connection URL.
* MinIO endpoint, access key, secret key, root user/password, and bucket name. Note
the distinction between keys used by the backend client (`AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`) and credentials used by the MinIO service itself
(`MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`).
* OpenAI API key.
* Tesseract command path.
* Frontend backend API URL.
* CORS origins are configured in `backend/app/main.py`.
Sensitive information like API keys and passwords should **only** be stored in the
`.env` file and **never** committed to version control. Ensure your `.gitignore` file
prevents this.

## Contributing and Future Enhancements
This project provides a solid foundation. Potential areas for contribution and future
enhancements include:
* Implementing the LLM training/feedback loop leveraging human feedback from the
dashboard.
* Mobile responsiveness
* Implementing the WebSocket real-time updates in the frontend.
* Adding more robust error handling and logging.
* Implementing Single Sign-On (SSO) for authentication.
* Transitioning to Kubernetes for production deployment.
* Setting up Continuous Integration/Continuous Deployment (CI/CD) pipelines.
* Adding integration tests.
* Implementing async DB sessions for improved performance.
Feel free to fork the repository, open issues, or submit pull requests.
