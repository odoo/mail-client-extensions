from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr, "website_sale.payment_delivery_methods", util.update_record_from_xml, reset_translations={"arch_db"}
    )

    # Set the arch for carried over cowed views, see pre-migrate.py
    cr.execute(
        """
        UPDATE ir_ui_view v
           SET arch_db = vv.arch_db
          FROM ir_ui_view vv
         WHERE vv.key = 'website_sale.extra_info'
           AND vv.website_id IS NULL -- the "main" view, not a cowed one
           AND v.key = 'website_sale.extra_info'
           AND v.website_id IS NOT NULL
        """
    )
