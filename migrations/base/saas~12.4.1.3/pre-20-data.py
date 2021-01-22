# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("base.state_mx_q{ ,_}roo"))

    cr.execute(
        "UPDATE res_lang SET date_format='%%Y-%%m-%%d' WHERE date_format='%%Y.%%m.%%d' AND id=%s",
        [util.ref(cr, "base.lang_lt")],
    )

    currencies = {"ZWD": "ZWL", "ZMK": "ZMW", "TMM": "TMT", "SRG": "SRD"}
    for old, new in currencies.items():
        cid = util.rename_xmlid(cr, "base." + old, "base." + new)
        if cid:
            cr.execute("UPDATE res_currency SET name = %s WHERE id = %s", [new, cid])

    # Force a more logical FK on currency rate as it will be the case in the future: odoo/odoo#46468
    # This will allow `delete_unused` to correctly remove `SDD` if not used.
    cr.execute(
        """
        ALTER TABLE res_currency_rate
        DROP CONSTRAINT IF EXISTS res_currency_rate_currency_id_fkey,
        ADD FOREIGN KEY (currency_id) REFERENCES res_currency(id) ON DELETE CASCADE
    """
    )
    util.delete_unused(cr, "base.SDD")

    cr.execute("UPDATE ir_ui_view SET field_parent = NULL WHERE id = %s", [util.ref(cr, "base.view_company_tree")])

    # `website` module adds a new field `website_form_key` on `ir.model` model.
    # This field is filled by xml data in the related `website_*` modules
    # Force the xmlids of models to be updatable -- opw-2439728
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
