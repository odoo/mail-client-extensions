# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "l10n_mx.tag_diot_16", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_16_non_cre", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_16_imp", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_0", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_8", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_8_non_cre", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_ret", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tag_diot_exento", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax9", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax12", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax1", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax2", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax3", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax5", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax7", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax8", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax13", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax14", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax16", noupdate=False)
    util.force_noupdate(cr, "l10n_mx.tax17", noupdate=False)
