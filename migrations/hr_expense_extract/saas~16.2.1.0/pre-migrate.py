# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_expense_extract.hr_expense_extract_endpoint")

    iap_extract = util.import_script("iap_extract/saas~16.2.1.0/end-status_code.py")
    iap_extract.migrate_status_code(cr, "hr.expense")
