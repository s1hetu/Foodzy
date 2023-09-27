import re

from django.core.exceptions import ValidationError


def validate_ifsc_code(code):
    regex_ifsc_code = "^[A-Z]{4}0[A-Z0-9]{6}$"
    compile_regex = re.compile(regex_ifsc_code)

    if re.search(compile_regex, code):
        return code
    raise ValidationError("enter a valid IFSC code. e.g. ABCD0123456")