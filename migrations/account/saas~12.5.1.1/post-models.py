# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Deleted in post-12.5 because used in post-12.4
    util.remove_field(cr, "account.journal", "post_at_bank_rec")
    account_account_type = {
        "asset": [
            util.ref(cr, "account.data_account_type_receivable"),
            util.ref(cr, "account.data_account_type_liquidity"),
            util.ref(cr, "account.data_account_type_current_assets"),
            util.ref(cr, "account.data_account_type_non_current_assets"),
            util.ref(cr, "account.data_account_type_prepayments"),
            util.ref(cr, "account.data_account_type_fixed_assets"),
        ],
        "liability": [
            util.ref(cr, "account.data_account_type_payable"),
            util.ref(cr, "account.data_account_type_credit_card"),
            util.ref(cr, "account.data_account_type_current_liabilities"),
            util.ref(cr, "account.data_account_type_non_current_liabilities"),
        ],
        "equity": [util.ref(cr, "account.data_account_type_equity"), util.ref(cr, "account.data_unaffected_earnings"),],
        "income": [
            util.ref(cr, "account.data_account_type_revenue"),
            util.ref(cr, "account.data_account_type_other_income"),
        ],
        "expense": [
            util.ref(cr, "account.data_account_type_expenses"),
            util.ref(cr, "account.data_account_type_depreciation"),
            util.ref(cr, "account.data_account_type_direct_costs"),
        ],
        "off_balance": [util.ref(cr, "account.data_account_off_sheet"),],
    }
    for internal_group in account_account_type:
        cr.execute(
            """
            UPDATE account_account_type
               SET internal_group=%s
             WHERE internal_group IS NULL
               AND id IN %s
            """, [internal_group, tuple(account_account_type[internal_group])]
        )
    cr.execute(
        """
        UPDATE account_account a
           SET internal_group = t.internal_group
          FROM account_account_type t
         WHERE t.id = a.user_type_id
           AND a.internal_group IS NULL
    """
    )
