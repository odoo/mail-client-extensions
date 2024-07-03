from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr, "website_sale.payment_delivery_methods", util.update_record_from_xml, reset_translations={"arch_db"}
    )

    # Set the arch for carried over cowed views, see pre-migrate.py
    for key in ["website_sale.extra_info", "website_sale.accept_terms_and_conditions"]:
        cr.execute(
            """
            UPDATE ir_ui_view cowed
               SET arch_db = original.arch_db
              FROM ir_ui_view original
             WHERE original.key = %s
               AND original.website_id IS NULL
               AND cowed.key = original.key
               AND cowed.website_id IS NOT NULL
            """,
            [key],
        )
