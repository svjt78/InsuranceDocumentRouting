# Insurance Document Management System (InsDocRouting)

Insurance Document Management System is an intelligent, AI-driven document processing and routing platform designed for insurance operations. Built with FastAPI and Next.js, it automates the complete lifecycle of insurance documents—from ingestion and OCR processing to intelligent classification and routing to appropriate destinations.

## Features

- **Multi-Channel Ingestion**: Process documents from web uploads, email attachments, and AWS S3 bucket monitoring
- **Advanced OCR Processing**: Extract text from PDFs and images using Tesseract with OpenCV preprocessing
- **AI-Powered Classification**: Intelligent document categorization using OpenAI GPT models with hierarchical classification
- **Metadata Extraction**: Extract policy numbers, account details, and claim information from documents and emails
- **Smart Routing**: Automatically route documents to appropriate S3 buckets based on classification
- **Real-time Dashboard**: Comprehensive metrics and monitoring with interactive widgets
- **Override System**: Manual classification override with instant rerouting capabilities
- **Email Integration**: IMAP-based email processing with Microsoft Graph API support
- **WebSocket Updates**: Real-time document status notifications across the application

## Architecture

Insurance Document Management follows a microservices architecture pattern:

```
Frontend (Next.js) → FastAPI Backend → AI Services (OCR + LLM)
                                   ↘ PostgreSQL Database
                                   ↘ RabbitMQ Message Queue
                                   ↘ AWS S3 Storage
```

### Technology Stack

- **Frontend**: Next.js 12, React 18, Tailwind CSS, Recharts
- **Backend**: FastAPI, Python 3.9+, SQLAlchemy, Pydantic
- **AI/ML**: OpenAI GPT, Tesseract OCR, OpenCV
- **Database**: PostgreSQL with Alembic migrations
- **Message Queue**: RabbitMQ for async processing
- **Storage**: AWS S3 for document storage and routing
- **Email Processing**: IMAP, Microsoft Graph API integration
- **Deployment**: Docker containerization with Docker Compose

## Installation

### Prerequisites

- Python 3.9+ with pip
- Node.js 18+ with npm
- Docker and Docker Compose
- PostgreSQL database
- RabbitMQ message broker
- AWS S3 bucket access
- OpenAI API key for document classification

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd InsDocRouting
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker**
   ```bash
   docker-compose up --build -d
   ```

   The application will be available at:
   - **Frontend**: `http://localhost:3001`
   - **Backend API**: `http://localhost:8000`
   - **API Documentation**: `http://localhost:8000/docs`

### Manual Setup

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   alembic upgrade head
   python -m app.main
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Start Workers**
   ```bash
   # OCR Worker
   python -m app.ocr_worker
   
   # Email Worker
   python -m app.email_worker
   
   # Outbox Publisher
   python -m app.outbox_publisher
   ```

## Configuration

### Required Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/insurance_docs

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_S3_BUCKET=insurance-documents

# S3 Prefixes
S3_INPUT_PREFIX=input/documents
S3_OUTPUT_PREFIX=output

# AI/ML Configuration
OPENAI_API_KEY=your_openai_api_key
TESSERACT_CMD=/usr/bin/tesseract

# Message Queue
RABBITMQ_URL=amqp://user:password@localhost:5672/

# Email Processing
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
IMAP_SERVER=imap.gmail.com
EMAIL_POLL_INTERVAL=60

# Microsoft Graph API (Optional)
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
USER_EMAIL=your-user@company.com

# Notification System
RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=no-reply@yourdomain.com

# Application Settings
OUTBOX_POLL_INTERVAL=5
PRESIGNED_URL_EXPIRES_IN=3600
INGESTION_MODE=realtime
```

## API Endpoints

### Document Management
- `POST /upload` - Upload documents for processing
- `GET /documents` - List all processed documents
- `GET /document/{doc_id}` - Get specific document details
- `POST /document/{doc_id}/override` - Override document classification
- `GET /documents/{doc_id}/download` - Download processed document
- `DELETE /document/{doc_id}` - Delete document record

### Classification Hierarchy
- `GET /lookup/hierarchy` - Get document classification hierarchy
- `POST /lookup/hierarchy` - Create new classification node
- `PUT /lookup/hierarchy/{node_id}` - Update classification node
- `DELETE /lookup/hierarchy/{node_id}` - Remove classification node

### Bucket Management
- `GET /bucket-mappings` - List S3 bucket mappings
- `POST /bucket-mappings` - Create new bucket mapping
- `PUT /bucket-mappings/{mapping_id}` - Update bucket mapping
- `DELETE /bucket-mappings/{mapping_id}` - Remove bucket mapping

### Email Configuration
- `GET /email-settings` - Get email notification settings
- `POST /email-settings` - Configure email notifications

### Metrics & Analytics
- `GET /metrics/dashboard` - Dashboard widget data
- `GET /metrics/status-distribution` - Document status breakdown
- `GET /metrics/daily-volume` - Daily processing volume
- `GET /metrics/processing-latency` - Processing time analytics

### Account & Policy APIs (v1)
- `GET /api/v1/accounts` - List insurance accounts
- `POST /api/v1/accounts` - Create new account
- `GET /api/v1/policies` - List insurance policies
- `GET /api/v1/claims` - List insurance claims

### System Management
- `GET /ingestion-mode` - Get current ingestion mode
- `PUT /ingestion-mode` - Switch between realtime/batch processing
- `POST /api/v1/email-webhook` - Handle incoming email webhooks

## Database Schema

The application uses SQLAlchemy ORM with the following core models:

- **Document Models**: `Document1` with extracted text, classification, and routing information
- **Classification**: `DocHierarchy` with department/category/subcategory structure
- **Configuration**: `BucketMapping`, `EmailSetting` for system configuration
- **Messaging**: `MessageOutbox` for reliable message delivery

### Key Features

- **Hierarchical Classification**: Three-tier classification system (Department → Category → Subcategory)
- **Metadata Extraction**: Automatic extraction of account numbers, policy numbers, and claim numbers
- **Audit Trail**: Complete processing history with timestamps and status tracking
- **Error Handling**: Comprehensive error logging and recovery mechanisms

## Development

### Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/              # API v1 endpoints
│   │   ├── routes/           # FastAPI route handlers
│   │   ├── metrics/          # Dashboard metrics
│   │   ├── model_schemas/    # Pydantic models
│   │   ├── seed_data/        # Initial data setup
│   │   ├── service/          # Business logic services
│   │   ├── templates/        # Email templates
│   │   ├── main.py           # FastAPI application
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── ocr_worker.py     # OCR processing worker
│   │   ├── email_worker.py   # Email ingestion worker
│   │   ├── llm_classifier.py # AI classification service
│   │   └── destination_service.py # Document routing
│   ├── alembic/              # Database migrations
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── components/           # React components
│   ├── metrics/              # Dashboard widgets
│   ├── pages/                # Next.js pages
│   ├── styles/               # CSS and styling
│   └── package.json          # Node.js dependencies
├── alembic/                  # Database migrations
└── docker-compose.yml        # Container orchestration
```

### Key Components

- **OCR Worker**: Tesseract-based text extraction with image preprocessing
- **LLM Classifier**: OpenAI GPT integration for intelligent document classification
- **Email Worker**: IMAP and Microsoft Graph email processing
- **Destination Service**: Smart routing based on classification rules
- **WebSocket Manager**: Real-time updates for document status changes
- **Metrics Dashboard**: Interactive visualizations with Recharts

### Development Scripts

```bash
# Backend Development
uvicorn app.main:app --reload     # Start FastAPI dev server
python -m app.ocr_worker          # Run OCR worker
python -m app.email_worker        # Run email processor
alembic upgrade head              # Apply database migrations

# Frontend Development
npm run dev                       # Start Next.js dev server
npm run build                     # Build for production
npm run start                     # Start production server

# Database Management
alembic revision --autogenerate   # Generate new migration
alembic upgrade head              # Apply migrations
```

## Processing Pipeline

### Document Flow

1. **Ingestion**: Documents arrive via web upload, email, or S3 bucket monitoring
2. **OCR Processing**: Extract text from PDFs and images using Tesseract
3. **Metadata Extraction**: Parse document content and email headers for insurance metadata
4. **AI Classification**: Use OpenAI GPT to classify documents into hierarchical categories
5. **Routing**: Automatically route to appropriate S3 destination bucket
6. **Notification**: Send real-time updates via WebSocket and email notifications

### Message Queue Processing

The system uses RabbitMQ for reliable async processing:

- **Document Queue**: OCR and classification tasks
- **Email Queue**: Email attachment processing
- **Notification Queue**: Status updates and alerts
- **Outbox Pattern**: Ensures reliable message delivery

### Error Handling & Recovery

- **Retry Logic**: Automatic retry with exponential backoff
- **Dead Letter Queues**: Failed message handling
- **Manual Override**: Admin intervention for classification errors
- **Comprehensive Logging**: Detailed error tracking and debugging

## Monitoring & Analytics

### Dashboard Widgets

The application includes comprehensive monitoring through interactive dashboard widgets:

- **Status Distribution**: Document processing status breakdown (Pending, Processed, Failed)
- **Daily Volume**: Document ingestion trends over time
- **Processing Latency**: Performance metrics and bottleneck identification
- **Classification Accuracy**: AI model performance tracking
- **Override Rates**: Manual intervention frequency
- **Error Analysis**: Failure type breakdown and resolution tracking

### Performance Metrics

- **Processing Speed**: Average time from ingestion to routing
- **OCR Accuracy**: Text extraction quality metrics
- **Classification Confidence**: AI model certainty scores
- **System Throughput**: Documents processed per hour/day
- **Resource Utilization**: CPU, memory, and storage usage

## Deployment

### Production Build

```bash
# Build backend image
docker build -f backend/Dockerfile.prod -t insurance-backend .

# Build frontend image
docker build -f frontend/Dockerfile.prod -t insurance-frontend .

# Deploy with production compose
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Scale workers based on load
kubectl scale deployment ocr-worker --replicas=3
```

### Database Migrations

```bash
# Production migration
alembic upgrade head

# Backup before migration
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

## Testing

### Backend Testing

```bash
# Run unit tests
pytest backend/tests/

# Test with coverage
pytest --cov=app backend/tests/

# Integration tests
pytest backend/tests/integration/
```

### Frontend Testing

```bash
# Run Jest tests
npm test

# Run E2E tests
npm run test:e2e
```

### Load Testing

```bash
# Document processing load test
locust -f tests/load_test.py --host=http://localhost:8000
```

## Future Development

Insurance Document Management System is actively evolving with several exciting features planned:

### AI/ML Enhancements
- **Custom Model Training**: Fine-tune classification models on insurance-specific data
- **Document Similarity**: Find similar documents using vector embeddings
- **Automated Data Extraction**: Extract structured data from complex insurance forms
- **Confidence Scoring**: Improved classification confidence metrics

### Integration Capabilities
- **Insurance Core Systems**: Direct integration with policy management systems
- **Claims Processing**: Automated claim document routing and processing
- **Compliance Monitoring**: Automated regulatory compliance checking
- **Third-party OCR**: Integration with premium OCR services (AWS Textract, Azure Form Recognizer)

### User Experience
- **Mobile App**: React Native app for field document capture
- **Drag-and-Drop Interface**: Enhanced file upload experience
- **Preview Mode**: In-browser document preview before processing
- **Batch Operations**: Bulk document processing and management

### Enterprise Features
- **Multi-tenant Architecture**: Support for multiple insurance companies
- **Advanced Security**: Enhanced encryption and access controls
- **Audit Logging**: Comprehensive compliance and audit trails
- **SLA Monitoring**: Service level agreement tracking and reporting

### Analytics & Reporting
- **Business Intelligence**: Advanced reporting and analytics dashboard
- **Predictive Analytics**: Forecast document volumes and processing needs
- **ROI Tracking**: Measure automation benefits and cost savings
- **Custom Reports**: Configurable reporting for different stakeholders

## Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code style
- Use TypeScript for frontend development
- Add comprehensive tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

### Code Quality

```bash
# Python code formatting
black backend/app/
isort backend/app/

# Frontend code formatting
npm run lint
npm run format
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- **Issues**: GitHub Issues for bug reports and feature requests
- **Documentation**: Comprehensive API documentation at `/docs`
- **Email**: Contact the development team at suvodutta.isme@gmail.com

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [Next.js](https://nextjs.org/)
- AI processing powered by [OpenAI](https://openai.com/) and [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- Database powered by [PostgreSQL](https://postgresql.org/) and [SQLAlchemy](https://sqlalchemy.org/)
- Message queue by [RabbitMQ](https://rabbitmq.com/)
- UI components styled with [Tailwind CSS](https://tailwindcss.com/)
- Charts and visualizations by [Recharts](https://recharts.org/)
- File storage by [AWS S3](https://aws.amazon.com/s3/)

---

**Insurance Document Management System** - Revolutionizing insurance document processing with AI-powered automation.