# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "portal.my_account_link")
    util.remove_view(cr, "portal.portal_my_home")
    util.if_unchanged(cr, "portal.mail_template_data_portal_welcome", util.update_record_from_xml)

    models = {"portal.mixin", "account.invoice", "project.project",
              "project.task", "purchase.order", "sale.order", "helpdesk.ticket"}
    for model in models:
        util.rename_field(cr, model, "portal_url", "access_url")
