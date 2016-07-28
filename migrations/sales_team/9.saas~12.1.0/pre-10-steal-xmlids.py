# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    xids = util.splitlines("""
        menu_config_bank_accounts
        menu_localisation
        menu_country_partner
        menu_country_group
        menu_country_state_partner
        menu_base_partner
        menu_sale_config
        menu_config_address_book
        menu_partner_title_contact
        menu_sales
        menu_parner_form
        menu_partner_category_form

        group_sale_salesman
        group_sale_manager
        group_sale_salesman_all_leads
    """)
    for x in xids:
        util.rename_xmlid(cr, 'base.' + x, 'sales_team.' + x)
        util.force_noupdate(cr, 'sales_team.' + x, False)

    util.rename_xmlid(cr, 'base_setup.view_sale_config_settings', 'sales_team.view_sale_config_settings')
    util.rename_xmlid(cr, 'base_setup.action_sale_config', 'sales_team.action_sale_config')
