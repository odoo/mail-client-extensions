from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.create_column(cr, "project_milestone", "sequence", "integer", default=10)
    util.remove_view(cr, "project.project_sharing_portal")
    util.rename_xmlid(cr, *eb("project.project_sharing_{embed,portal}"))
    util.remove_view(cr, "project.project_sharing")

    is_industry_fsm_installed = util.module_installed(cr, "industry_fsm")
    is_website_project_installed = util.module_installed(cr, "website_project")
    if is_industry_fsm_installed:
        util.move_field_to_module(cr, "project.task", "partner_phone", "industry_fsm", "project")
    if is_website_project_installed:
        util.move_field_to_module(cr, "project.task", "partner_phone", "website_project", "project")
    if not (is_industry_fsm_installed or is_website_project_installed):
        util.create_column(cr, "project_task", "partner_phone", "varchar")
        util.explode_execute(
            cr,
            """
            UPDATE project_task t
               SET partner_phone = COALESCE(p.mobile, p.phone)
              FROM res_partner p
             WHERE t.partner_id = p.id
            """,
            table="project_task",
            alias="t",
        )
    util.remove_field(cr, "project.task", "show_display_in_project")
    util.explode_execute(
        cr,
        """
        UPDATE project_task t
           SET display_in_project = False
          FROM project_task parent
         WHERE parent.id = t.parent_id
           AND t.display_in_project IS TRUE
           AND t.project_id = parent.project_id
        """,
        table="project_task",
        alias="t",
    )
