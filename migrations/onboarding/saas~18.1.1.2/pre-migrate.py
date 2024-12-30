from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(cr, "onboarding_progress", "onboarding_progress_onboarding_company_uniq", warn=False)
