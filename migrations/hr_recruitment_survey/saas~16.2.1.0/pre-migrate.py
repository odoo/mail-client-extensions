# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "survey.user_input", "applicant_id", "applicant_ids")
