# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "hr.recruitment.stage", "not_hired_stage", "use_in_referral")
    cr.execute("UPDATE hr_recruitment_stage SET use_in_referral = NOT COALESCE(use_in_referral, false)")
