from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.remove_field(cr, "pos.config", "module_pos_mercury")
    util.remove_field(cr, "res.config.settings", "module_pos_mercury")

    util.rename_field(cr, "pos.order", "note", "floating_order_name")
    util.rename_field(cr, "pos.order.line", *eb("combo_{line,item}_id"))

    util.rename_xmlid(cr, *eb("point_of_sale.product_jeans_combo_{line,item}_1"))
    util.rename_xmlid(cr, *eb("point_of_sale.product_jeans_combo_{line,item}_2"))
    util.rename_xmlid(cr, *eb("point_of_sale.product_tshirt_combo_{line,item}_1"))
    util.rename_xmlid(cr, *eb("point_of_sale.product_tshirt_combo_{line,item}_2"))
    util.rename_xmlid(cr, *eb("point_of_sale.product_tshirt_combo_{line,item}_3"))
    util.rename_xmlid(cr, *eb("point_of_sale.menu_{pos,product}_combo"))

    util.rename_xmlid(cr, *eb("point_of_sale.access_{pos_combo,product_combo_pos}_manager"))
    util.rename_xmlid(cr, *eb("point_of_sale.access_{pos_combo,product_combo_pos}_user"))
    util.rename_xmlid(cr, *eb("point_of_sale.access_{pos_combo_line,product_combo_item_pos}_manager"))
    util.rename_xmlid(cr, *eb("point_of_sale.access_{pos_combo_line,product_combo_item_pos}_user"))

    for fields_to_add in [
        "card_brand",
        "card_no",
        "payment_ref_no",
        "payment_method_authcode",
        "payment_method_issuer_bank",
        "payment_method_payment_mode",
    ]:
        util.create_column(cr, "pos_payment", fields_to_add, "varchar")

    cr.execute(
        """
        WITH method2account AS (
            SELECT pm.id,
                   company.account_journal_payment_debit_account_id AS account
              FROM pos_payment_method pm
              JOIN res_company company
                ON pm.company_id = company.id
              JOIN account_journal journal
                ON journal.id = pm.journal_id
             WHERE journal.type = 'bank' AND pm.outstanding_account_id IS NULL
        )
        UPDATE pos_payment_method pm
           SET outstanding_account_id = method2account.account
          FROM method2account
         WHERE pm.id = method2account.id
        """
    )

    if util.module_installed(cr, "pos_self_order"):
        util.move_field_to_module(cr, "product.template", "description_self_order", "pos_self_order", "point_of_sale")
        util.rename_field(cr, "product.template", "description_self_order", "public_description")

    util.remove_field(cr, "pos.config", "iface_start_categ_id")
    util.remove_field(cr, "pos.config", "start_category")
    util.remove_field(cr, "res.config.settings", "pos_iface_start_categ_id")
    util.remove_field(cr, "res.config.settings", "pos_start_category")

    util.remove_view(cr, "point_of_sale.qunit_suite")
