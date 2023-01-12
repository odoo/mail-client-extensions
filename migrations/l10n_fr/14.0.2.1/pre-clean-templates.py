# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_fr.tva_0")
    util.remove_record(cr, "l10n_fr.tva_export_0")
    util.remove_record(cr, "l10n_fr.tva_intra_0")
