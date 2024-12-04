import contextlib

from odoo.tools import mute_logger

from odoo.addons.phone_validation.tools.phone_validation import phone_format


@mute_logger("odoo.addons.phone_validation.tools.phone_validation")
def sanitize(pid, number, country_code, phone_code):
    with contextlib.suppress(Exception):
        sanitized_number = phone_format(number, country_code, phone_code, force_format="E164", raise_exception=True)
        # We only return the sanitized number if it is valid
        return sanitized_number, True, pid
    return None, False, pid
