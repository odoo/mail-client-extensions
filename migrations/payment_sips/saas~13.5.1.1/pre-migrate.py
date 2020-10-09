# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "payment_acquirer", "sips_key_version", "int4")

    # force test values for test acquirers
    cr.execute(
        """
            UPDATE payment_acquirer
               SET sips_merchant_id = '002001000000001',
                   sips_secret = '002001000000001_KEY1',
                   sips_key_version = 1
             WHERE provider = 'sips'
               AND state != 'enabled'
        """
    )

    cr.execute("DELETE FROM ir_config_parameter WHERE key='sips.key_version' RETURNING value")
    [key_version] = cr.fetchone() or [2]
    cr.execute(
        """
            UPDATE payment_acquirer
               SET sips_key_version = %s
             WHERE provider = 'sips'
               AND sips_key_version IS NULL
        """,
        [int(key_version)],
    )
