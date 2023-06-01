# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "l10n_hk"):
        util.move_field_to_module(cr, "res.partner.bank", "l10n_hk_fps_type", "l10n_hk", "account_qr_code_emv")
        util.rename_field(cr, "res.partner.bank", "l10n_hk_fps_type", "proxy_type")
        util.move_field_to_module(cr, "res.partner.bank", "l10n_hk_fps_identifier", "l10n_hk", "account_qr_code_emv")
        util.rename_field(cr, "res.partner.bank", "l10n_hk_fps_identifier", "proxy_value")
        util.move_field_to_module(cr, "res.partner.bank", "country_code", "l10n_hk", "account_qr_code_emv")
