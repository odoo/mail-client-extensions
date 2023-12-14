# -*- coding: utf-8 -*-
from odoo.addons.l10n_mx_edi_extended import post_init_hook

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1
          FROM ir_model_data
         WHERE module = 'l10n_mx_edi_extended'
           AND model = 'res.city'
         LIMIT 1
        """
    )
    if not cr.rowcount:
        post_init_hook(cr, util.env(cr))
