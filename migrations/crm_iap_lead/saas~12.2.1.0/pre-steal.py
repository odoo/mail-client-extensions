# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.util import expand_braces as eb


def _(x):
    return x.replace(".", "_") + "_"


def _rename_model(cr, suffix):
    f, t = util.expand_braces("crm.{reveal,iap.lead}." + suffix)
    util.rename_model(cr, f, t)
    util.move_model(cr, t, "crm_iap_lead_website", "crm_iap_lead", move_data=False)
    cr.execute(
        """
        UPDATE ir_model_data
           SET name = replace(name, %s, %s),
               module = 'crm_iap_lead'
         WHERE model = %s
           AND module = 'crm_iap_lead_website'
    """,
        [_(f), _(t), t],
    )

    util.rename_xmlid(cr, *eb("crm_iap_lead.access_crm_{reveal,iap_lead}_" + suffix))


def migrate(cr, version):
    util.rename_xmlid(cr, *eb("crm_iap_lead{_website,}.lead_message_template"))
    util.rename_xmlid(cr, "crm_iap_lead_website.reveal_no_credits", "crm_iap_lead.lead_generation_no_credits")

    util.move_field_to_module(cr, "crm.lead", "reveal_id", *eb("crm_iap_lead{_website,}"))

    _rename_model(cr, "industry")
    _rename_model(cr, "role")
    _rename_model(cr, "seniority")
