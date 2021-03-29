# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_model(cr, "crm.lead", "mail_client_extension", "crm_mail_plugin")
    util.rename_xmlid(
        cr, "mail_client_extension.lead_creation_prefilled_action", "crm_mail_plugin.lead_creation_prefilled_action"
    )
