# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "hr_recruitment.applicant_hired_template", noupdate=True)
