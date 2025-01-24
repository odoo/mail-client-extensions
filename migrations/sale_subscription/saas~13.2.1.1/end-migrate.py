from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE sale_subscription s
           SET stage_category = t.category
          FROM sale_subscription_stage t
         WHERE t.id = s.stage_id
    """
    )

    util.recompute_fields(cr, "sale.subscription.line", ["price_subtotal"], strategy="commit")
    util.recompute_fields(
        cr, "sale.subscription", ["recurring_total", "recurring_tax", "recurring_total_incl"], strategy="commit"
    )
    util.recompute_fields(cr, "sale.subscription.log", ["amount_company_currency"])
