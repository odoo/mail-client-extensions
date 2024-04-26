from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "hr_employee_planning_role_rel", "hr_employee", "planning_role")
    cr.execute(
        """
        INSERT INTO hr_employee_planning_role_rel(hr_employee_id, planning_role_id)
             SELECT id, planning_role_id
               FROM hr_employee
              WHERE planning_role_id IS NOT NULL
    """
    )
    util.update_field_usage(cr, "hr.employee", "planning_role_id", "planning_role_ids")
    util.remove_field(cr, "hr.employee", "planning_role_id")

    util.create_column(cr, "planning_slot", "department_id", "integer")
    util.create_column(cr, "planning_slot", "access_token", "varchar")
    util.create_column(cr, "planning_slot", "template_id", "integer")
    util.remove_field(cr, "planning.slot", "template_creation")
    cr.execute(
        """
        UPDATE planning_slot s
           SET department_id = e.department_id
          FROM hr_employee e
         WHERE e.id = s.employee_id
    """
    )
    cr.execute(
        """
        UPDATE planning_slot
           SET access_token = md5(CONCAT(id, '/', clock_timestamp()))::uuid::varchar
         WHERE access_token IS NULL
    """
    )

    util.create_column(cr, "planning_role", "sequence", "integer")
    cr.execute("UPDATE planning_role SET sequence = id")

    util.remove_constraint(cr, "planning_planning", "planning_planning_check_start_date_lower_stop_date")
    util.remove_field(cr, "planning.planning", "last_sent_date")
    util.create_m2m(cr, "planning_planning_planning_slot_rel", "planning_planning", "planning_slot")
    cr.execute(
        """
        SELECT p.id, s.id
          FROM planning_planning p, planning_slot s
         WHERE p.company_id = s.company_id
           AND s.start_datetime <= p.end_datetime
           AND s.end_datetime > p.start_datetime
           AND (p.include_unassigned
                OR
                s.employee_id IS NOT NULL)
    """
    )

    util.create_column(cr, "planning_slot_template", "company_id", "integer")

    # wizard
    util.remove_constraint(cr, "planning_send", "planning_send_check_start_date_lower_stop_date")
    util.remove_field(cr, "planning.send", "company_id")
    util.create_m2m(cr, "hr_employee_planning_send_rel", "hr_employee", "planning_send")
    util.create_m2m(cr, "planing_send_planing_slot", "planning_send", "planning_slot")

    # data
    util.remove_view(cr, "planning.planning_view_form_quickcreate")
