# Conference Classification Feature

## Overview

Conference classification has been implemented to automatically categorize conferences based on their research focus. The classification occurs during the data enrichment phase when a conference submission is received at the `/submissions` endpoint.

## How It Works

### 1. **Automatic Classification During Submission**

When a new conference is submitted via the `/submissions` endpoint:

```bash
POST /submissions
{
  "name": "NeurIPS 2024",
  "organizers": "...",
  "location": "...",
  "papers": [
    {"title": "Deep Learning Methods", "authors": ["Author One"]},
    {"title": "Neural Network Optimization", "authors": ["Author Two"]}
  ]
}
```

The system automatically:
- Analyzes the conference name
- Analyzes all paper titles
- Classifies the conference into a primary field
- Identifies related secondary fields
- Calculates a confidence score (0-1)

### 2. **Classification Storage**

The classification data is stored in the pending submission payload with this structure:

```json
{
  "primary": "Machine Learning",
  "secondary": ["Computer Vision", "Natural Language Processing"],
  "confidence": 0.87,
  "reasoning": "Classified based on keyword analysis of conference name and paper titles..."
}
```

### 3. **Persistence to Database**

When an admin approves a pending submission via `/admin/approve`, the classification is persisted to the Conference database table in the `classification` column.

## Supported Conference Fields

The classification system recognizes the following research fields:

- **Machine Learning** - ML, deep learning, neural networks, AI, algorithms
- **Natural Language Processing** - NLP, language models, text processing
- **Computer Vision** - Image recognition, object detection, video analysis
- **Robotics** - Robot control, autonomous systems, navigation
- **Human-Computer Interaction** - UI/UX, user studies, interaction design
- **Software Engineering** - Development practices, testing, architecture
- **Security** - Cryptography, privacy, authentication, attacks
- **Database Systems** - SQL, queries, data management
- **Distributed Systems** - Concurrency, consensus, distributed computing
- **Web Technology** - Web frameworks, APIs, web services
- **Bioinformatics** - Genetics, protein analysis, computational biology
- **Data Science** - Analytics, data mining, visualization, statistics
- **Theory** - Computational complexity, formal methods, algorithms

## API Response Format

### Submit Conference (POST /submissions)

Response includes classification information:

```json
{
  "submission_id": 123,
  "status": "pending",
  "message": "Conference submission received and will be reviewed",
  "enrichment_summary": {
    "total_papers": 5,
    "total_authors": 15,
    "successfully_enriched": 12
  },
  "classification": {
    "primary": "Machine Learning",
    "secondary": ["Computer Vision", "Natural Language Processing"],
    "confidence": 0.87,
    "error": null
  }
}
```

### Get Conference (GET /conferences/<id>)

Response includes classification data:

```json
{
  "id": 1,
  "name": "NeurIPS 2024",
  "classification": {
    "primary": "Machine Learning",
    "secondary": ["Computer Vision"],
    "confidence": 0.87,
    "reasoning": "Classified based on keyword analysis..."
  },
  "...": "other conference fields"
}
```

### Update Conference (PUT /conferences/<id>)

Admins can manually update classification:

```bash
PUT /conferences/1
{
  "classification": {
    "primary": "Deep Learning",
    "secondary": ["Machine Learning", "Computer Vision"],
    "confidence": 0.95,
    "reasoning": "Manually updated by admin"
  }
}
```

## Database Schema

The `conferences` table now includes:

```sql
classification JSON NULL
```

This stores the classification object with fields:
- `primary` (string): Main research field
- `secondary` (array): Related fields
- `confidence` (float): 0-1 score
- `reasoning` (string): Explanation of classification

## Workflow

```
1. User submits conference via POST /submissions
   |
   v
2. Author enrichment (Semantic Scholar API)
   |
   v
3. CONFERENCE CLASSIFICATION (NEW)
   - Analyze conference name + paper titles
   - Determine primary field and secondary fields
   - Calculate confidence score
   |
   v
4. Store enriched data + classification in PendingSubmission
   |
   v
5. Admin reviews submission via GET /admin/pending
   - Sees classification alongside enriched data
   |
   v
6. Admin approves via POST /admin/approve
   |
   v
7. Conference created in database with classification
```

## Error Handling

If classification fails:
- Classification field in response will be `null`
- `classification_status.error` will contain the error message
- Submission continues normally (classification failure doesn't block submission)
- Admin can manually add/update classification after approval

## Example Workflow

### 1. Submit Conference

```bash
curl -X POST http://localhost:5000/submissions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ICML 2024",
    "organizers": "International Conference on Machine Learning",
    "location": "Vienna, Austria",
    "papers": [
      {
        "title": "Efficient Deep Learning Training Methods",
        "authors": ["John Doe", "Jane Smith"]
      },
      {
        "title": "Computer Vision Applications in Healthcare",
        "authors": ["Alice Johnson"]
      }
    ]
  }'
```

### 2. Response (with Classification)

```json
{
  "submission_id": 5,
  "status": "pending",
  "classification": {
    "primary": "Machine Learning",
    "secondary": ["Computer Vision"],
    "confidence": 0.92,
    "error": null
  }
}
```

### 3. Admin Reviews & Approves

```bash
curl -X POST http://localhost:5000/admin/approve \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"submission_id": 5}'
```

### 4. Conference Created (with Classification)

```json
{
  "id": 123,
  "name": "ICML 2024",
  "classification": {
    "primary": "Machine Learning",
    "secondary": ["Computer Vision"],
    "confidence": 0.92,
    "reasoning": "Classified based on keyword analysis..."
  }
}
```

## Testing

The implementation includes comprehensive classification logic that handles:
- Multiple paper titles for better accuracy
- Weighted keyword matching
- Confidence scoring based on match distribution
- Graceful degradation if no keywords match

Run tests with:
```bash
python test_classification.py
```

## Configuration

The classification fields and keywords can be customized by editing the `FIELD_KEYWORDS` dictionary in [services/scholar_service.py](services/scholar_service.py#L392).

Add new fields or keywords as needed for your use case.
