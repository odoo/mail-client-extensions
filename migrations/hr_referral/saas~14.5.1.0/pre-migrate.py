# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "hr.recruitment.stage", "not_hired_stage", "use_in_referral")
    cr.execute("UPDATE hr_recruitment_stage SET use_in_referral = NOT COALESCE(use_in_referral, false)")

    util.create_m2m(cr, "hr_referral_alert_users_rel", "hr_referral_alert", "res_users", "alert_id", "user_id")

    util.create_column(cr, "hr_referral_reward", "active", "boolean", default=True)
