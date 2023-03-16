# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Explicit removal of demo records to avoid contract conflicts
    if not util.module_installed(cr, "hr_work_entry_contract_planning"):
        util.delete_unused(cr, "planning_contract.hr_contract_ngh")

    if not util.module_installed(cr, "hr_work_entry_contract_attendance"):
        util.delete_unused(cr, "planning_contract.hr_contract_hne")
