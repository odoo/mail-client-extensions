from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "sign_send_request", "signers_count")
    util.create_column(cr, "sign_item_type", "field_size", "varchar", default="regular_text")
    util.create_column(cr, "sign_template", "signature_request_validity", "int", default=60)

    cr.execute(
        """
        UPDATE sign_item_type
            SET field_size = CASE
                WHEN default_width <= 0.14 THEN 'short_text'
                WHEN default_width >= 0.24 THEN 'long_text'
                ELSE 'regular_text'
            END
        WHERE item_type = 'text'
        """
    )

    util.make_field_non_stored(cr, "sign.item.type", "default_width", selectable=False)
    util.make_field_non_stored(cr, "sign.item.type", "default_height", selectable=False)
