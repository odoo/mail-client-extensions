# -*- coding: utf-8 -*-
from odoo import models

try:
    from odoo.addons.stock.models import stock_warehouse  # noqa
except ImportError:
    from odoo.addons.stock import stock  # noqa


def migrate(cr, version):
    pass


class Warehouse(models.Model):
    _name = "stock.warehouse"
    _inherit = ["stock.warehouse"]
    _module = "stock"
    _match_uniq = True
