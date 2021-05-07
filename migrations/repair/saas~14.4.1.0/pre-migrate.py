# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_html(cr, "repair.order", "internal_notes")
    util.convert_field_to_html(cr, "repair.order", "quotation_notes")
