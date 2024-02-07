# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.ref(cr, "stock.warehouse0"):
        util.ensure_xmlid_match_record(cr, "stock.warehouse0", "stock.warehouse", {"code": "WH"})
