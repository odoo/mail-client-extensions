# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.create_m2m(
        cr,
        "account_analytic_tag_project_project_rel",
        "account_analytic_tag",
        "project_project",
        "account_analytic_tag_id",
        "project_project_id",
    )
