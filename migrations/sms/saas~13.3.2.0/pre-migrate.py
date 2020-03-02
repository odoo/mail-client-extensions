# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Template preview model
    # ----------------------------------------------------------------------
    # Remove fields linked to _inherit of sms.template removal
    util.remove_field(cr, "sms.template.preview", "name")
    util.remove_field(cr, "sms.template.preview", "model")
    util.remove_field(cr, "sms.template.preview", "sidebar_action_id")
    util.remove_field(cr, "sms.template.preview", "copyvalue")
    util.remove_field(cr, "sms.template.preview", "null_value")
    util.remove_field(cr, "sms.template.preview", "sub_model_object_field")
    util.remove_field(cr, "sms.template.preview", "sub_object")
    util.remove_field(cr, "sms.template.preview", "model_object_field")
    # Remove fields linked to sms.template.preview code cleaning
    util.remove_field(cr, "sms.template.preview", "res_id")
    # Remove column linked to _inherit of sms.template removal, now a computed field
    util.remove_column(cr, "sms_template_preview", "body")

    # Composer model
    # ----------------------------------------------------------------------
    util.remove_field(cr, "sms.composer", "partner_ids")
    util.rename_field(cr, "sms.composer", "recipient_count", "recipient_valid_count")
    util.rename_field(cr, "sms.composer", "recipient_description", "recipient_single_description")
    # force view update as it is quite changed
    util.force_noupdate(cr, "sms.sms_composer_view_form", False)
