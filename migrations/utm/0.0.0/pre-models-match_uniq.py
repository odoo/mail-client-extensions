# -*- coding: utf-8 -*-
from odoo import models

try:
    from odoo.addons.utm.models import utm_source  # noqa
except ImportError:
    from odoo.addons.utm.models import utm  # noqa


def migrate(cr, version):
    pass


class UtmSource(models.Model):
    _inherit = "utm.source"
    _module = "utm"
    _match_uniq = True
