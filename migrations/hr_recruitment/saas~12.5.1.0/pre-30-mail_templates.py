# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for suffix in {"refuse", "interest", "congratulations"}:
        util.if_unchanged(
            cr,
            "hr_recruitment.email_template_data_applicant_" + suffix,
            util.update_record_from_xml,
        )
