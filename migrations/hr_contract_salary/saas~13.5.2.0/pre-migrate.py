# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.table_exists(cr, "hr_contract_salary_personal_info"):
        cr.execute(
            """
            UPDATE hr_contract_salary_personal_info i
               SET name = f.field_description
              FROM ir_model_fields f
             WHERE f.id = i.res_field_id
               AND i.name IS NULL
            """
        )
