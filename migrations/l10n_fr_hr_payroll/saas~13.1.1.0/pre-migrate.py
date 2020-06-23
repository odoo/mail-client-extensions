# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "l10n_fr_hr_payroll.holiday_status_heures_sup")
