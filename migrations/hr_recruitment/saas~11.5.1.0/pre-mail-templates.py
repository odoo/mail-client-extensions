# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record_if_unchanged(cr, "hr_recruitment.email_template_data_applicant_refuse")
    util.remove_record_if_unchanged(cr, "hr_recruitment.email_template_data_applicant_interest")
    util.remove_record_if_unchanged(cr, "hr_recruitment.email_template_data_applicant_congratulations")

    util.remove_record(cr, "hr_recruitment.email_template_data_applicant_employee")
