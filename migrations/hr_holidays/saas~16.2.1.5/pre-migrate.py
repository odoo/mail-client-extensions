# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "hr_leave_type_res_users_rel", "hr_leave_type", "res_users")
    cr.execute(
        """
        INSERT INTO hr_leave_type_res_users_rel(hr_leave_type_id, res_users_id)
             SELECT id, responsible_id
               FROM hr_leave_type
              WHERE responsible_id is NOT NULL
    """
    )
    util.adapt_domains(cr, "hr.leave.type", "responsible_id", "responsible_ids")
    util.remove_field(cr, "hr.leave.type", "responsible_id")
    util.delete_unused(cr, "hr_holidays.mail_act_leave_allocation_second_approval")

    util.create_column(cr, "hr_leave_accrual_plan", "company_id", "int4")
    cr.execute(
        """
            UPDATE hr_leave_accrual_plan p
               SET company_id = t.company_id
              FROM hr_leave_type t
             WHERE t.id = p.time_off_type_id
        """
    )
