from marshmallow import Schema, fields

class ConferenceSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    acronym = fields.Str()
    city = fields.Str()
    country = fields.Str()
    start_date = fields.Date()
    end_date = fields.Date()
    description = fields.Str()
    organizers = fields.Str()
    location = fields.Str()
    featured_papers = fields.List(fields.Str(), dump_only=True) # Keep for backward compat if needed, but papers is better
    papers = fields.List(fields.Nested(lambda: PaperSchema(only=("title", "authors"))), dump_only=True)
    featured_workshops = fields.Str()
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class PaperSchema(Schema):
    """Schema for paper with title and authors"""
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    authors = fields.List(fields.Nested(lambda: AuthorSchema(only=("name", "h_index", "affiliation"))), dump_only=True)

class AuthorSchema(Schema):
    """Schema for author with h-index information"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    h_index = fields.Int(dump_only=True)
    semantic_scholar_id = fields.Str(dump_only=True)
    affiliation = fields.Str(dump_only=True)
    last_updated = fields.DateTime(dump_only=True)

class SubmissionSchema(Schema):
    name = fields.Str(required=True)
    organizers = fields.Str(required=True)
    location = fields.Str(required=True)
    papers = fields.List(fields.Nested(PaperSchema), required=True)  # List of papers with authors
    featured_workshops = fields.Str(required=True)

class AuthSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)

class SubmissionActionSchema(Schema):
    submission_id = fields.Int(required=True)

class PendingSubmissionUpdateSchema(Schema):
    """Schema for updating a pending submission"""
    payload = fields.Dict(required=True)  # The updated payload data

class ConferenceUpdateSchema(Schema):
    """Schema for updating a conference - all fields optional"""
    name = fields.Str()
    acronym = fields.Str()
    city = fields.Str()
    country = fields.Str()
    start_date = fields.Date()
    end_date = fields.Date()
    description = fields.Str()
    organizers = fields.Str()
    location = fields.Str()
    featured_workshops = fields.Str()
    status = fields.Str()
    website = fields.Str()
    latitude = fields.Float()
    longitude = fields.Float()

class ConferenceQuerySchema(Schema):
    q = fields.Str()
    country = fields.Str()
    sort_by = fields.Str()
    page = fields.Int()
    per_page = fields.Int()


