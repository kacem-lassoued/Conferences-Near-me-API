from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from datetime import datetime


class PaperSchema(Schema):
    """Schema for paper with title and authors"""
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=3, max=500))
    authors = fields.List(
        fields.Nested(lambda: AuthorSchema(only=("id", "name", "h_index", "affiliation"))), 
        dump_only=True
    )


class AuthorSchema(Schema):
    """Schema for author with h-index information"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    h_index = fields.Int(dump_only=True, allow_none=True)
    semantic_scholar_id = fields.Str(dump_only=True, allow_none=True)
    affiliation = fields.Str(allow_none=True, validate=validate.Length(max=300))
    last_updated = fields.DateTime(dump_only=True)
    citation_count = fields.Int(dump_only=True, allow_none=True)
    match_confidence = fields.Float(dump_only=True, allow_none=True)


class AuthorInputSchema(Schema):
    """Schema for author input (name only)"""
    name = fields.Str(required=True, validate=validate.Length(min=2, max=200))


class ConferenceSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    acronym = fields.Str(validate=validate.Length(max=20), allow_none=True)
    city = fields.Str(validate=validate.Length(max=100), allow_none=True)
    country = fields.Str(validate=validate.Length(max=100), allow_none=True)
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)
    description = fields.Str(validate=validate.Length(max=2000), allow_none=True)
    organizers = fields.Str(validate=validate.Length(max=500), allow_none=True)
    location = fields.Str(validate=validate.Length(max=500), allow_none=True)
    website = fields.Url(allow_none=True)
    papers = fields.List(
        fields.Nested(lambda: PaperSchema(only=("title", "authors"))), 
        dump_only=True
    )
    featured_workshops = fields.Str(validate=validate.Length(max=500), allow_none=True)
    status = fields.Str(validate=validate.OneOf(['scheduled', 'cancelled', 'postponed']), dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    classification = fields.Dict(dump_only=True, allow_none=True)
    
    @validates('end_date')
    def validate_end_date(self, value):
        """Ensure end_date is not before start_date"""
        if value and self.context.get('start_date') and value < self.context.get('start_date'):
            raise ValidationError("End date must be after start date")


class PaperInputSchema(Schema):
    """Schema for paper input with author names"""
    title = fields.Str(required=True, validate=validate.Length(min=3, max=500))
    authors = fields.List(
        fields.Str(validate=validate.Length(min=2, max=200)),
        required=True,
        validate=validate.Length(min=1, max=50)
    )


class SubmissionSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    organizers = fields.Str(required=True, validate=validate.Length(min=2, max=500))
    location = fields.Str(required=True, validate=validate.Length(min=3, max=500))
    papers = fields.List(
        fields.Nested(PaperInputSchema),
        required=True,
        validate=validate.Length(min=1, max=50)
    )
    featured_workshops = fields.Str(allow_none=True, validate=validate.Length(max=500))
    
    @validates_schema
    def validate_data(self, data, **kwargs):
        """Cross-field validation"""
        if not data.get('papers') or len(data['papers']) == 0:
            raise ValidationError("At least one paper is required")


class AuthSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=100))


class SubmissionActionSchema(Schema):
    submission_id = fields.Int(required=True, validate=validate.Range(min=1))


class PendingSubmissionUpdateSchema(Schema):
    """Schema for updating a pending submission"""
    payload = fields.Dict(required=True)


class ConferenceUpdateSchema(Schema):
    """Schema for updating a conference - all fields optional"""
    name = fields.Str(validate=validate.Length(min=3, max=200), allow_none=True)
    acronym = fields.Str(validate=validate.Length(max=20), allow_none=True)
    city = fields.Str(validate=validate.Length(max=100), allow_none=True)
    country = fields.Str(validate=validate.Length(max=100), allow_none=True)
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)
    description = fields.Str(validate=validate.Length(max=2000), allow_none=True)
    organizers = fields.Str(validate=validate.Length(max=500), allow_none=True)
    location = fields.Str(validate=validate.Length(max=500), allow_none=True)
    featured_workshops = fields.Str(validate=validate.Length(max=500), allow_none=True)
    status = fields.Str(validate=validate.OneOf(['scheduled', 'cancelled', 'postponed']), allow_none=True)
    website = fields.Url(allow_none=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    classification = fields.Dict(allow_none=True)


class ConferenceQuerySchema(Schema):
    q = fields.Str(allow_none=True, validate=validate.Length(max=200))
    country = fields.Str(allow_none=True, validate=validate.Length(max=100))
    sort_by = fields.Str(
        validate=validate.OneOf(['name', 'created_at', 'start_date']),
        allow_none=True
    )
    page = fields.Int(validate=validate.Range(min=1), allow_none=True)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), allow_none=True)


