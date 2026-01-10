from marshmallow import Schema, fields

class Specialization_Schema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    course_items = fields.List(fields.Nested(lambda: Course_ItemSchema(exclude=("specialization",))), dump_only=True)

class Course_ItemSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    specialization_id = fields.Str(required=True, load_only=True)
    specialization = fields.Nested(Specialization_Schema(only=("id", "name")), dump_only=True)

class Course_ItemUpdateSchema(Schema):
    name = fields.Str()
    type = fields.Str()j"4