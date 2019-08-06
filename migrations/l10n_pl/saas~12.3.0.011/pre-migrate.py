# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "l10n_pt.iva23", noupdate=False)
    util.force_noupdate(cr, "l10n_pt.iva13", noupdate=False)
    util.force_noupdate(cr, "l10n_pt.iva6", noupdate=False)
    util.force_noupdate(cr, "l10n_pt.iva0", noupdate=False)
    util.force_noupdate(cr, "l10n_pt.compiva23", noupdate=False)
    util.force_noupdate(cr, "l10n_pt.compiva13", noupdate=False)
    util.force_noupdate(cr, "l10n_pt.compiva6", noupdate=False)
    util.force_noupdate(cr, "l10n_pt.compiva0", noupdate=False)
