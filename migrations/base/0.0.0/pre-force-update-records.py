# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "base.group_system", noupdate=False)

    if util.version_gte("saas~12.4") and not util.version_gte("saas~14.2"):
        # `website` module adds a new field `website_form_key` on `ir.model` model.
        # This field is filled by xml data in the related `website_*` modules
        # Force the xmlids of models to be updatable -- opw-2439728
        #
        # This query is executed in multiple versions (0.0.0 script) to handle
        # databases upgraded to >=saas~12.4 before 21 Jan 2021 -- opw-2706498

        cr.execute(
            """
            UPDATE ir_model_data
               SET noupdate = FALSE
             WHERE model = 'ir.model'
               AND CONCAT(module, '.', name) IN (
                    'crm.model_crm_lead',                 -- website_crm
                    'mail.model_mail_mail',               -- website_form
                    'project.model_project_task',         -- website_form_project
                    'hr_recruitment.model_hr_applicant',  -- website_hr_recruitment
                    'base.model_res_partner',             -- website_sale
                    'helpdesk.model_helpdesk_ticket'      -- website_helpdesk (enterprise)
               )
            """
        )
