# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.city", "l10n_mx_edi_code", "l10n_mx_edi", "l10n_mx_edi_extended")

    # Move external ids of city in the right module in case they were in the wrong one
    cr.execute(
        """
        UPDATE ir_model_data
          SET module = 'l10n_mx_edi_extended'
        WHERE module = 'l10n_mx_edi'
          AND model = 'res.city'
        """
    )
