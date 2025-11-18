from app.extensions import ma
from app.models import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    name = ma.String(required=True)
    email = ma.String(required=True)
    phone = ma.String(required=True)
    salary = ma.Float(required=True)

    class Meta:
        model = Mechanic
        load_instance = False


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
