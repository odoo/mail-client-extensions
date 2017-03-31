# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'project.config.settings', 'module_project_issue_sheet')
    util.remove_field(cr, 'project.config.settings', 'module_rating_project_issue')
    util.force_noupdate(cr, 'project_issue.project_config_settings_view_form_inherit_project_issue', False)
