from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_model(cr, *eb("account.{disallowed.expenses,fiscal.categories}.fleet.report.handler"))
    util.rename_xmlid(
        cr, *eb("account_fiscal_categories_fleet.view_account_{disallowed_expenses,fiscal}_category_tree")
    )
    util.rename_xmlid(
        cr, *eb("account_fiscal_categories_fleet.view_account_{disallowed_expenses,fiscal}_category_form")
    )
