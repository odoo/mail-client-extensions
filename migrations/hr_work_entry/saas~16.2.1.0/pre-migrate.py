# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{hr_payroll_attendance,hr_work_entry}.overtime_work_entry_type"))
