from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.session", "login_number")
    util.remove_field(cr, "pos.session", "sequence_number")
    util.rename_field(cr, "pos.order", "general_note", "general_customer_note")
    util.delete_unused(cr, "point_of_sale.product_category_pos")
    util.remove_field(cr, "res.config.settings", "module_pos_paytm")

    util.remove_view(cr, "point_of_sale.product_product_view_form_normalized_pos")

    cr.execute(
        """
         DELETE FROM pos_bill_pos_config_rel r
         USING pos_bill b
         WHERE b.id = r.pos_bill_id
           AND b.for_all_config IS TRUE
        """
    )
    util.remove_field(cr, "pos.bill", "for_all_config")

    util.create_column(cr, "pos_order", "tracking_number", "varchar")
    util.explode_execute(
        cr,
        """
        UPDATE pos_order
           SET tracking_number = LPAD(((session_id % 10) * 100 + (sequence_number % 100))::varchar, 3, '0')
        """,
        table="pos_order",
    )
