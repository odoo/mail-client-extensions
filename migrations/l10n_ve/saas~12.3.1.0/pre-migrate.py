# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "l10n_ve.tax0sale", noupdate=False)
    util.force_noupdate(cr, "l10n_ve.tax1sale", noupdate=False)
    util.force_noupdate(cr, "l10n_ve.tax2sale", noupdate=False)
    util.force_noupdate(cr, "l10n_ve.tax3sale", noupdate=False)
    util.force_noupdate(cr, "l10n_ve.tax0purchase", noupdate=False)
    util.force_noupdate(cr, "l10n_ve.tax1purchase", noupdate=False)
    util.force_noupdate(cr, "l10n_ve.tax2purchase", noupdate=False)
    util.force_noupdate(cr, "l10n_ve.tax3purchase", noupdate=False)
