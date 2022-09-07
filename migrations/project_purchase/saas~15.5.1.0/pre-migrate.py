# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_purchase.project_project_form_view_inherited")
