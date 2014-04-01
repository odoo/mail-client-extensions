# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    # m2o function fields (including related) now have foreign keys...

    m2o = [
        # base
        ('res_partner', 'commercial_partner_id', 'res_partner'),

        # account
        ('account_move', 'partner_id', 'res_partner'),
        ('account_invoice_line', 'partner_id', 'res_partner'),
        ('account_invoice', 'commercial_partner_id', 'res_partner'),

        # analytic
        ('account_analytic_account', 'currency_id', 'res_currency'),

        # hr_holidays
        ('hr_holidays', 'user_id', 'res_users'),
        ('hr_holidays', 'department_id', 'hr_department'),

        # hr_timesheet_sheet
        ('hr_analytic_timesheet', 'sheet_id', 'hr_timesheet_sheet_sheet'),
        ('hr_analytic_timesheet', 'partner_id', 'res_partner'),

        # mass_mailing
        ('mail_mail_statistics', 'mass_mailing_campaign_id', 'mail_mass_mailing_campaign'),

        # point_of_sale
        ('pos_session', 'cash_register_id', 'account_bank_statement'),
        ('pos_session', 'cash_journal_id', 'account_journal'),

        # project_mrp
        ('project_task', 'sale_line_id', 'sale_order_line'),

        # purchase
        ('purchase_order_line', 'partner_id', 'res_partner'),

        # sale
        ('sale_order_line', 'salesman_id', 'res_users'),
        ('sale_order_line', 'order_partner_id', 'res_partner'),
    ]

    for each in m2o:
        util.ensure_m2o_func_field_data(cr, *each)
