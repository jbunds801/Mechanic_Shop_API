from app.extensions import ma
from app.models import ServiceTicket
from app.blueprints.mechanics.schemas import MechanicSchema
from app.blueprints.customers.schemas import CustomerSchema
from marshmallow.validate import Length
from marshmallow import fields, validates_schema, ValidationError


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    VIN = ma.String(required=True, validate=Length(equal=17))
    created_at = fields.DateTime(dump_only=True)
    service_date = ma.Date(required=True)
    service_desc = ma.String(required=True)
    is_open = fields.Boolean(required=False, load_default=True)
    mechanics = fields.List(fields.Nested(MechanicSchema, only=["id", "name"]))
    customer = fields.Nested(CustomerSchema, only=["name"])

    class Meta:
        model = ServiceTicket
        load_instance = False
        include_fk = True
        fields = (
            "id",
            "customer_id",
            "customer",
            "VIN",
            "created_at",
            "service_date",
            "service_desc",
            "is_open",
            "mechanics",
        )


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)


class EditServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=False, load_default=list)
    remove_mechanic_ids = fields.List(fields.Int(), required=False, load_default=list)

    @validates_schema
    def validate_at_least_one_operation(self, data, **kwargs):
        add_ids = data.get("add_mechanic_ids", [])
        remove_ids = data.get("remove_mechanic_ids", [])

        if len(add_ids) == 0 and len(remove_ids) == 0:
            raise ValidationError(
                "Provide at least one mechanic id in add_mechanic_ids or remove_mechanic_ids."
            )

    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")


edit_service_ticket_schema = EditServiceTicketSchema()
