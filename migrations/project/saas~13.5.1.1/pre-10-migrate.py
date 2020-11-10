# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # The description becomes an HTML field. It was a char previously
    description_html = util.pg_text2html("description")
    cr.execute(f"UPDATE project_project SET description = {description_html} WHERE description IS NOT NULL")

    util.create_column(cr, "project_project", "allow_recurring_tasks", "boolean", default=False)
    util.create_column(cr, "project_project", "partner_email", "varchar")
    util.create_column(cr, "project_project", "partner_phone", "varchar")
    cr.execute(
        """
            UPDATE project_project
               SET partner_phone = rp.phone,
                   partner_email = rp.email
              FROM res_partner rp
             WHERE rp.id = project_project.partner_id
        """
    )

    util.create_column(cr, "project_task", "recurring_task", "boolean", default=False)
    util.create_column(cr, "project_task", "recurrence_id", "int4")

    # Data
    util.remove_view(cr, "project.project_view_kanban")
