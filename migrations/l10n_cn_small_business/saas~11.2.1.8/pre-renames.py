# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE ir_model_data
           SET name = 'l10n_cn_' || substr(name, 20)
         WHERE module = 'l10n_cn_small_business'
           AND model = 'account.account.template'
           AND name LIKE 'small\_business\_chart%'
    """)

    util.remove_record(cr, 'l10n_cn_small_business.tax_tag1')
    util.remove_record(cr, 'l10n_cn_small_business.tax_tag2')
    util.remove_record(cr, 'l10n_cn_small_business.vats_small_business')
    util.remove_record(cr, 'l10n_cn_small_business.vatp_small_business')
