from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_model(cr, *eb("account.{disallowed.expenses,fiscal}.category"))
    util.rename_model(cr, *eb("account.{disallowed.expenses,fiscal}.report.handler"))
    util.rename_model(cr, *eb("account.{disallowed.expenses,account.fiscal}.rate"))

    util.rename_field(cr, "account.account", "disallowed_expenses_category_id", "fiscal_category_id")
    util.remove_field(cr, "account.fiscal.category", "current_rate")
    util.remove_field(cr, "account.fiscal.category", "rate_ids")
    util.remove_field(cr, "account.account.fiscal.rate", "category_id", drop_column=False)

    util.remove_record(cr, "account_fiscal_categories.action_account_disallowed_expenses_category_list")
    util.remove_record(cr, "account_fiscal_categories.action_account_report_de")
    util.remove_record(cr, "account_fiscal_categories.account_disallowed_expenses_comp_rule")
    util.remove_view(cr, "account_fiscal_categories.account_disallowed_expenses_rate_tree")

    util.rename_xmlid(cr, *eb("account_fiscal_categories.{disallowed_expenses,fiscal}_report"))
    util.rename_xmlid(cr, *eb("account_fiscal_categories.{disallowed_expenses,fiscal}_report_total_amount"))
    util.rename_xmlid(cr, *eb("account_fiscal_categories.{disallowed_expenses,fiscal}_report_rate"))
    util.rename_xmlid(cr, *eb("account_fiscal_categories.{disallowed_expenses,fiscal}_report_deductible_amount"))
    util.rename_xmlid(cr, *eb("account_fiscal_categories.view_account_{disallowed_expenses,fiscal}_category_tree"))
    util.rename_xmlid(cr, *eb("account_fiscal_categories.view_account_{disallowed_expenses,fiscal}_category_search"))
    util.rename_xmlid(cr, *eb("account_fiscal_categories.view_account_{disallowed_expenses,fiscal}_category_form"))
    util.rename_xmlid(cr, *eb("account_fiscal_categories.action_account_{disallowed_expenses,fiscal}_category_list"))
    util.rename_xmlid(
        cr, *eb("account_fiscal_categories.menu_action_account_{disallowed_expenses,fiscal}_category_list")
    )
