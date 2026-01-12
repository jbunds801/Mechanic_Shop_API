from marshmallow import validate
from app.extensions import ma
from app.models import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Mechanic
        load_instance = False
        include_fk = True
        fields = ("id", "name", "email", "phone", "salary", "is_admin")


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)


class LoginSchema(ma.Schema):
    email = ma.String(required=True)
    password = ma.String(required=True)


login_schema = LoginSchema()
