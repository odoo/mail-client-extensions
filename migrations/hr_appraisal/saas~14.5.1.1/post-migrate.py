# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr,
        "hr_appraisal.mail_template_appraisal_confirm",
        util.update_record_from_xml,
        reset_translations={"subject", "body_html"},
    )
    util.if_unchanged(
        cr,
        "hr_appraisal.mail_template_appraisal_request",
        util.update_record_from_xml,
        reset_translations={"body_html"},
    )
    util.if_unchanged(
        cr,
        "hr_appraisal.mail_template_appraisal_request_from_employee",
        util.update_record_from_xml,
        reset_translations={"subject", "body_html"},
    )
