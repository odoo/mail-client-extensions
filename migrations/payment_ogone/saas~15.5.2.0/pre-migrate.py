# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        DELETE
        FROM ir_config_parameter
        WHERE "key" = 'payment_ogone.hash_function'
        RETURNING value
        """
    )

    [hash_function] = cr.fetchone() or ["sha1"]

    util.create_column(cr, "payment_provider", "ogone_hash_function", "varchar")

    cr.execute(
        """
        UPDATE payment_provider
        SET ogone_hash_function = %s
        WHERE "code" = 'ogone'
        """,
        [hash_function],
    )

    util.rename_xmlid(cr, "payment_ogone.payment_acquirer_form", "payment_ogone.payment_provider_form")
