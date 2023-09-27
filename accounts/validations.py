import re

from django.contrib.auth.password_validation import validate_password as default_validate_password
from django.core.exceptions import ValidationError


def validate_password(*args, **kwargs):
    default_validate_password(*args, **kwargs)

    password = args[0]

    if not re.findall('[A-Z]', password):
        raise ValidationError(
            "The password must contain at least 1 uppercase letter, A-Z.",
            code='password_no_upper',
        )

    if not re.findall('[a-z]', password):
        raise ValidationError(
            "The password must contain at least 1 lowercase letter, a-z.",
            code='password_no_lower',
        )
    if not re.findall("""(?=.*?[0-9])""", password):
        raise ValidationError(
            "The password must contain at least 1 digit.",
            code='password_no_lower',
        )

    if not re.findall("""^(?=.*?[!@#\][:()"`;+\-'|_?,.</\\>=$%}{^&*~]).{8,}$""", password):
        raise ValidationError(
            "The password must contain at least 1 special character.",
            code='password_no_lower',
        )

# def validate_pin_code(pin_code):
#     if not re.findall("""^[1-9][0-9]{5}$""", pin_code):
#         raise ValidationError(
#             "The pin code must contain at least 6 digits long.",
#             code='pincode_not_valid',
#         )
