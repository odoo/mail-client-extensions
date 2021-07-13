# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "project_project_project_tags_rel", "project_project", "project_tags")
    util.create_column(cr, "project_project", "stage_id", "int4")
