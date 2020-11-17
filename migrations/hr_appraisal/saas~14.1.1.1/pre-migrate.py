# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "hr_appraisal.mail_template_appraisal_confirm_employee", noupdate=True)
    util.force_noupdate(cr, "hr_appraisal.mail_template_appraisal_confirm_manager", noupdate=True)
    util.force_noupdate(cr, "hr_appraisal.mail_template_appraisal_request", noupdate=True)
    util.force_noupdate(cr, "hr_appraisal.mail_template_appraisal_request_from_employee", noupdate=True)
