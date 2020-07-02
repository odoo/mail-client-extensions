# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO ir_property(
            name, company_id, type, fields_id,
            res_id,
            value_reference
        )
        SELECT f.name, j.company_id, 'many2one', f.id,
               CONCAT('hr.payroll.structure,', p.struct_id),
               CONCAT('account.journal,', j.id)
          FROM hr_payslip p
          JOIN account_journal j ON (j.id = p.journal_id)
          JOIN ir_model_fields f ON (f.model = 'hr.payroll.structure' AND f.name = 'journal_id')
      GROUP BY f.name, j.company_id, f.id, p.struct_id, j.id
        """
    )

    util.remove_column(cr, "hr_payslip", "journal_id")  # Yes, intended to not remove field
