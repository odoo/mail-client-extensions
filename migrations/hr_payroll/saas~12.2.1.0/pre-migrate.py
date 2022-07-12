# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "hr.benefit.employees")

    if util.table_exists(cr, "hr_benefit"):
        util.create_column(cr, "hr_benefit", "contract_id", "int4")
        util.create_column(cr, "hr_benefit", "company_id", "int4")

        # Ok. hr.benefits are new in saas~12.1
        # There is only one supported production database in this version (www.odoo.com)
        # So we can assume that the current contract of employee is the correct one to attach to
        # benefit.
        cr.execute("""
            UPDATE hr_benefit b
               SET contract_id = e.contract_id,
                   company_id = e.company_id
              FROM hr_employee e
             WHERE e.id = b.employee_id
        """)

    # hr.payslip
    util.remove_field(cr, "hr.payslip", "payslip_count")
    cr.execute("UPDATE hr_payslip SET name = concat('Payslip #', id) WHERE name IS NULL")
    cr.execute("""
        UPDATE hr_payslip p
           SET company_id = e.company_id
          FROM hr_employee e
         WHERE e.id = p.employee_id
           AND p.company_id IS NULL
    """)

    # hr.payslip.run
    util.create_column(cr, "hr_payslip_run", "company_id", "int4")
    util.create_column(cr, "hr_payslip_run", "_src_id", "int4")
    cols = util.get_columns(cr, "hr_payslip_run", ("id", "company_id", "_src_id"))
    cr.execute("""
        WITH slips AS (
            SELECT payslip_run_id, company_id, count(*) as cnt
              FROM hr_payslip
             WHERE payslip_run_id IS NOT NULL
               AND company_id IS NOT NULL
          GROUP BY payslip_run_id, company_id
        ),
        runs AS (
            SELECT payslip_run_id, array_agg(company_id ORDER BY cnt DESC) as company_ids
              FROM slips
          GROUP BY payslip_run_id
        ),
        _up AS (
            UPDATE hr_payslip_run r
               SET company_id = runs.company_ids[1]
              FROM runs
             WHERE r.id = runs.payslip_run_id
        ),
        _ins AS (
            INSERT INTO hr_payslip_run({}, _src_id, company_id)
                 SELECT {}, r.id, unnest(c.company_ids[2:array_length(c.company_ids, 1)])
                   FROM hr_payslip_run r
                   JOIN runs c ON (r.id = c.payslip_run_id)
              RETURNING id, company_id, _src_id
        )
        UPDATE hr_payslip s
           SET payslip_run_id = i.id
          FROM _ins i
         WHERE s.payslip_run_id = i._src_id
           AND s.company_id = i.company_id
    """.format(",".join(cols), ",".join("r." + c for c in cols)))

    cr.execute("""
        UPDATE hr_payslip_run r
           SET company_id = u.company_id
          FROM res_users u
         WHERE u.id = COALESCE(r.write_uid, r.create_uid)
           AND r.company_id IS NULL
    """)
    cr.execute("UPDATE hr_payslip_run SET company_id = %s WHERE company_id IS NULL",
               [util.ref(cr, "base.main_company")])

    util.remove_column(cr, "hr_payslip_run", "_src_id")

    # hr.payroll.structure
    util.create_column(cr, "hr_payroll_structure", "country_id", "int4")
    util.create_column(cr, "hr_payroll_structure", "report_id", "int4")
    cr.execute("""
        UPDATE hr_payroll_structure s
           SET country_id = p.country_id
          FROM res_company c
          JOIN res_partner p ON (p.id = c.partner_id)
         WHERE c.id = s.company_id
        """)
    util.remove_field(cr, "hr.payroll.structure", "company_id")

    util.remove_field(cr, "hr.contribution.register", "company_id")
    util.remove_field(cr, "hr.salary.rule.category", "company_id")

    #
    # calendar
    util.create_column(cr, "resource_calendar", "full_time_required_hours", "float8")
    if util.table_exists(cr, "resource_calendar_attendance"):
        cr.execute("""
            WITH cals AS (
                SELECT calendar_id, SUM(hour_to - hour_from) AS total
                  FROM resource_calendar_attendance
                 WHERE resource_id IS NULL
              GROUP BY calendar_id
            )
            UPDATE resource_calendar c
               SET full_time_required_hours = cals.total
              FROM cals
             WHERE c.id = cals.calendar_id
        """)
