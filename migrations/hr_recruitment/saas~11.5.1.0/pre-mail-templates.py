# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_recruitment.email_template_data_applicant_refuse", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_recruitment.email_template_data_applicant_interest", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_recruitment.email_template_data_applicant_congratulations", util.update_record_from_xml)

    util.remove_record(cr, "hr_recruitment.email_template_data_applicant_employee")
