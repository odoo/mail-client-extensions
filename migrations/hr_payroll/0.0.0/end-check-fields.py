from odoo import modules

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("16.0", "saas~18.4"):
        cr.execute(
            r"""
            WITH expected_fields AS (
                SELECT CONCAT_WS(
                           '_',
                           'x_l10n',
                           COALESCE(LOWER(c.code), 'xx'),
                           LOWER(REGEXP_REPLACE(r.code, '[-\. ]', '_', 'g'))
                       ) AS name
                  FROM hr_salary_rule r
                  JOIN hr_payroll_structure s
                    ON r.struct_id = s.id
             LEFT JOIN res_country c
                    ON s.country_id = c.id
                 WHERE r.appears_on_payroll_report
            )
            SELECT f.name,
                   d.module,
                   d.name
              FROM ir_model_fields f
         LEFT JOIN expected_fields ef
                ON ef.name = f.name
         LEFT JOIN ir_model_data d
                ON d.res_id = f.id
               AND d.model = 'ir.model.fields'
             WHERE f.model = 'hr.payroll.report'
               AND f.name ~ 'x_l10n_[a-z]{2}_\w+'
               AND ef IS NULL
               AND (  d.id IS NULL
                   OR d.module IN %s)
            """,
            [tuple(modules.get_modules())],
        )
        if cr.rowcount:
            util._logger.warning(
                "Unexpected salary rule field(s) in hr.payroll.report: %s. "
                "If the linked salary rule was removed during the upgrade consider using `util.hr_payroll.remove_salary_rule`",
                [r[0] for r in cr.fetchall()],
            )
