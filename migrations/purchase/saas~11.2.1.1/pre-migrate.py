# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'purchase.mail_template_data_notification_email_purchase_order')
    util.remove_field(cr, 'res.config.settings', 'group_analytic_account_for_purchases')
    util.remove_record(cr, 'purchase.group_analytic_accounting')
    util.remove_view(cr, 'purchase.res_config_settings_view_form_account')
