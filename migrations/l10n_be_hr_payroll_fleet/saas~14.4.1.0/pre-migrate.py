# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_property(cr, "fleet.vehicle.model", "can_be_requested", "boolean", company_field="NULL")
