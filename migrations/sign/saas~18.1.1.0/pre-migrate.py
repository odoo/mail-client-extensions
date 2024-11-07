from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sign_item_type", "model_id", "int4")
    cr.execute(
        """
        UPDATE sign_item_type
           SET model_id=%s
         WHERE auto_field IS NOT NULL
        """,
        [util.ref(cr, "base.model_res_partner")],
    )
