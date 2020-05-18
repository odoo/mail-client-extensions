# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "payment_acquirer", "sips_key_version", "int4")
    cr.execute("SELECT value FROM ir_config_parameter WHERE key='sips.key_version'")
    query_result = cr.fetchone()
    key_version_default = query_result and query_result[0] or "2"
    cr.execute(
        """
        UPDATE payment_acquirer
        SET sips_key_version=%s
        WHERE provider='sips'
    """,
        key_version_default,
    )
