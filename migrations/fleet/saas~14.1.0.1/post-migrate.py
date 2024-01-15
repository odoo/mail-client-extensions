# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "fleet.fleet_rule_contract_visibility_user")
    util.update_record_from_xml(cr, "fleet.fleet_rule_service_visibility_user")
