# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Remove recurrence from subtasks
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """ UPDATE project_task pt
                   SET recurrence_id = NULL
                 WHERE parent_id IS NOT NULL
            """,
            table="project_task",
            alias="pt",
        ),
    )
    util.change_field_selection_values(cr, "project.task", "recurrence_update", {"subsequent": "future"})

    fields_to_remove_per_model_name = {
        "project.task": [
            "partner_is_company",
            "manager_id",
            "email_from",
            "ancestor_id",
            "partner_email",
            "project_analytic_account_id",
            "is_analytic_account_id_changed",
        ],
        "project.project": ["partner_email", "partner_phone"],
    }
    for model_name, fields in fields_to_remove_per_model_name.items():
        for field in fields:
            util.remove_field(cr, model_name, field)
