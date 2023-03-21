# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account_edi_proxy_client.user", "edi_format_code")
    util.remove_field(cr, "account_edi_proxy_client.user", "edi_format_id")
    util.remove_constraint(
        cr, "account_edi_proxy_client_user", "account_edi_proxy_client_user_unique_edi_identification_per_for"
    )

    util.create_column(cr, "account_edi_proxy_client_user", "proxy_type", "varchar")
    cr.execute("DELETE FROM ir_config_parameter WHERE key='account_edi_proxy_client.demo' RETURNING value")

    [mode] = cr.fetchone() or ["prod"]
    if mode not in ("test", "prod"):
        mode = "demo"
    util.create_column(cr, "account_edi_proxy_client_user", "edi_mode", "varchar", default=mode)
