# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Explicit removal of demo records to avoid contract conflicts
    util.remove_record(cr, "planning_contract.hr_contract_ngh")
    util.remove_record(cr, "planning_contract.hr_contract_hne")
