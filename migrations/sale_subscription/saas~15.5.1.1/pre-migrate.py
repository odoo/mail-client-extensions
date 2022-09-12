# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    old_user = util.ref(cr, "sale_subscription.group_sale_subscription_view")
    old_manager = util.ref(cr, "sale_subscription.group_sale_subscription_manager")
    new_user = util.ref(cr, "sales_team.group_sale_salesman")
    new_manager = util.ref(cr, "sales_team.group_sale_manager")

    util.replace_record_references_batch(
        cr, {old_user: new_user, old_manager: new_manager}, "res.groups", replace_xmlid=False
    )

    util.remove_record(cr, "sale_subscription.group_sale_subscription_view")
    util.remove_record(cr, "sale_subscription.group_sale_subscription_manager")

    invoice_batch = util.ref(cr, "sale_subscription.invoice_batch")
    util.create_column(cr, "sale_order", "is_batch", "boolean")
    if invoice_batch and util.table_exists(cr, "account_analytic_tag_sale_order_rel"):
        query = """
            UPDATE sale_order so
               SET is_batch = 't'
              FROM account_analytic_tag_sale_order_rel rel
             WHERE rel.sale_order_id = so.id
               AND rel.account_analytic_tag_id = %s
        """
        query = cr.mogrify(query, [invoice_batch]).decode()
        util.parallel_execute(cr, util.explode_query_range(cr, query, table="sale_order", alias="so"))

    invoiced_cron_tag = util.ref(cr, "sale_subscription.invoiced_cron_tag")
    util.create_column(cr, "sale_order", "is_invoice_cron", "boolean")
    if invoiced_cron_tag and util.table_exists(cr, "account_analytic_tag_sale_order_rel"):
        query = """
            UPDATE sale_order so
               SET is_invoice_cron = 't'
              FROM account_analytic_tag_sale_order_rel rel
             WHERE rel.sale_order_id = so.id
               AND rel.account_analytic_tag_id = %s
        """
        query = cr.mogrify(query, [invoiced_cron_tag]).decode()
        util.parallel_execute(cr, util.explode_query_range(cr, query, table="sale_order", alias="so"))

    util.remove_field(cr, "sale.order", "account_tag_ids")
    util.remove_field(cr, "sale.order.alert", "tag_id")
    cr.execute("DELETE FROM sale_order_alert WHERE action = 'set_tag'")
    util.remove_field(cr, "sale.order.template", "tag_ids")
