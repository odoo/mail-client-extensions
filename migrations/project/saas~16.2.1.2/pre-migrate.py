# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Remove recurrence from subtasks
    util.explode_execute(
        cr,
        """ UPDATE project_task pt
               SET recurrence_id = NULL
             WHERE parent_id IS NOT NULL
        """,
        table="project_task",
        alias="pt",
    )

    # Delete recurrences without tasks
    cr.execute(
        """
        SELECT r.id
          FROM project_task_recurrence r
         WHERE NOT EXISTS (
                    SELECT 1 FROM project_task t WHERE t.recurrence_id = r.id
              )
        """
    )
    util.remove_records(cr, "project.task.recurrence", [rid for rid, in cr.fetchall()])

    # Remove the cron that creates recurring tasks, as they will now be created when marking the last task as done
    util.remove_record(cr, "project.ir_cron_recurring_tasks")

    # Change repeat n times to repeat until <last_task.create_date + n * rec.repeat_interval [rec.repeat_unit]>
    cr.execute(
        """ WITH rec_to_update AS (
               SELECT r.id,
                      max(t.create_date) + (r.repeat_interval * r.recurrence_left || ' ' || r.repeat_unit)::interval as repeat_until
                 FROM project_task t
                 JOIN project_task_recurrence r
                   ON r.id = t.recurrence_id
                WHERE r.repeat_type = 'after'
             GROUP BY r.id
          )
          UPDATE project_task_recurrence r
             SET repeat_until = u.repeat_until,
                 repeat_type = 'until'
            FROM rec_to_update u
           WHERE u.id = r.id
        """
    )

    # Replace kanban_state field with state field
    util.create_column(cr, "project_task", "state", "character varying")

    query = """
        UPDATE project_task
           SET state = CASE
          WHEN is_blocked IS TRUE then '04_waiting_normal'
          WHEN kanban_state = 'normal' THEN '01_in_progress'
          WHEN kanban_state = 'blocked' THEN '02_changes_requested'
          WHEN kanban_state = 'done' THEN '03_approved'
          ELSE '01_in_progress'
           END
    """

    util.explode_execute(cr, query, table="project_task")

    # rename auto_validation_kanban_state
    util.rename_field(cr, "project.task.type", "auto_validation_kanban_state", "auto_validation_state")

    # remove digest_tip_project_0
    util.remove_record(cr, "project.digest_tip_project_0")

    # rename xmlid for subtypes
    util.rename_xmlid(cr, "project.mt_task_progress", "project.mt_task_in_progress")
    util.rename_xmlid(cr, "project.mt_task_blocked", "project.mt_task_changes_requested")
    util.rename_xmlid(cr, "project.mt_task_ready", "project.mt_task_approved")

    util.rename_xmlid(cr, "project.mt_project_task_progress", "project.mt_project_task_in_progress")
    util.rename_xmlid(cr, "project.mt_project_task_blocked", "project.mt_project_task_changes_requested")
    util.rename_xmlid(cr, "project.mt_project_task_ready", "project.mt_project_task_approved")

    # adapt is_blocked and kanban_state domains
    def state_adapter(leaf, _o, _n):
        _, op, right = leaf
        kanban_to_state_dict = {
            "normal": "01_in_progress",
            "blocked": "02_changes_requested",
            "done": "03_approved",
        }
        if isinstance(right, str):
            right = kanban_to_state_dict.get(right, right)
        elif right:
            right = [kanban_to_state_dict.get(r, r) for r in right]
        return [("state", op, right)]

    def is_blocked_adapter(leaf, _o, _n):
        # here we will consider is_blocked as the inverse of is_closed
        _, op, right = leaf
        new_op = "!=" if bool(right) else "="
        return [("is_closed", new_op, right)]

    util.adapt_domains(cr, "project.task", "kanban_state", "state", adapter=state_adapter)
    util.adapt_domains(cr, "project.task", "is_blocked", "is_closed", adapter=is_blocked_adapter)

    util.update_record_from_xml(cr, "project.project_manager_all_project_tasks_rule")

    recurrence_fields = [
        "sun",
        "sat",
        "fri",
        "thu",
        "wed",
        "tue",
        "mon",
        "repeat_month",
        "repeat_weekday",
        "repeat_week",
        "repeat_day",
        "repeat_on_year",
        "repeat_on_month",
        "repeat_number",
    ]
    fields_to_remove_per_model_name = {
        "project.task": [
            *recurrence_fields,
            "partner_is_company",
            "manager_id",
            "email_from",
            "ancestor_id",
            "partner_email",
            "project_analytic_account_id",
            "is_analytic_account_id_changed",
            "kanban_state",
            "is_blocked",
            "kanban_state_label",
            "legend_done",
            "legend_blocked",
            "legend_normal",
            "repeat_show_month",
            "repeat_show_week",
            "repeat_show_day",
            "repeat_show_dow",
            "recurrence_message",
            "recurrence_update",
        ],
        "project.task.type": [
            "legend_done",
            "legend_blocked",
            "legend_normal",
        ],
        "report.project.task.user": [
            "kanban_state",
            "is_blocked",
        ],
        "project.project": ["partner_email", "partner_phone"],
        "project.task.recurrence": [
            *recurrence_fields,
            "recurrence_left",
            "next_recurrence_date",
        ],
    }
    for model_name, fields in fields_to_remove_per_model_name.items():
        for field in fields:
            util.remove_field(cr, model_name, field)

    util.update_record_from_xml(cr, "project.project_task_recurrence_1")
    util.update_record_from_xml(cr, "project.project_task_recurrence_2")
