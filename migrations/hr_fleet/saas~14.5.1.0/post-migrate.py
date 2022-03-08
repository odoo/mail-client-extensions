# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "fleet.fleet_rule_odometer_visibility_user", from_module="hr_fleet")
