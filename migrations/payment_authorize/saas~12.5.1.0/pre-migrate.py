# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "payment_acquirer", "authorize_signature_key", "varchar")
    util.create_column(cr, "payment_acquirer", "authorize_client_key", "varchar")

    cr.execute(
        r"""
        WITH keys AS (
            DELETE FROM ir_config_parameter
                  WHERE key LIKE 'payment\_authorize.signature\_key\_%'
              RETURNING SUBSTR(key, 33)::int4 id, value
        )
        UPDATE payment_acquirer a
           SET authorize_signature_key = k.value
          FROM keys k
         WHERE k.id = a.id
    """
    )
