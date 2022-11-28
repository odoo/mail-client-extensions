# -*- coding: utf-8 -*-
from odoo.upgrade import util

eb = util.expand_braces


def migrate(cr, version):
    util.rename_field(cr, "sale.order", *eb("tax_totals{_json,}"))
    util.create_column(cr, "account_move_line", "is_downpayment", "boolean")
    query = """
        UPDATE account_move_line aml
           SET is_downpayment = TRUE
          FROM sale_order_line_invoice_rel r
          JOIN sale_order_line sol ON sol.id = r.order_line_id
         WHERE aml.id = r.invoice_line_id
           AND sol.is_downpayment
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line", alias="aml"))
    util.rename_xmlid(cr, "sale.acquirer_form_inherit_sale", "sale.payment_provider_form")

    util.rename_model(cr, "sale.payment.acquirer.onboarding.wizard", "sale.payment.provider.onboarding.wizard")

    util.rename_xmlid(cr, *eb("sale.access_sale_payment_{acquirer,provider}_onboarding_wizard"))
    util.rename_xmlid(cr, *eb("sale.sale_payment_{acquirer,provider}_onboarding_wizard_rule"))

    util.create_column(cr, "sale_order_line", "analytic_distribution", "jsonb")

    # The accounts were set on the SO and the tags on the SOL, this is why we can't use `upgrade_analytic_distribution`
    # The total amount of the account is added as 100% in the business code
    query = """
        WITH _lines AS (
            SELECT id FROM sale_order_line line WHERE {parallel_filter}
        ), line_sum AS (
            SELECT line.id AS line_id,
                   distribution.account_id AS account_id,
                   SUM(distribution.percentage) AS percentage
              FROM _lines line
              JOIN account_analytic_tag_sale_order_line_rel analytic_rel ON analytic_rel.sale_order_line_id = line.id
              JOIN account_analytic_distribution distribution ON analytic_rel.account_analytic_tag_id = distribution.tag_id
          GROUP BY line_id, account_id
        ),
        line_distribution AS (
            SELECT line_id,
                   json_object_agg(account_id, percentage) AS distribution
              FROM line_sum
          GROUP BY line_id
        )
        UPDATE sale_order_line line
           SET analytic_distribution = line_distribution.distribution
          FROM line_distribution
         WHERE line.id = line_distribution.line_id
    """

    util.parallel_execute(cr, util.explode_query_range(cr, query, table="sale_order_line", alias="line"))

    util.remove_field(cr, "sale.order.line", "analytic_tag_ids")
    util.move_field_to_module(cr, "sale.order.line", "product_type", "sale_stock", "sale")

    util.remove_field(cr, "res.config.settings", "confirmation_mail_template_id")
    util.remove_menus(cr, [util.ref(cr, "sale.menu_report_product_all")])
