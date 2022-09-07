# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_sale_subscription.project_project_view_form")
