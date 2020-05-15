# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("payment.payment_acquirer_{ogone,ingenico}"))
    util.replace_record_references(
        cr,
        ("payment.acquirer", util.ref(cr, "payment.payment_acquirer_custom")),
        ("payment.acquirer", util.ref(cr, "payment.payment_acquirer_transfer")),
        replace_xmlid=False,
    )
    util.remove_record(cr, "payment.payment_acquirer_custom")
    util.remove_view(cr, "payment.assets_backend")
    util.remove_menus(cr, [util.ref(cr, "payment.root_payment_menu")])

    util.create_column(cr, "payment_acquirer", "color", "int4")
    util.create_column(cr, "payment_acquirer", "display_as", "varchar")
    util.create_column(cr, "payment_acquirer", "module_state", "varchar")

    util.rename_field(cr, "payment.acquirer", "environment", "state")
    util.rename_field(cr, "payment.acquirer", "post_msg", "auth_msg")

    cr.execute("UPDATE payment_acquirer SET state='enabled' WHERE state='prod'")
    cr.execute("UPDATE payment_acquirer SET state='disabled' WHERE website_published != true")
    cr.execute(
        """
        UPDATE payment_acquirer a
           SET module_state = m.state
          FROM ir_module_module m
         WHERE m.id = a.module_id
    """
    )
    cr.execute(
        """
        UPDATE payment_acquirer
           SET color = CASE WHEN module_id IS NOT NULL AND module_state != 'installed' THEN 4
                            WHEN state = 'disabled' THEN 3
                            WHEN state = 'test' THEN 2
                            WHEN state = 'enabled' THEN 7
                        END
        """
    )
    cr.execute(
        """
            DELETE
              FROM payment_country_rel
             WHERE payment_id IN (SELECT id
                                    FROM payment_acquirer
                                   WHERE COALESCE(specific_countries, false) = false)
        """
    )

    util.remove_field(cr, "payment.acquirer", "specific_countries")
    util.remove_field(cr, "payment.acquirer", "website_published")
    util.remove_field(cr, "payment.acquirer", "error_msg")

    util.create_column(cr, "payment_token", "company_id", "int4")
    cr.execute(
        """
        UPDATE payment_token k
           SET company_id = a.company_id
          FROM payment_acquirer a
         WHERE a.id = k.acquirer_id
    """
    )
