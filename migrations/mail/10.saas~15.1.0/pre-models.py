# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.module_installed(cr, "web_studio"):
        util.move_field_to_module(cr, "ir.model", "mail_thread", "web_studio", "mail")
        util.rename_field(cr, "ir.model", "mail_thread", "is_mail_thread")
        util.move_field_to_module(cr, "ir.model.fields", "track_visibility", "web_studio", "mail")
        util.rename_xmlid(cr, "web_studio.model_form_view", "mail.model_form_view")
        util.rename_xmlid(cr, "web_studio.model_search_view", "mail.model_search_view")
        util.rename_xmlid(cr, "web_studio.field_form_view", "mail.field_form_view")

    # No need to set values for this column as they will be set by the _reflect_model_params method
    # when models are loaded
    util.create_column(cr, "ir_model", "is_mail_thread", "boolean")

    util.create_column(cr, "res_users", "notification_type", "varchar")
    cr.execute(
        """
        UPDATE res_users u
           SET notification_type = CASE WHEN p.notify_email = 'none' THEN 'inbox' ELSE 'email' END
          FROM res_partner p
         WHERE p.id = u.partner_id
    """
    )
    util.remove_field(cr, "res.partner", "notify_email")
