from app.extensions import ma
from app.models import Customer


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    name = ma.String(required=True)
    phone = ma.String(required=True)

    class Meta:
        model = Customer
        load_instance = False
        fields = ("id", "name", "email", "phone")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
