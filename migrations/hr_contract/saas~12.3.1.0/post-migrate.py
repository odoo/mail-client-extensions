# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_contract.group_hr_contract_manager", False)
