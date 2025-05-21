from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee_skill", "valid_from", "date")
    util.create_column(cr, "hr_employee_skill", "valid_to", "date")
    util.create_column(cr, "hr_skill_type", "levels_count", "integer")
    util.remove_constraint(cr, "hr_employee_skill", "hr_employee_skill__unique_skill", warn=False)
    util.remove_constraint(cr, "hr_employee_skill", "hr_employee_skill_HrEmployeeSkill__unique_skill", warn=False)
    cr.execute(
        """
        DELETE
        FROM hr_employee_skill
        """
    )
    cr.execute(
        """
        WITH
            distinct_employee_skill as (
                SELECT DISTINCT ON (employee_id, skill_id, skill_level_id)
                    employee_id,
                    skill_id,
                    skill_type_id,
                    skill_level_id,
                    date
                FROM hr_employee_skill_log
                ORDER BY employee_id, skill_id, skill_level_id, date ASC
            ),
            lag_date_table as (
                SELECT
                    employee_id,
                    skill_id,
                    skill_level_id,
                    skill_type_id,
                    date,
                    LAG(date) OVER (PARTITION BY employee_id, skill_id ORDER BY date DESC) AS lag_date
                FROM distinct_employee_skill
            ),
            employee_skill_new as (
                SELECT
                    employee_id,
                    skill_id,
                    skill_level_id,
                    skill_type_id,
                    date AS valid_from,
                    CASE
                        WHEN lag_date_table.lag_date IS NOT NULL
                        THEN lag_date_table.lag_date - INTERVAL '1 day'
                        ELSE NULL
                    END AS valid_to
                FROM lag_date_table
            )
        INSERT INTO hr_employee_skill (
            employee_id,
            skill_id,
            skill_level_id,
            skill_type_id,
            valid_from,
            valid_to
        )
        SELECT *
        FROM employee_skill_new
    """
    )
    util.remove_model(cr, "hr.employee.skill.log")
