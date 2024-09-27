# -*- coding: utf-8 -*-
from odoo import models

try:
    from odoo.addons.calendar.models import calendar  # noqa
except Exception:
    from odoo.addons.calendar.models import calendar_event_type  # noqa


def migrate(cr, version):
    pass


class Tax(models.Model):
    _name = "calendar.event.type"
    _inherit = ["calendar.event.type"]
    _module = "calendar"
    _match_uniq = True
