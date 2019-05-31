# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        update account_tax
        set name = concat(account_tax.name, 'child')
        from ir_model_data
        where ir_model_data.model = 'account.tax'
        and ir_model_data.res_id = account_tax.id
        and ir_model_data.name like '%l10n_ie_tax_pt8m'
        and ir_model_data.module = 'l10n_ie';
    """)