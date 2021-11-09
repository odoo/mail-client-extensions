# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr,
        "industry_fsm_report.mail_template_data_send_report",
        util.update_record_from_xml,
        reset_translations={"subject", "report_name", "body_html"},
    )
