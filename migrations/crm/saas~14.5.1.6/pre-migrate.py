# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_references(
        cr, "activity_date_deadline_my", "my_activity_date_deadline", only_models=("crm.lead",)
    )
    util.remove_field(cr, "crm.lead", "activity_date_deadline_my")

    util.rename_field(cr, "res.config.settings", "module_crm_iap_lead", "module_crm_iap_mine")
    util.rename_field(cr, "res.config.settings", "module_crm_iap_lead_enrich", "module_crm_iap_enrich")
    util.rename_field(cr, "res.config.settings", "module_crm_iap_lead_website", "module_website_crm_iap_reveal")
