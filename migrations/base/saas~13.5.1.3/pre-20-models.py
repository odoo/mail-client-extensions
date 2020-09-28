# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.country", "image")

    util.create_column(cr, "res_country", "zip_required", "boolean", default=True)
    util.create_column(cr, "res_country", "state_required", "boolean", default=False)

    cr.execute("DELETE FROM res_currency_rate WHERE currency_id IS NULL")
