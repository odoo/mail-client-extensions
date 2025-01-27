from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.appraisal", "meeting_ids")
    util.remove_field(cr, "hr.appraisal", "meeting_count_display")
    util.remove_field(cr, "hr.appraisal", "date_final_interview")

    query = "UPDATE hr_appraisal SET active = false WHERE active AND state = 'cancel'"
    util.explode_execute(cr, query, table="hr_appraisal")

    def adapter(leaf, _or, _neg):
        left, op, right = leaf
        prefix, _, _ = left.rpartition(".")
        if prefix:
            prefix += "."
        is_neg = op in [
            "not any",
            "not in",
            "not like",
            "not ilike",
            "not =like",
            "not =ilike",
            "!=",
            "<>",
        ]  # All NEGATIVE_CONDITION_OPERATORS
        to_check = [right] if isinstance(right, str) else right
        if "cancel" not in to_check:
            return [leaf]
        return ["&", leaf, (f"{prefix}active", "=", not is_neg)]

    util.adapt_domains(cr, "hr.appraisal", "state", "state", adapter=adapter)

    util.change_field_selection_values(
        cr, "hr.appraisal", "state", {"new": "1_new", "pending": "2_pending", "done": "3_done", "cancel": "1_new"}
    )

    util.rename_field(cr, "hr.departure.wizard", "cancel_appraisal", "delete_appraisal")
    util.create_m2m(cr, "hr_appraisal_goal_hr_employee_rel", "hr_appraisal_goal", "hr_employee")
    # fill the many2many field with the employee_id first
    cr.execute("""
        INSERT INTO hr_appraisal_goal_hr_employee_rel (hr_appraisal_goal_id, hr_employee_id)
        SELECT id, employee_id
          FROM hr_appraisal_goal
         WHERE employee_id IS NOT NULL
    """)
    # remove employee_id by renaming it to update the domains and then drop the col
    util.rename_field(cr, "hr.appraisal.goal", "employee_id", "employee_ids")
    util.remove_column(cr, "hr_appraisal_goal", "employee_ids")

    util.create_m2m(cr, "hr_appraisal_goal_hr_employee_manager_rel", "hr_appraisal_goal", "hr_employee")
    # fill the many2many field with the manager_id first
    cr.execute("""
        INSERT INTO hr_appraisal_goal_hr_employee_manager_rel (hr_appraisal_goal_id, hr_employee_id)
        SELECT id, manager_id
          FROM hr_appraisal_goal
         WHERE manager_id IS NOT NULL
    """)
    # remove manager_id by renaming it to update the domains and then drop the col
    util.rename_field(cr, "hr.appraisal.goal", "manager_id", "manager_ids")
    util.remove_column(cr, "hr_appraisal_goal", "manager_ids")
    util.remove_field(cr, "hr.appraisal.goal", "manager_user_id")
