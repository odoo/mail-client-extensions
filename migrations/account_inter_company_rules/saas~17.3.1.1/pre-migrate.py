from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "intercompany_document_state", "varchar", default="draft")
    util.remove_field(cr, "res.company", "intercompany_transaction_message")
    util.remove_field(cr, "res.config.settings", "intercompany_transaction_message")
    util.remove_field(cr, "res.config.settings", "rules_company_id")
    util.create_column(cr, "res_company", "intercompany_generate_bills_refund", "boolean")
    cr.execute(
        """
            UPDATE res_company SET intercompany_generate_bills_refund = true WHERE rule_type = 'invoice_and_refund'
        """
    )

    has_sale_purchase = util.module_installed(cr, "sale_purchase_inter_company_rules")

    # In this adapter the selection field rule_type will be change to some booleans, here are the different possibilities
    # Without the module sale_purchase_inter_company_rules, rule_type could be either:
    # - invoice_and_refund or not_synchronize
    # With the module installed we add:
    # - sale, purchase and sale_purchase
    #
    # Different cases without the module sale_purchase_inter_company_rules:
    # (rule_type = invoice_and_refund) ==> (intercompany_generate_bills_refund = True)
    # (rule_type = not_synchronize) ==> every new boolean are False
    # With the module:
    # (rule_type = sale) ==> (intercompany_generate_sales_orders = True)
    # (rule_type = purchase) ==> (intercompany_generate_purchase_orders = True)
    # (rule_type = sale_purchase ==> (intercompany_generate_sales_orders = True and intercompany_generate_purchase_orders = True)
    def rule_type_selection_to_boolean_adapter(leaf, _or, _neg):
        left, op, right = leaf
        if op not in ["=", "!="]:
            return [leaf]

        path = left.rsplit(".", maxsplit=1)[0]
        if right == "invoice_and_refund":
            return [(path + ".intercompany_generate_bills_refund", op, True)]
        elif right == "not_synchronize":
            if has_sale_purchase:
                return [
                    "|",
                    "|",
                    (path + ".intercompany_generate_bills_refund", op, False),
                    (path + ".intercompany_generate_sales_orders", op, False),
                    (path + ".intercompany_generate_purchase_orders", op, False),
                ]
            return [(path + ".intercompany_generate_bills_refund", op, False)]
        elif has_sale_purchase:
            if right == "sale":
                return [(path + ".intercompany_generate_sales_orders", op, True)]
            elif right == "purchase":
                return [(path + ".intercompany_generate_purchase_orders", op, True)]
            elif right == "sale_purchase":
                return [
                    "&",
                    (path + ".intercompany_generate_sales_orders", op, True),
                    (path + ".intercompany_generate_purchase_orders", op, True),
                ]
        return [leaf]

    util.adapt_domains(cr, "res.company", "rule_type", "ignore", adapter=rule_type_selection_to_boolean_adapter)
    # the column will be removed in sale_purchase_inter_company_rules
    util.remove_field(cr, "res.company", "rule_type", drop_column=not has_sale_purchase)
    util.remove_field(cr, "res.config.settings", "rule_type")
