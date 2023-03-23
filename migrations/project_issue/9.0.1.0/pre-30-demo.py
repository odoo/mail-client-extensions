# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("project_issue.project_issue_{category_01,tags_00}"))
    util.rename_xmlid(cr, *eb("project_issue.project_issue_{category_02,tags_01}"))
    util.rename_xmlid(cr, *eb("project_issue.project_issue_{category_03,tags_02}"))
