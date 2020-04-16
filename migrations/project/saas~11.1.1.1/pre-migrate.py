# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'res.config.settings', 'module_rating_project')
    util.remove_record(cr, 'project.action_project_task_user_tree_filtered')

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('project.{,rating_}index'), noupdate=False)

    views = util.splitlines("""
        # rating templates
        project_data_satisfaction
        project_rating_page
        project_rating_data

        # inherited task views
        project_task_view_form_inherit_rating
        project_task_view_search
        project_task_view_kanban_inherit_rating

        view_project_project_rating_form
        view_project_project_rating_kanban

        view_project_task_type_rating_form
    """)
    for view in views:
        util.remove_view(cr, 'project.' + view)
