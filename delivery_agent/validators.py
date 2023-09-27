import re

from django.core.exceptions import ValidationError


# Function to validate Indian driving license number.
def validate_license_no(license_no):
    # Regex to check valid
    # 16 characters long (including space or hyphen (-)
    # Indian driving license number
    regex = ("^(([A-Z]{2}[0-9]{2})" +
             "( )|([A-Z]{2}-[0-9]" +
             "{2}))((19|20)[0-9]" +
             "[0-9])[0-9]{7}$")

    # Compile the ReGex
    p = re.compile(regex)

    # Return if the string
    # matched the ReGex
    if not license_no or not re.search(p, license_no):
        raise ValidationError("Enter a valid licence no ex.(HR-0619850034761)")
    return license_no


def validate_pancard_no(pancard_no):
    # Regex to check valid
    # PAN Card number
    # It should be 10 characters long.
    regex = "[A-Z]{5}[0-9]{4}[A-Z]{1}"

    # Compile the ReGex
    p = re.compile(regex)

    # Return if the PAN Card number
    # matched the ReGex
    if not pancard_no or not re.search(p, pancard_no) or len(pancard_no) != 10:
        raise ValidationError("Enter a valid pancard no\nEx.(BNZAA2318J)")
    return pancard_no


def validate_rating(value):
    """
    Validate given rating
    """
    if 0.5 <= value <= 5:
        return value
    raise ValidationError("Rating should be between half star and 5 star")
