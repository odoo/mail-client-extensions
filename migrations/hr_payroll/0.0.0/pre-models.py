# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

if util.version_gte("saas~12.5"):
    from odoo import models

    from odoo.addons.hr_payroll.models import hr_rule_parameter as _ignore  # noqa: F401

    class HRPV(models.Model):
        _name = "hr.rule.parameter.value"
        _inherit = ["hr.rule.parameter.value"]
        _module = "hr_payroll"
        _match_uniq = True

    class HRP(models.Model):
        _name = "hr.rule.parameter"
        _inherit = ["hr.rule.parameter"]
        _module = "hr_payroll"
        _match_uniq = True


def migrate(cr, version):
    pass
