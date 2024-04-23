from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("saas~12.3", "18.0") and util.column_exists(
        cr, "res_company", "sale_onboarding_sample_quotation_state"
    ):
        cr.execute(
            """
            UPDATE res_company c
               SET sale_onboarding_sample_quotation_state = CASE sale_onboarding_sample_quotation_state
                                                                WHEN 'true' THEN 'just_done'
                                                                ELSE 'not_done'
                                                                END
             WHERE sale_onboarding_sample_quotation_state IN ('true', 'false')
            """
        )
