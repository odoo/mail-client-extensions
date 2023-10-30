# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_partner", "l10n_mx_edi_locality", "varchar")
    util.move_field_to_module(cr, "res.city", "l10n_mx_edi_code", "l10n_mx_edi", "l10n_mx_edi_extended")
