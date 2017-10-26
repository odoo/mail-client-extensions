# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_financial_html_report', 'hierarchy_option', 'boolean')
    util.create_column(cr, 'account_financial_html_report', 'generated_menu_id', 'int4')
    cr.execute("UPDATE account_financial_html_report SET hierarchy_option=true")
    cr.execute("""
        UPDATE account_financial_html_report r
           SET generated_menu_id = x.res_id
          FROM ir_model_data x
         WHERE x.model = 'ir.ui.menu'
           AND x.name = CONCAT('account_financial_html_report_menu_', r.id)
    """)
    util.remove_column(cr, 'account_financial_html_report', 'parent_id')  # field is now a related
