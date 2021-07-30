# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Template preview model
    # ----------------------------------------------------------------------
    # Remove fields linked to _inherit of sms.template removal
    util.remove_inherit_from_model(cr, "sms.template.preview", "sms.template", keep=("lang", "model_id", "body"))
    # Remove column linked to _inherit of sms.template removal, now a computed field
    util.remove_column(cr, "sms_template_preview", "body")
    # Remove fields linked to sms.template.preview code cleaning
    util.remove_field(cr, "sms.template.preview", "res_id")

    # Composer model
    # ----------------------------------------------------------------------
    util.remove_field(cr, "sms.composer", "partner_ids")
    util.rename_field(cr, "sms.composer", "recipient_count", "recipient_valid_count")
    util.rename_field(cr, "sms.composer", "recipient_description", "recipient_single_description")
    util.create_column(cr, "sms_composer", "recipient_single_number_itf", "varchar")
    # force view update as it is quite changed
    util.force_noupdate(cr, "sms.sms_composer_view_form", False)
