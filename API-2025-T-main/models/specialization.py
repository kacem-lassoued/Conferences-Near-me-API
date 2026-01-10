from db import db
import uuid

class SpecializationModel(db.Model):
    __tablename__ = "specializations"

    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    name = db.Column(db.String(80), unique=True, nullable=False)

    course_items = db.relationship(
        "CourseItemModel",
        back_populates="specialization",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )