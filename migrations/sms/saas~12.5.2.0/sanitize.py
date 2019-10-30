#!/usr/bin/env python3
from odoo.tools import mute_logger
from odoo.addons.phone_validation.tools.phone_validation import phone_format


@mute_logger("odoo.addons.phone_validation.tools.phone_validation")
def sanitize(pid, number, country_code, phone_code):
    return (
        phone_format(number, country_code, phone_code, force_format="E164", raise_exception=False),
        pid,
    )
