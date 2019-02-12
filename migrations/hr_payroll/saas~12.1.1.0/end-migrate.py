# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # done as end- script becuase table used by l10n_be_payroll migration
    util.remove_model(cr, "hr.contract.advantage.template")
