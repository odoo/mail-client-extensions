# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(
        cr, *eb("hr_work_entry_holidays{,_enterprise}.payroll_leave_hr_work_entry_type_view_form_inherit")
    )
    util.rename_xmlid(cr, *eb("hr_work_entry_holidays{,_enterprise}.payroll_hr_work_entry_view_form_inherit_contract"))
    util.rename_xmlid(cr, *eb("hr_work_entry_holidays{,_enterprise}.payroll_hr_work_entry_view_form_inherit"))
    util.rename_xmlid(cr, *eb("hr_work_entry_contract{,_enterprise}.hr_leave_work_entry_action"))
    util.rename_xmlid(cr, *eb("hr_work_entry_contract{,_enterprise}.menu_work_entry_leave_to_approve"))
