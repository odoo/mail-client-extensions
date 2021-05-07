# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_html(cr, "maintenance.equipment", "note")
    util.convert_field_to_html(cr, "maintenance.equipment.category", "note")
    util.convert_field_to_html(cr, "maintenance.request", "description")
