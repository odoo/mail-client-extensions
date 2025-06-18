from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee_skill", "valid_from", "date")
    util.create_column(cr, "hr_employee_skill", "valid_to", "date")
    util.create_column(cr, "hr_skill_type", "levels_count", "integer")
    util.remove_constraint(cr, "hr_employee_skill", "hr_employee_skill__unique_skill", warn=False)
    util.remove_constraint(cr, "hr_employee_skill", "hr_employee_skill_HrEmployeeSkill__unique_skill", warn=False)
    cr.execute("DELETE FROM hr_employee_skill")
    cr.execute(
        """
        WITH relevant_employee_skill AS (
            SELECT employee_id,
                   skill_id,
                   skill_level_id,
                   skill_type_id,
                   date AS valid_from,
                   skill_level_id IS DISTINCT FROM (LAG(skill_level_id) OVER (PARTITION BY employee_id, skill_id ORDER BY date)) AS is_changed
              FROM hr_employee_skill_log
        )
        INSERT INTO hr_employee_skill (
                    employee_id, skill_id, skill_level_id, skill_type_id, valid_from, valid_to
        )
             SELECT employee_id,
                    skill_id,
                    skill_level_id,
                    skill_type_id,
                    valid_from,
                    LEAD(valid_from) OVER (PARTITION BY employee_id, skill_id ORDER BY valid_from) - INTERVAL '1 day' valid_to
               FROM relevant_employee_skill
              WHERE is_changed
    """
    )
    util.remove_model(cr, "hr.employee.skill.log")
    cr.execute(
        """
        WITH levels AS (
            SELECT skill_type_id AS type_id,
                   count(*) AS total
              FROM hr_skill_level
          GROUP BY skill_type_id
        )
        UPDATE hr_skill_type t
           SET levels_count = levels.total
          FROM levels
         WHERE t.id = levels.type_id
    """
    )
