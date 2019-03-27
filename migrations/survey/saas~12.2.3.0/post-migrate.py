# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "survey.mail_template_user_input_invite", False)
    util.recompute_fields(cr, "survey.user_input", ["quizz_passed"])
