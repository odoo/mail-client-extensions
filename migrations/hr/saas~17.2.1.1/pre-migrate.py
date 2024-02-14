from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "hr_recruitment"):
        cr.execute(
            """
            WITH sub AS (
                SELECT job_id,
                       COUNT(*)
                    AS count
                  FROM hr_applicant
                 WHERE date_closed IS NOT NULL
                   AND active IS NOT NULL
              GROUP BY job_id
            )

            UPDATE hr_job
               SET no_of_hired_employee = sub.count
              FROM sub
             WHERE hr_job.id = sub.job_id
            """
        )
    else:
        util.remove_field(cr, "hr.job", "no_of_hired_employee")
