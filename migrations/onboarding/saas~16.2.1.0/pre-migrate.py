from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Remove extra onboarding progress (step) records without company
    # created for the same onboarding.
    cr.execute(
        """
        DELETE FROM onboarding_progress
              WHERE company_id IS NULL
                AND id NOT IN (
                       SELECT max(id)
                         FROM onboarding_progress
                        WHERE company_id IS NULL
                     GROUP BY onboarding_id
                )
        """
    )
    # Replaced with unique index handling NULL as identical values
    util.remove_constraint(cr, "onboarding_progress", "onboarding_progress_onboarding_company_uniq")
