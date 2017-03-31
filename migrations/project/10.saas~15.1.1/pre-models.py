# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.move_field_to_module(cr, 'project.config.settings', 'module_project_timesheet_synchro',
                              'hr_timesheet_sheet', 'project')
    util.remove_field(cr, 'project.config.settings', 'project_time_mode_id')
    util.remove_field(cr, 'project.config.settings', 'module_pad')
    util.remove_field(cr, 'project.config.settings', 'module_rating_project')

    util.remove_view(cr, 'project.view_config_settings')

    util.rename_xmlid(cr, 'project.action_config_settings',
                      'project.project_config_settings_action')
    util.rename_xmlid(cr, 'project.menu_project_general_settings',
                      'project.project_config_settings_menu_action')
