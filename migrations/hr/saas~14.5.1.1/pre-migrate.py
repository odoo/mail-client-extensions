# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "hr.employee", "id_card", "l10n_be_hr_contract_salary", "hr")
    util.move_field_to_module(cr, "hr.employee", "driving_license", "l10n_be_hr_contract_salary", "hr")

    util.create_column(cr, "hr_job", "sequence", "int4", default=10)
    cr.execute(
        """
        UPDATE hr_job
           SET sequence = id,
               no_of_recruitment = GREATEST(no_of_recruitment, 0)
    """
    )
