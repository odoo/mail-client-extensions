# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "project.mail_template_data_module_install_project")
    util.remove_record(cr, "project.mail_template_function_module_install_project")
