# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.partner", "l10n_cl_activity_description", "l10n_cl_edi", "l10n_cl")
    util.move_field_to_module(cr, "res.company", "l10n_cl_activity_description", "l10n_cl_edi", "l10n_cl")  # Not stored
