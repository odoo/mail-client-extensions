# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.country", "image")

    cr.execute("DELETE FROM res_currency_rate WHERE currency_id IS NULL")
