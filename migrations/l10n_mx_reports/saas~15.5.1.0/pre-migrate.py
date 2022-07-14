# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    for model in ("l10n_mx.account.diot", "l10n_mx.coa.report", "l10n_mx.trial.report"):
        util.remove_model(cr, model)
