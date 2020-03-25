# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # The old l10n_ch.print_qrcode must be removed and used to know whether or
    # not the company is using the new generic QR-code option
    cr.execute("""
        select value from ir_config_parameter
        where key = 'l10n_ch.print_qrcode';
    """)

    config_param = cr.fetchone()
    if config_param and config_param[0]:
        cr.execute("""
            update res_company
            set qr_code = true;
        """)

    cr.execute("""
        delete from ir_config_parameter
        where key = 'l10n_ch.print_qrcode';
    """)

    util.remove_field(cr, "res.config.settings", "l10n_ch_print_qrcode")