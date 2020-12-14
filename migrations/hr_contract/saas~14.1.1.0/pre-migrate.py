# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.create_column(cr, "hr_employee", "first_contract_date", "date")
    cr.execute(
        """
        WITH employee_first_contract AS (
              SELECT employee_id,
                     MIN(date_start) AS start_date
                FROM hr_contract
               WHERE state != 'cancel'
            GROUP BY employee_id
        )
        UPDATE hr_employee
           SET first_contract_date = employee_first_contract.start_date
          FROM employee_first_contract
         WHERE id = employee_first_contract.employee_id
        """
    )
    util.create_column(cr, "hr_contract", "contract_type_id", "int4")
    util.remove_record(cr, "hr_contract.act_hr_employee_2_hr_contract")
