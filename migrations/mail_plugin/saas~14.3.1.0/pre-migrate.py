# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.move_model(cr, "crm.lead", "mail_plugin", "crm_mail_plugin")
    util.rename_xmlid(cr, *eb("{mail_plugin,crm_mail_plugin}.lead_creation_prefilled_action"))
