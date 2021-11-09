# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr,
        "industry_fsm.mail_template_data_intervention_details",
        util.update_record_from_xml,
        reset_translations={"subject", "body_html"},
    )
