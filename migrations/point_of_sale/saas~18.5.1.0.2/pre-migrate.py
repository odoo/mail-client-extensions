from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "point_of_sale.pos_iot_config_view_form")
    util.make_field_non_stored(cr, "res.config.settings", "pos_epson_printer_ip", selectable=True)

    util.convert_m2o_field_to_m2m(
        cr,
        "pos.order",
        "procurement_group_id",
        new_name="stock_reference_ids",
        m2m_table="stock_reference_pos_order_rel",
        col1="reference_id",
        col2="pos_order_id",
    )
    util.convert_m2o_field_to_m2m(
        cr,
        "stock.reference",
        "pos_order_id",
        new_name="pos_order_ids",
        m2m_table="stock_reference_pos_order_rel",
        col1="pos_order_id",
        col2="reference_id",
    )
    util.create_column(cr, "pos_order", "source", "varchar", default="pos")

    # We cannot rename these fields to reuse them since isn't exactly the same type of sequence
    # and the sequence is not used in the same way.
    util.remove_field(cr, "pos.session", "order_seq_id")
    util.remove_field(cr, "pos.session", "login_number_seq_id")

    # These fields can be renamed, but the associated sequence need to be updated
    # to match the new padding and implementation.
    util.rename_field(cr, "pos.config", "sequence_id", "order_seq_id")
    util.rename_field(cr, "pos.config", "sequence_line_id", "order_line_seq_id")

    # Remove linked fields in res.config.settings, they are not used anymore
    util.remove_field(cr, "res.config.settings", "pos_sequence_id")

    # Update the sequences to match the new padding and implementation
    cr.execute(
        """
        UPDATE ir_sequence s
           SET padding = 6,
               implementation = 'no_gap'
          FROM pos_config c
         WHERE s.id = c.order_seq_id
            OR s.id = c.order_line_seq_id
        """
    )
