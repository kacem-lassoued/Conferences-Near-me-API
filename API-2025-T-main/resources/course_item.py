from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import CourseItemModel
from schemas import Course_ItemSchema, Course_ItemUpdateSchema
from decorators import admin_or_chef_required

blp = Blueprint("Course_Items", __name__, description="Operations on course_items")


@blp.route("/course_item/<string:course_item_id>")
class Course_Item(MethodView):
    @admin_or_chef_required  # GET allowed for students, modifications for admin/chef
    @blp.response(200, Course_ItemSchema)
    def get(self, course_item_id):
        course_item = CourseItemModel.query.get_or_404(course_item_id)
        return course_item
    
    @admin_or_chef_required
    def delete(self, course_item_id):
        course_item = CourseItemModel.query.get_or_404(course_item_id)
        db.session.delete(course_item)
        db.session.commit()
        return {"message": "Course_item deleted."}

    @admin_or_chef_required
    @blp.arguments(Course_ItemUpdateSchema)
    @blp.response(200, Course_ItemSchema)
    def put(self, course_item_data, course_item_id):
        course_item = CourseItemModel.query.get_or_404(course_item_id)
        
        course_item.name = course_item_data.get("name", course_item.name)
        course_item.type = course_item_data.get("type", course_item.type)
        
        db.session.commit()
        return course_item


@blp.route("/course_item")
class Course_ItemList(MethodView):
    @admin_or_chef_required  # GET allowed for students, modifications for admin/chef
    @blp.response(200, Course_ItemSchema(many=True))
    def get(self):
        return CourseItemModel.query.all()
    
    @admin_or_chef_required
    @blp.arguments(Course_ItemSchema)
    @blp.response(201, Course_ItemSchema)
    def post(self, course_item_data):
        # Check if course_item already exists
        existing = CourseItemModel.query.filter_by(
            name=course_item_data["name"],
            specialization_id=course_item_data["specialization_id"]
        ).first()
        
        if existing:
            abort(400, message="Course_Item already exists.")

        course_item = CourseItemModel(**course_item_data)
        
        try:
            db.session.add(course_item)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while inserting the course_item.")
        
        return course_item