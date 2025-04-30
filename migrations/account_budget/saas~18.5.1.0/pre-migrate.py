from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    for model, fname in [
        ("budget.line", "committed_amount"),
        ("budget.line", "committed_percentage"),
        ("budget.report", "committed"),
        ("purchase.order", "is_above_budget"),
        ("purchase.order", "is_analytic"),
        ("purchase.order.line", "analytic_json"),
        ("purchase.order.line", "is_above_budget"),
        ("purchase.order.line", "budget_line_ids"),
    ]:
        util.move_field_to_module(cr, model, fname, "account_budget", "account_budget_purchase")
    util.rename_xmlid(cr, *eb("account_budget{,_purchase}.purchase_order_form_account_budget"))
