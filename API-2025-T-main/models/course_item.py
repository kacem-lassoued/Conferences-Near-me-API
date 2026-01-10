from db import db
import uuid

class CourseItemModel(db.Model):
    __tablename__ = "course_items"

    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    name = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.String(50))

    specialization_id = db.Column(
        db.String(32),
        db.ForeignKey("specializations.id"),
        nullable=False
    )

    specialization = db.relationship(
        "SpecializationModel",
        back_populates="course_items",
        lazy="joined"
    )
