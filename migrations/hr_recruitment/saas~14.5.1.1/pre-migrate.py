# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_recruitment_stage", "hired_stage", "boolean")
