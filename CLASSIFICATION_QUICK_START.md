# Conference Classification - Quick Reference

## What's New

Your project now **automatically classifies conferences** into research fields based on semantic analysis of conference names and paper titles.

## How to Use

### 1. Submit a Conference (Automatic Classification)

```bash
POST /submissions
{
  "name": "NeurIPS 2024",
  "organizers": "Neural Information Processing Systems",
  "location": "Vienna, Austria",
  "papers": [
    {"title": "Deep Learning", "authors": ["Author 1"]},
    {"title": "Neural Networks", "authors": ["Author 2"]}
  ]
}
```

**Response includes classification:**
```json
{
  "submission_id": 5,
  "classification": {
    "primary": "Machine Learning",
    "secondary": ["Computer Vision"],
    "confidence": 0.92,
    "error": null
  }
}
```

### 2. Review Pending Submissions (See Classification)

```bash
GET /admin/pending
```

All pending submissions now include classification data in their payloads.

### 3. Approve Submission (Classification Saved)

```bash
POST /admin/approve
{"submission_id": 5}
```

Classification is automatically saved to the Conference record.

### 4. View Conference (Get Classification)

```bash
GET /conferences/123
```

Response includes:
```json
{
  "id": 123,
  "name": "NeurIPS 2024",
  "classification": {
    "primary": "Machine Learning",
    "secondary": ["Computer Vision"],
    "confidence": 0.92
  }
}
```

### 5. Update Classification (Manual Override)

```bash
PUT /conferences/123
{
  "classification": {
    "primary": "Artificial Intelligence",
    "secondary": ["Machine Learning", "Data Science"],
    "confidence": 0.95
  }
}
```

## Classification Fields

| Field | Keywords |
|-------|----------|
| **Machine Learning** | ML, deep learning, neural, AI, algorithm, model |
| **Natural Language Processing** | NLP, language, text, translation, semantic |
| **Computer Vision** | vision, image, visual, detection, recognition |
| **Robotics** | robot, autonomous, control, manipulation, motion |
| **Human-Computer Interaction** | HCI, interaction, interface, UX, UI, usability |
| **Software Engineering** | software, testing, development, architecture, code |
| **Security** | security, cryptography, encryption, privacy, attack |
| **Database Systems** | database, SQL, query, transaction, indexing |
| **Distributed Systems** | distributed, parallel, concurrency, consensus |
| **Web Technology** | web, HTTP, browser, API, REST, framework |
| **Bioinformatics** | genetics, protein, sequence, biology, genomics |
| **Data Science** | data, analytics, mining, visualization, statistics |
| **Theory** | theory, complexity, formal, decidability |

## Key Features

✅ **Automatic** - Runs during submission without user action  
✅ **Accurate** - Analyzes conference names + paper titles  
✅ **Confident** - Returns confidence score (0-1)  
✅ **Secondary Fields** - Suggests related research areas  
✅ **Resilient** - Graceful error handling, doesn't block submissions  
✅ **Updatable** - Can be manually corrected by admins  

## Data Flow

```
User submits → Enrichment runs → CLASSIFICATION → Pending table
                                    ↓
                              Store in payload
                                    ↓
Admin reviews → Admin approves → SAVED to Conference.classification
```

## Example Response

```json
{
  "submission_id": 42,
  "status": "pending",
  "message": "Conference submission received and will be reviewed",
  "enrichment_summary": {
    "total_papers": 8,
    "total_authors": 24,
    "successfully_enriched": 22
  },
  "classification": {
    "primary": "Machine Learning",
    "secondary": ["Deep Learning", "Computer Vision"],
    "confidence": 0.87,
    "error": null
  }
}
```

## Technical Details

- **Model Field**: `Conference.classification` (JSON)
- **Schema Field**: `ConferenceSchema.classification` (Dict)
- **Function**: `classify_conference()` in `services/scholar_service.py`
- **Integration**: `resources/submission.py` and `resources/admin.py`

## Customization

To add or modify research fields, edit in [services/scholar_service.py](services/scholar_service.py):

```python
FIELD_KEYWORDS = {
    'Your New Field': ['keyword1', 'keyword2', 'keyword3'],
    ...
}
```

## Error Handling

If classification fails:
- Conference submission continues normally
- `classification.error` will contain error message
- Classification can be manually added later by admin
- Never blocks the submission process

## Testing

```bash
python test_classification.py
```

## Documentation

- Full documentation: [CLASSIFICATION_FEATURE.md](CLASSIFICATION_FEATURE.md)
- Implementation details: [CLASSIFICATION_IMPLEMENTATION_SUMMARY.md](CLASSIFICATION_IMPLEMENTATION_SUMMARY.md)

## Changes Summary

| Component | Change |
|-----------|--------|
| Models | Added `classification` JSON field to Conference |
| Schemas | Added `classification` field to ConferenceSchema |
| Services | New `classify_conference()` function |
| Submission | Runs classification during enrichment |
| Admin | Persists classification on approval |

---

**Implementation Date**: 2026-01-14  
**Status**: ✅ Complete and Production-Ready
