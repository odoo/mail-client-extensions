# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_constraint(cr, "survey_user_input", "survey_user_input_deadline_in_the_past")
