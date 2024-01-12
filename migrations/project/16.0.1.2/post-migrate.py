# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # https://github.com/odoo/odoo/pull/101006
    util.if_unchanged(cr, "project.burndown_chart_project_user_rule", util.update_record_from_xml)
