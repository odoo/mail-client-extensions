# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_mx_edi.sat_digital_certificate")
    util.recompute_fields(cr, "account.move", ["l10n_mx_edi_external_trade"])
