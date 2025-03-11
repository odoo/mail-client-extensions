from odoo.upgrade import util


def migrate(cr, version):
    pl_sick_leave_id = util.ref(cr, "hr_holidays.l10n_pl_leave_type_sick_leave")
    pl_sick_work_entry = util.ref(cr, "hr_work_entry.l10n_pl_work_entry_type_sick_leave")

    util.explode_execute(
        cr,
        cr.mogrify(
            """
            UPDATE hr_leave l
               SET holiday_status_id = %s
              FROM hr_work_entry we
              JOIN hr_work_entry_type wet
                ON wet.id = we.work_entry_type_id
               AND wet.code = 'LEAVE110'
              JOIN hr_employee e
                ON e.id = we.employee_id
              JOIN res_company rc
                ON rc.id = e.company_id
              JOIN res_partner rp
                ON rp.id = rc.partner_id
              JOIN res_country c
                ON c.id = rp.country_id
               AND c.code = 'PL'
             WHERE we.leave_id = l.id
            """,
            [pl_sick_leave_id],
        ).decode(),
        table="hr_leave",
        alias="l",
    )

    util.explode_execute(
        cr,
        cr.mogrify(
            """
            UPDATE hr_work_entry h
               SET work_entry_type_id = %s
              FROM res_company rc
              JOIN res_partner rp
                ON rp.id = rc.partner_id
              JOIN res_country c
                ON c.id = rp.country_id
               AND c.code = 'PL'
              JOIN hr_work_entry_type t
                ON t.code = 'LEAVE110'
             WHERE rc.id = h.company_id
               AND t.id = h.work_entry_type_id
            """,
            [pl_sick_work_entry],
        ).decode(),
        table="hr_work_entry",
        alias="h",
    )

    util.explode_execute(
        cr,
        cr.mogrify(
            """
            UPDATE hr_payslip_worked_days wd
               SET work_entry_type_id = %s
              FROM hr_payslip hp
              JOIN hr_payroll_structure s
                ON s.id = hp.struct_id
              JOIN res_country c
                ON c.id = s.country_id
               AND c.code = 'PL'
              JOIN hr_work_entry_type t
                ON t.code = 'LEAVE110'
             WHERE wd.payslip_id = hp.id
               AND wd.work_entry_type_id = t.id
            """,
            [pl_sick_work_entry],
        ).decode(),
        table="hr_payslip_worked_days",
        alias="wd",
    )
