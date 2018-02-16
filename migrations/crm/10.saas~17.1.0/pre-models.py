# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

eb = util.expand_braces

def migrate(cr, version):
    util.remove_field(cr, 'crm.lead', 'fax')

    util.remove_field(cr, 'sale.config.settings', 'generate_sales_team_alias')
    util.rename_field(cr, 'sale.config.settings', *eb('{default_,}generate_lead_from_alias'))
    cr.execute("""
        UPDATE ir_config_parameter
           SET key='crm.generate_lead_from_alias'
         WHERE key='sale_config_settings.default_generate_lead_from_alias'
    """)
