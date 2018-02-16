# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'sale.report_sale_order', 'sale.action_report_saleorder')

    eb = util.expand_braces
    util.rename_field(cr, 'sale.config.settings', *eb('{default_,}use_sale_note'))
    util.rename_field(cr, 'sale.config.settings',
                      'deposit_product_id_setting', 'default_deposit_product_id')
    util.rename_field(cr, 'sale.config.settings', *eb('module_sale_{contract,subscription}'))

    cr.execute("""
        UPDATE ir_config_parameter
           SET key='sale.use_sale_note'
         WHERE key='sale.default_use_sale_note'
    """)

    mapping = {
        'sale_pricelist_setting': 'sale_pricelist_setting',
        'deposit_product_id_setting': 'default_deposit_product_id',
        'auto_done_setting': 'auto_done_setting',
        'sale_show_tax': 'sale_show_tax',
    }

    imp = util.import_script('base/10.saas~17.1.3/default_to_icp.py')
    for f, k in mapping.items():
        imp.default_to_icp(cr, 'sale.config.settings', f, 'sale.' + k)
