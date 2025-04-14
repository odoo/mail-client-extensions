import re

from odoo.osv.expression import normalize_leaf
from odoo.tools import flatten

from odoo.upgrade import util


def migrate(cr, version):
    # move user_type_id data from account.account.type to account.account
    types_mapping = {
        util.ref(cr, "account.data_account_type_receivable"): "asset_receivable",
        util.ref(cr, "account.data_account_type_liquidity"): "asset_cash",
        util.ref(cr, "account.data_account_type_current_assets"): "asset_current",
        util.ref(cr, "account.data_account_type_non_current_assets"): "asset_non_current",
        util.ref(cr, "account.data_account_type_prepayments"): "asset_prepayments",
        util.ref(cr, "account.data_account_type_fixed_assets"): "asset_fixed",
        util.ref(cr, "account.data_account_type_payable"): "liability_payable",
        util.ref(cr, "account.data_account_type_credit_card"): "liability_credit_card",
        util.ref(cr, "account.data_account_type_current_liabilities"): "liability_current",
        util.ref(cr, "account.data_account_type_non_current_liabilities"): "liability_non_current",
        util.ref(cr, "account.data_account_type_equity"): "equity",
        util.ref(cr, "account.data_unaffected_earnings"): "equity_unaffected",
        util.ref(cr, "account.data_account_type_revenue"): "income",
        util.ref(cr, "account.data_account_type_other_income"): "income_other",
        util.ref(cr, "account.data_account_type_expenses"): "expense",
        util.ref(cr, "account.data_account_type_depreciation"): "expense_depreciation",
        util.ref(cr, "account.data_account_type_direct_costs"): "expense_direct_cost",
        util.ref(cr, "account.data_account_off_sheet"): "off_balance",
        util.ref(cr, "l10n_pl.account_type_settlement"): "off_balance",
        util.ref(cr, "l10n_syscohada.account_type_special"): "off_balance",
        util.ref(cr, "l10n_gr.account_type_other"): "off_balance",
        util.ref(cr, "l10n_th.acc_type_reconciled"): "off_balance",
    }

    util.create_column(cr, "account_account", "account_type", "varchar", default="off_balance")
    util.create_column(cr, "account_account_template", "account_type", "varchar", default="off_balance")
    query_account = """
        UPDATE account_account aa
           SET account_type = %s
         WHERE user_type_id = %s
    """
    query_account_template = """
        UPDATE account_account_template aat
           SET account_type = %s
         WHERE user_type_id = %s
    """
    queries = [
        cr.mogrify(query_account, (new_type, old_type)).decode()
        for old_type, new_type in types_mapping.items()
        if old_type
    ]
    queries += [
        cr.mogrify(query_account_template, (new_type, old_type)).decode()
        for old_type, new_type in types_mapping.items()
        if old_type
    ]
    util.parallel_execute(cr, queries)

    # move include_initial_balance data from account.account.type to account.account
    util.create_column(cr, "account_account", "include_initial_balance", "boolean")
    query = """
        UPDATE account_account aa
           SET include_initial_balance = t.include_initial_balance
          FROM account_account_type t
         WHERE aa.user_type_id = t.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_account", alias="aa"))

    # adapt domains for user_type_id and internal_type before removing them
    def internal_type_adapter(leaf, is_or, negated):
        mapping = {
            "other": (
                "asset_current",
                "asset_non_current",
                "asset_prepayments",
                "asset_fixed",
                "liability_current",
                "liability_non_current",
                "equity",
                "equity_unaffected",
                "income",
                "income_other",
                "expense",
                "expense_depreciation",
                "expense_direct_cost",
                "off_balance",
            ),
            "receivable": "asset_receivable",
            "payable": "liability_payable",
            "liquidity": ("asset_cash", "liability_credit_card"),
        }
        left, operator, right = normalize_leaf(leaf)
        if isinstance(right, str):
            right = mapping.get(right, right)
        elif isinstance(right, (list, tuple)) and all(isinstance(x, str) for x in right):
            right = flatten(mapping.get(r, r) for r in right)
        if isinstance(right, (list, tuple)) and operator in ("=", "!="):
            operator = "in" if operator == "=" else "not in"
        return [(left, operator, right)]

    def type_adapter(leaf, is_or, negated):
        left, operator, right = leaf
        if "user_type_id.type" in left:
            return internal_type_adapter(
                (re.sub(r"\buser_type_id\.type\b", "account_type", left), operator, right), is_or, negated
            )
        if "user_type_id.id" in left:
            left = re.sub(r"\buser_type_id\.id\b", "account_type", left)
        right = (
            [types_mapping.get(t, t) for t in right]
            if isinstance(right, (tuple, list))
            else types_mapping.get(right, right)
        )
        return [(left, operator, right)]

    def account_account_adapter(leaf, is_or, negated):
        left, operator, right = leaf
        if "user_type_id.internal_group" in left or "user_type_id.include_initial_balance" in left:
            return [(re.sub(r"\buser_type_id\.", "", left), operator, right)]
        return type_adapter(leaf, is_or, negated)

    util.update_field_usage(
        cr, "account.account", "user_type_id", "account_type", domain_adapter=account_account_adapter
    )
    util.update_field_usage(cr, "account.account.template", "user_type_id", "account_type", domain_adapter=type_adapter)
    util.update_field_usage(cr, "account.asset", "user_type_id", "account_type", domain_adapter=type_adapter)
    util.update_field_usage(
        cr, "account.account", "internal_type", "account_type", domain_adapter=internal_type_adapter
    )

    util.remove_field(cr, "account.account", "user_type_id")
    util.remove_field(cr, "account.account", "internal_type")
    util.remove_field(cr, "account.account.template", "user_type_id")

    util.remove_field(cr, "account.journal", "type_control_ids")
    # Initialize the column manually so that everything is False and not computed
    util.create_column(cr, "account_journal", "payment_sequence", "bool")

    util.remove_field(cr, "account.move.line", "account_internal_type")
    util.remove_model(cr, "account.account.type")
