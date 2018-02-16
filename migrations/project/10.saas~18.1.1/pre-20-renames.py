# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('project.{,portal_}my_project'))
    util.rename_xmlid(cr, *eb('project.{,portal_}my_tasks'))
    util.rename_xmlid(cr, *eb('project.{,portal_}my_task'))

    # rename to /dev/null
    util.remove_record(cr, 'project.portal_project_rule')   # from website_project
    util.remove_record(cr, 'project.portal_issue_rule')   # from website_project_issue

    views = util.splitlines("""
        analytic_account_inherited_issue_form
        project_project_view_form_simplified_inherit_issue
        view_project_kanban_inherited
        view_project_form_inherited
        res_partner_issues_button_view
    """)
    for view in views:
        util.remove_view(cr, 'project.' + view)
