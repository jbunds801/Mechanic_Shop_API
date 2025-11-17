from app.extensions import ma
from app.models import ServiceTicket


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = False
        include_fk = True


service_tickets_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
