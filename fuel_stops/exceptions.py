from django.core.exceptions import ValidationError


class ORSException(ValidationError):
    pass
