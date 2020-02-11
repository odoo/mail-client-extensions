# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Remove fields linked to _inherit of sms.template removal
    util.remove_field(cr, "sms.template.preview", "name")
    util.remove_field(cr, "sms.template.preview", "model")
    util.remove_field(cr, "sms.template.preview", "sidebar_action_id")
    # Remove fields linked to sms.template.preview code cleaning
    util.remove_field(cr, "sms.template.preview", "res_id")
    # Remove column linked to _inherit of sms.template removal, now a computed field
    util.remove_column(cr, "sms_template_preview", "body")
