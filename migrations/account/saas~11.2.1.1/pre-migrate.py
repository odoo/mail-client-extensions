# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.remove_record(cr, 'account.mail_template_data_notification_email_account_invoice')

    cr.execute("UPDATE account_tax SET type_tax_use='adjustment' WHERE tax_adjustment=true")
    cr.execute("UPDATE account_tax_template SET type_tax_use='adjustment' WHERE tax_adjustment=true")
    util.remove_field(cr, 'account.tax', 'tax_adjustment')
    util.remove_field(cr, 'account.tax.template', 'tax_adjustment')

    util.rename_field(cr, 'res.config.settings', *eb('module_{l10n_us,account}_check_printing'))

    util.remove_record(cr, 'account.analytic_line_reporting_pivot')
    util.remove_record(cr, 'account.menu_action_analytic_lines_reporting')
