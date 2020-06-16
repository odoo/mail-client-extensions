# -*- coding: utf-8 -*-
from odoo import models


def migrate(cr, version):
    pass


class HrContract(models.Model):
    _inherit = "hr.contract"
    _module = "l10n_be_hr_contract_salary"

    def _compute_final_yearly_costs(self):
        if self.env.context.get("_mig_dry_run", True):
            for contract in self:
                contract.final_yearly_costs = 0
        else:
            super()._compute_final_yearly_costs()
