from authentication import User
from database.model.agent.contact import Contact
from database.model.agent.email import Email
from database.model.agent.organisation import Organisation
from database.model.agent.person import Person
from routers.resource_router import ResourceRouter

from sqlmodel import select


class ContactRouter(ResourceRouter):
    def __init__(self):
        super().__init__()
        # Ugly hack to avoid "field "organisation" not yet prepared so type is still a ForwardRef"
        # error. This is caused by the circular relationship between (contact, organisation),
        # and also between (contact, person). See https://github.com/tiangolo/fastapi/issues/5607.
        Person.__init_subclass__ = lambda: None
        Organisation.__init_subclass__ = lambda: None
        for model in (self.resource_class_create, self.resource_class_read):
            model.update_forward_refs(Person=Person, Organisation=Organisation)

    @property
    def version(self) -> int:
        return 1

    @property
    def resource_name(self) -> str:
        return "contact"

    @property
    def resource_name_plural(self) -> str:
        return "contacts"

    @property
    def resource_class(self) -> type[Contact]:
        return Contact

    @staticmethod
    def _verify_user_roles(
        session,
        contact: Contact,
        user: User | None,
    ):
        if not user:
            email_mask = "******"
            # This ensures that the API doesn't break in case the email mask exists in
            # in the DB
            email = session.exec(select(Email).where(Email.name == email_mask)).first()
            if not email:
                email = Email(name=email_mask)
                session.add(email)
            contact.email = [email] * len(contact.email)
        return contact

    def _retrieve_resource(self, session, identifier, user=None, platform=None):
        contact = super()._retrieve_resource(session, identifier, platform)
        return self._verify_user_roles(session, contact, user)

    def _retrieve_resources(self, session, pagination, user=None, platform=None):
        contacts = super()._retrieve_resources(session, pagination, user, platform)
        contacts = [self._verify_user_roles(session, contact, user) for contact in contacts]
        return contacts
