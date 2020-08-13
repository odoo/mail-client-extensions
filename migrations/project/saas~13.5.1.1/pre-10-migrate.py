# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project.project_view_kanban")
    # The description becomes an HTML field. It was a char previously
    cr.execute(
        """
                  UPDATE project_project
                     SET description = {}
                   WHERE description IS NOT NULL
              """.format(
            util.pg_text2html("description")
        )
    )
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
