# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('project.{,portal_}my_project'))
    util.rename_xmlid(cr, *eb('project.{,portal_}my_tasks'))
    util.rename_xmlid(cr, *eb('project.{,portal_}my_task'))
    util.rename_xmlid(cr, *eb('project.{portal_project_rule,project_project_rule_portal}'))
    util.rename_xmlid(cr, *eb('project.{portal_task_rule,project_task_rule_portal}'))

    util.force_noupdate(cr, "project.edit_project", False)

    # rename to /dev/null
    util.remove_record(cr, 'project.portal_issue_rule')   # from website_project_issue

    views = util.splitlines("""
        analytic_account_inherited_issue_form
        project_project_view_form_simplified_inherit_issue
        view_project_kanban_inherited
        view_project_form_inherited
        res_partner_issues_button_view

        my_issues
        my_issues_issue
    """)
    for view in views:
        util.remove_view(cr, 'project.' + view)
