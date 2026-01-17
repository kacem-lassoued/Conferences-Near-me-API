# Detailed Entity-Relationship Diagram

## Overview

This PlantUML diagram provides a comprehensive Entity-Relationship (ER) representation of the Conference Discovery Platform database schema. It includes all entities, attributes, relationships, and constraints in a professional format suitable for academic documentation.

## Diagram Contents

### Entities (Tables)

1. **conferences** - Main conference information
2. **conference_editions** - Yearly editions of conferences
3. **rankings** - Conference rankings from various systems
4. **themes** - Research themes/categories
5. **papers** - Academic papers presented at conferences
6. **authors** - Paper authors with research metrics
7. **pending_submissions** - User-submitted conference data awaiting approval

### Junction Tables (Many-to-Many Relationships)

1. **conference_themes** - Links conferences to research themes
2. **paper_authors** - Links papers to their authors

## Attribute Details

### Notation Used

- **Bold text**: Primary key attributes
- *Italic text*: Foreign key attributes
- `<<Tags>>`: Special constraints and metadata
- `VARCHAR(n)`: String type with max length
- `TEXT`: Unlimited text
- `JSON`: JSON data structure
- `FLOAT`: Floating-point numbers
- `INTEGER`: Whole numbers
- `DATETIME`: Date and time

### Key Constraints

- **NOT NULL**: Required fields
- **UNIQUE**: Unique value constraints
- **INDEX**: Database performance indexes
- **DEFAULT value**: Automatic default values
- **CHECK (condition)**: Business rule validations
- **FOREIGN KEY**: Referential integrity constraints

## Relationships

### Cardinalities

- `||--o{`: One-to-many (1:N)
- `}o--o{`: Many-to-many (M:N)
- `}o--||`: Many-to-one (N:1)

### Relationship Types

1. **Conference → Editions**: One conference can have multiple yearly editions
2. **Conference → Rankings**: One conference can have multiple ranking sources
3. **Conference → Papers**: One conference contains multiple papers
4. **Theme → Theme**: Hierarchical parent-child theme relationships
5. **Conference ↔ Theme**: Many-to-many through conference_themes
6. **Paper ↔ Author**: Many-to-many through paper_authors

## Business Rules

The diagram enforces several business rules through constraints:

- Conference end dates must be after start dates
- Conference-year combinations must be unique
- Status fields limited to valid enumerations
- H-index values must be non-negative
- Submission types and statuses are validated

## How to Use in Draw.io

1. **Import to Draw.io**:
   - Open [diagrams.net](https://diagrams.net)
   - File → Import → PlantUML...
   - Copy and paste the entire `.puml` file content

2. **Alternative Method**:
   - Visit [plantuml.com](https://plantuml.com)
   - Paste the code and generate PNG/SVG
   - Import the image into Draw.io for further editing

3. **Customization**:
   - Modify colors, fonts, and layout in Draw.io
   - Add additional annotations or callouts
   - Export to PDF, PNG, or other formats

## Database Implementation Notes

- **PostgreSQL**: Primary production database
- **SQLite**: Development and testing database
- **Indexes**: Applied to frequently queried columns
- **JSON Support**: Used for flexible metadata storage
- **Cascade Deletes**: Maintain referential integrity
- **UTF-8 Encoding**: Support for international characters

## Integration with Technical Report

This ER diagram corresponds to **Section 7: Domain Model & Data Design** in the technical report, providing visual representation of:

- Core domain entities and their attributes
- Database schema design decisions
- Relationship mappings between domain models and tables
- Normalization choices and indexing strategies
- Data integrity constraints and enforcement

## Legend Reference

| Symbol | Meaning |
|--------|---------|
| **bold** | Primary Key |
| *italic* | Foreign Key |
| `<<PK>>` | Primary Key |
| `<<FK>>` | Foreign Key |
| `<<NOT NULL>>` | Required Field |
| `<<INDEX>>` | Database Index |
| `<<UNIQUE>>` | Unique Constraint |
| `<<AUTO_INCREMENT>>` | Auto-generated ID |
| `<<DEFAULT value>>` | Default Value |
| `CHECK (condition)` | Check Constraint |

This diagram serves as both a technical specification and educational tool for understanding the complex relationships in an academic conference management system.