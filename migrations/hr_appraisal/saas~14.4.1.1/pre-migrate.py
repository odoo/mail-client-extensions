# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "request_appraisal", "lang", "varchar")
    # refresh templates to update some wrongly-defined fields, only if not customized
    util.if_unchanged(cr, "hr_appraisal.mail_template_appraisal_confirm_employee", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_appraisal.mail_template_appraisal_confirm_manager", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_appraisal.mail_template_appraisal_request", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_appraisal.mail_template_appraisal_request_from_employee", util.update_record_from_xml)
    util.convert_field_to_html(cr, "hr.appraisal.goal", "description")
