# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        INSERT INTO taxes_not_to_merge(tax_id)
        SELECT res_id
        FROM ir_model_data
        WHERE
        (name LIKE '%gstpst_bc_sale_en'
            OR name LIKE '%gstpst_mb_sale_en'
            OR name LIKE '%gstqst_sale_en'
            OR name LIKE '%gstpst_sk_sale_en'
            OR name LIKE '%gstpst_bc_purc_en'
            OR name LIKE '%gstpst_mb_purc_en'
            OR name LIKE '%gstqst_purc_en'
            OR name LIKE '%gstpst_sk_purc_en')
        AND model = 'account.tax'
        AND module = 'l10n_ca'
    """)