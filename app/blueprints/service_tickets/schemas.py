from app.extensions import ma
from app.models import ServiceTicket
from marshmallow.validate import Length


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    VIN = ma.String(required=True, validate=Length(equal=17))
    service_date = ma.Date(required=True)
    service_desc = ma.String(required=True)

    class Meta:
        model = ServiceTicket
        load_instance = False
        include_fk = True


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
