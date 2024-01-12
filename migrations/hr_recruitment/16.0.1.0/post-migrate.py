# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    rt = {"reset_translations": {"body_html"}}
    util.if_unchanged(
        cr, "hr_recruitment.email_template_data_applicant_congratulations", util.update_record_from_xml, **rt
    )
    util.if_unchanged(cr, "hr_recruitment.email_template_data_applicant_interest", util.update_record_from_xml, **rt)

    util.if_unchanged(cr, "hr_recruitment.hr_applicant_interviewer_rule", util.update_record_from_xml)
