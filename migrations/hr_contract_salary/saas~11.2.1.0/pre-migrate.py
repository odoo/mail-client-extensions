# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'hr_contract_salary.mail_template_data_notification_email_send_offer')
