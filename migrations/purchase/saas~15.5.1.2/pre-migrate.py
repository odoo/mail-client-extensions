# -*- coding: utf-8 -*-
from odoo.upgrade import util

eb = util.expand_braces


def migrate(cr, version):
    util.rename_field(cr, "purchase.order", *eb("tax_totals{_json,}"))
