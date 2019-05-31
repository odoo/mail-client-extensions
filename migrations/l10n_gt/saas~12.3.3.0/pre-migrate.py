# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "l10n_gt.impuestos_plantilla_iva_por_cobrar", noupdate=False)
    util.force_noupdate(cr, "l10n_gt.impuestos_plantilla_iva_por_pagar", noupdate=False)
