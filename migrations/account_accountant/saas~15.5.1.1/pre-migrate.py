# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    for field in {"in_invoice", "out_invoice", "payment", "misc_entry"}:
        util.remove_field(cr, "bank.rec.widget", f"reconciled_{field}_ids")
        util.remove_field(cr, "bank.rec.widget", f"reconciled_{field}_ids_count")
