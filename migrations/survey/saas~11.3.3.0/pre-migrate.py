# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "survey.assets_frontend")
    util.remove_view(cr, "survey.assets_frontend_survey")
    util.remove_view(cr, "survey.assets_frontend_result")
