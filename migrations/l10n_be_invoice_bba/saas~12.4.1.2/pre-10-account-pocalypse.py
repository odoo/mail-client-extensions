# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Manual update due to noupdate block.
    util.force_noupdate(cr, 'l10n_be_invoice_bba.email_template_edi_invoice', noupdate=False)
