from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import SpecializationModel
from schemas import Specialization_Schema
from decorators import admin_required

blp = Blueprint("specializations", __name__, description="Operations on specializations")


@blp.route("/specialization/<string:specialization_id>")
class Specialization(MethodView):
    @admin_required  # GET allowed for students, modifications for admin only
    @blp.response(200, Specialization_Schema)
    def get(self, specialization_id):
        specialization = SpecializationModel.query.get_or_404(specialization_id)
        return specialization
    
    @admin_required
    def delete(self, specialization_id):
        specialization = SpecializationModel.query.get_or_404(specialization_id)
        db.session.delete(specialization)
        db.session.commit()
        return {"message": "Specialization deleted."}

    @admin_required
    @blp.arguments(Specialization_Schema)
    @blp.response(200, Specialization_Schema)
    def put(self, data, specialization_id):
        specialization = SpecializationModel.query.get_or_404(specialization_id)
        specialization.name = data["name"]
        db.session.commit()
        return specialization


@blp.route("/specialization")
class SpecializationList(MethodView):
    @admin_required  # GET allowed for students, modifications for admin only
    @blp.response(200, Specialization_Schema(many=True))
    def get(self):
        return SpecializationModel.query.all()

    @admin_required
    @blp.arguments(Specialization_Schema)
    @blp.response(201, Specialization_Schema)
    def post(self, data):
        existing = SpecializationModel.query.filter_by(name=data["name"]).first()
        if existing:
            abort(400, message="Specialization already exists.")

        specialization = SpecializationModel(name=data["name"])
        
        try:
            db.session.add(specialization)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            print(f"IntegrityError: {str(e)}")
            abort(400, message=f"Database integrity error: {str(e)}")
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"SQLAlchemyError: {str(e)}")
            abort(500, message=f"Database error: {str(e)}")
        except Exception as e:
            db.session.rollback()
            print(f"Unexpected error: {str(e)}")
            abort(500, message=f"An unexpected error occurred: {str(e)}")
        
        return specialization