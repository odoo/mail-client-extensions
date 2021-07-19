# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_contract.hr_menu_contract_history_to_review")

    # demo data moved and renamed
    util.rename_xmlid(cr, "hr_payroll.hr_contract_admin", "hr_contract.hr_contract_admin_new")
