# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "hr.contract", "thirteen_month")
    util.remove_field(cr, "hr.contract", "double_holidays")
    util.remove_field(cr, "hr.contract", "holidays_editable")
    util.remove_field(cr, "hr.contract", "holidays_compensation")

    cr.execute("""
        UPDATE hr_contract
        SET holidays = holidays - 20.0
        WHERE holidays >= 20.0
        AND id IN (
            SELECT c.id
            FROM hr_contract c
            INNER JOIN res_company o on c.company_id=o.id
            INNER JOIN res_partner p on o.partner_id=p.id
            INNER JOIN res_country rc on p.country_id=rc.id
            WHERE rc.code='BE'
        )
    """)
