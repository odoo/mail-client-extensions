from odoo.upgrade import util


def migrate(cr, version):
    us_overtime_work_entry = util.ref(cr, "hr_work_entry.l10n_us_work_entry_type_overtime")

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
               AND c.code = 'US'
              JOIN hr_work_entry_type t
                ON t.code = 'OVERTIME'
             WHERE rc.id = h.company_id
               AND t.id = h.work_entry_type_id
            """,
            [us_overtime_work_entry],
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
               AND c.code = 'US'
              JOIN hr_work_entry_type t
                ON t.code = 'OVERTIME'
             WHERE wd.payslip_id = hp.id
               AND wd.work_entry_type_id = t.id
            """,
            [us_overtime_work_entry],
        ).decode(),
        table="hr_payslip_worked_days",
        alias="wd",
    )
