# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_contract_salary.mail_template_send_offer", util.update_record_from_xml)
    util.if_unchanged(cr, "hr_contract_salary.mail_template_send_offer_applicant", util.update_record_from_xml)
