# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Onboardings refactoring
    util.remove_view(cr, "base.onboarding_container")
    util.remove_view(cr, "base.onboarding_company_step")
    util.remove_view(cr, "base.base_onboarding_company_form")

    util.remove_record(cr, "base.action_open_base_onboarding_company")
    util.remove_record(cr, "base.onboarding_step")
