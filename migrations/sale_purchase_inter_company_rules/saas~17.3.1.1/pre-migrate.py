from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
            UPDATE res_company
               SET intercompany_document_state = 'posted'
             WHERE auto_validation = TRUE
        """
    )
    util.remove_field(cr, "res.company", "auto_validation")
    util.remove_field(cr, "res.config.settings", "auto_validation")
    util.create_column(cr, "res_company", "intercompany_generate_sales_orders", "boolean")
    util.create_column(cr, "res_company", "intercompany_generate_purchase_orders", "boolean")
    cr.execute(
        """
        UPDATE res_company
           SET intercompany_generate_sales_orders = rule_type IN ('sale', 'sale_purchase'),
               intercompany_generate_purchase_orders = rule_type IN ('purchase', 'sale_purchase')
        """
    )
    util.remove_column(cr, "res_company", "rule_type")
    move_fields = util.module_installed(cr, "sale_purchase_stock_inter_company_rules")
    for model, old_name, new_name in [
        # res.company fields
        ("res.company", "sync_delivery_receipt", "intercompany_sync_delivery_receipt"),
        ("res.company", "warehouse_id", "intercompany_warehouse_id"),
        ("res.company", "intercompany_receipt_type_id", "intercompany_receipt_type_id"),
        # res.config.settings fields
        ("res.config.settings", "sync_delivery_receipt", "intercompany_sync_delivery_receipt"),
        ("res.config.settings", "warehouse_id", "intercompany_warehouse_id"),
        ("res.config.settings", "intercompany_receipt_type_id", "intercompany_receipt_type_id"),
    ]:
        if move_fields:
            if old_name != new_name:
                util.rename_field(cr, model, old_name, new_name)
            util.move_field_to_module(
                cr,
                model,
                new_name,
                "sale_purchase_inter_company_rules",
                "sale_purchase_stock_inter_company_rules",
            )
        else:
            util.remove_field(cr, model, old_name)
