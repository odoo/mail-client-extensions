# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_menus(cr, [util.ref(cr, "hr_appraisal.hr_appraisal_menu_employee")])
    util.rename_xmlid(
        cr, "hr_appraisal.mail_template_appraisal_confirm_employee", "hr_appraisal.mail_template_appraisal_confirm"
    )
    util.if_unchanged(cr, "hr_appraisal.mail_template_appraisal_confirm", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_appraisal.mail_template_appraisal_request", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_appraisal.mail_template_appraisal_request_from_employee", util.update_record_from_xml)
    util.remove_view(cr, "hr_appraisal.hr_job_view_form")
    util.remove_record(cr, "hr_appraisal.mail_template_appraisal_confirm_manager")
    util.remove_record(cr, "hr_appraisal.hr_appraisal_plan_comp_rule")
    util.update_record_from_xml(cr, "hr_appraisal.hr_appraisal_goal_all")
    util.update_record_from_xml(cr, "hr_appraisal.hr_appraisal_goal_own")
    util.update_record_from_xml(cr, "hr_appraisal.group_hr_appraisal_manager")
    util.update_record_from_xml(cr, "hr_appraisal.ir_cron_scheduler_appraisal")
