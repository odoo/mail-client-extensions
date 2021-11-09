# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_recruitment.stage_job5")

    rt = dict(reset_translations={"subject", "body_html"})
    util.if_unchanged(cr, "hr_recruitment.email_template_data_applicant_refuse", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "hr_recruitment.email_template_data_applicant_interest", util.update_record_from_xml, **rt)
    util.if_unchanged(
        cr, "hr_recruitment.email_template_data_applicant_congratulations", util.update_record_from_xml, **rt
    )

    util.if_unchanged(
        cr,
        "hr_recruitment.digest_tip_hr_recruitment_0",
        util.update_record_from_xml,
        reset_translations={"tip_content"},
    )
