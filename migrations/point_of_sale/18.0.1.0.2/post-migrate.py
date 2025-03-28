from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "res_partner", "phone_sanitized"):
        util.explode_execute(
            cr,
            """
            UPDATE pos_order
               SET mobile = partner.phone_sanitized,
                   email = partner.email
              FROM res_partner partner
             WHERE pos_order.partner_id = partner.id
               AND (partner.phone_sanitized IS NOT NULL
                    OR partner.email IS NOT NULL)
               AND {parallel_filter}
            """,
            table="pos_order",
        )
    else:
        util.recompute_fields(cr, "pos.order", ["email", "mobile"])
