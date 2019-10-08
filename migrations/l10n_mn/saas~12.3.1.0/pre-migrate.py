# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.table_exists(cr, "tax_accounts_v12_bckp"):
        return

    cr.execute("""
        INSERT INTO v12_financial_tags_registry(tag_id)
        SELECT res_id
        FROM ir_model_data
        JOIN account_account_tag
        ON account_account_tag.id = ir_model_data.res_id
        WHERE ir_model_data.module = 'l10n_mn'
            AND ir_model_data.model = 'account.account.tag'
            AND account_account_tag.applicability = 'taxes'
    """)
