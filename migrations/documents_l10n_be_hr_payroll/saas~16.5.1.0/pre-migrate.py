# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "documents_l10n_be_hr_payroll.mail_template_individual_account")
    util.remove_record(cr, "documents_l10n_be_hr_payroll.mail_template_281_10")
    util.remove_record(cr, "documents_l10n_be_hr_payroll.mail_template_281_45")
