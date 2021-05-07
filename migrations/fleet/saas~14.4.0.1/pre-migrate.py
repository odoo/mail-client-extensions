# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_html(cr, "fleet.vehicle", "description")
    util.convert_field_to_html(cr, "fleet.vehicle.log.contract", "notes")
