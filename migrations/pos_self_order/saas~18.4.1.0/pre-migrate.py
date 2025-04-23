from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT relation_table
          FROM ir_model_fields
         WHERE model = 'pos.config'
           AND name IN ('self_ordering_image_home_ids', 'self_ordering_image_background_ids')
        """
    )

    for (table,) in cr.fetchall():
        cr.execute(
            util.format_query(
                cr,
                """
                UPDATE ir_attachment AS att
                   SET public = true
                  FROM {} t
                 WHERE att.id = t.ir_attachment_id
                """,
                table,
            )
        )
