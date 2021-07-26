# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.ref(cr, "documents_hr_payroll.documents_hr_documents_payslips"):
        util.update_record_from_xml(cr, "base.main_company", from_module="documents_hr_payroll")
