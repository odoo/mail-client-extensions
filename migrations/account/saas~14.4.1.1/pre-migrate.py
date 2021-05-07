# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_html(cr, "account.move", "narration")
    util.convert_field_to_html(cr, "account.payment.term", "note")
    util.convert_field_to_html(cr, "account.fiscal.position", "note")
    util.convert_field_to_html(cr, "res.company", "invoice_terms")
