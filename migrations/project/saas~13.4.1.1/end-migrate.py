# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "project_project", "portal_show_rating")
