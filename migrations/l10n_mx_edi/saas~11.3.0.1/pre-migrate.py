# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_mx_edi.cfdiv32")
    util.remove_record(cr, "l10n_mx_edi.payment_method_na")

    util.remove_field(cr, "account.invoice", "l10n_mx_edi_uuid")
