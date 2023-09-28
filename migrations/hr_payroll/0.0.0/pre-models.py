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


if util.version_gte("16.0"):

    class Rule(models.Model):
        _inherit = "hr.salary.rule"
        _module = "hr_payroll"

        def unlink(self):
            external_ids = self.get_external_id()
            for rule in self:
                info = external_ids.get(rule.id) or "{} (code={})".format(rule.name, rule.code)
                util._logger.warning(
                    "The hr.salary.rule record `%s` should be explicitly removed using `util.hr_payroll.remove_salary_rule`",
                    info,
                )
            return super().unlink()


def migrate(cr, version):
    pass
