# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee", "language_code", "varchar")
    util.create_column(cr, "hr_employee", "nif_country_code", "int4")
    util.create_column(cr, "hr_employee", "has_bicycle", "boolean")

    cr.execute("""
        UPDATE hr_employee
           SET language_code='french',
               nif_country_code=0,
               has_bicycle=FALSE
         WHERE id IN (
            SELECT e.id
            FROM hr_employee e
            INNER JOIN res_company o on e.company_id=o.id
            INNER JOIN res_partner p on o.partner_id=p.id
            INNER JOIN res_country rc on p.country_id=rc.id
            WHERE rc.code='BE'
         )
    """)

    util.create_column(cr, "hr_payslip", "has_attachment_salary", "boolean")

    util.create_column(cr, "hr_work_entry_type", "dmfa_code", "varchar")
    util.create_column(cr, "hr_work_entry_type", "leave_right", "boolean")

    util.create_column(cr, "res_company", "onss_company_id", "varchar")
    util.create_column(cr, "res_company", "onss_registration_number", "varchar")
    util.create_column(cr, "res_company", "dmfa_employer_class", "varchar")
