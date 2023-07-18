# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Onboardings refactoring
    util.remove_view(cr, "base.onboarding_container")
    util.remove_view(cr, "base.onboarding_company_step")
    util.remove_view(cr, "base.base_onboarding_company_form")

    util.remove_record(cr, "base.action_open_base_onboarding_company")
    util.remove_record(cr, "base.onboarding_step")

    util.rename_xmlid(cr, "base.identity_check_wizard", "base.res_users_identitycheck_view_form")
