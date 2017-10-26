# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'website_rating_project.edit_project_inherit_website_rating_project_issue')
    util.rename_field(cr, 'project.project', 'website_published', 'portal_show_rating')
