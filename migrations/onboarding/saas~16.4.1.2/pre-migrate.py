# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # progress.steps are now linked to company_id and not to the onboarding.progress, see below.
    util.remove_constraint(cr, "onboarding_progress_step", "progress_step_uniq")

    # onboarding_step -> onboarding is now many2many
    util.create_m2m(
        cr,
        "onboarding_onboarding_onboarding_onboarding_step_rel",
        "onboarding_onboarding",
        "onboarding_onboarding_step",
    )
    cr.execute(
        """
       INSERT INTO onboarding_onboarding_onboarding_onboarding_step_rel(onboarding_onboarding_id, onboarding_onboarding_step_id)
            SELECT onboarding_id, id
              FROM onboarding_onboarding_step
        """
    )

    # onboarding_progress_step -> onboarding_progress is now many2many
    util.create_m2m(
        cr, "onboarding_progress_onboarding_progress_step_rel", "onboarding_progress", "onboarding_progress_step"
    )
    util.create_column(cr, "onboarding_progress_step", "company_id", "int4")
    util.create_column(cr, "onboarding_onboarding_step", "is_per_company", "boolean")
    cr.execute(
        """
        UPDATE onboarding_onboarding_step step
           SET is_per_company = panel.is_per_company
          FROM onboarding_onboarding panel
         WHERE step.onboarding_id = panel.id
        """
    )
    cr.execute(
        """
       UPDATE onboarding_progress_step
          SET company_id = onboarding_progress.company_id
         FROM onboarding_progress
        WHERE onboarding_progress_step.progress_id = onboarding_progress.id
        """
    )
    cr.execute(
        """
       INSERT INTO onboarding_progress_onboarding_progress_step_rel(onboarding_progress_id, onboarding_progress_step_id)
            SELECT progress_id, id
              FROM onboarding_progress_step
        """
    )

    util.remove_field(cr, "onboarding.progress.step", "progress_id")
    util.remove_field(cr, "onboarding.progress.step", "onboarding_id")
    util.remove_column(cr, "onboarding_onboarding", "is_per_company")
    util.remove_field(cr, "onboarding.onboarding.step", "onboarding_id")

    util.rename_xmlid(cr, "base.onboarding_step", "onboarding.onboarding_step")
