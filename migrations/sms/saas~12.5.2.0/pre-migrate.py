# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "ir_act_server", "sms_template_id", "int4")
    util.create_column(cr, "ir_act_server", "sms_mass_keep_log", "boolean")
    cr.execute("UPDATE ir_act_server SET sms_mass_keep_log=true")

    util.create_column(cr, "mail_message_res_partner_needaction_rel", "sms_id", "int4")
    util.create_column(cr, "mail_message_res_partner_needaction_rel", "sms_number", "varchar")

    util.remove_view(cr, "sms.partner_form_send_sms_form_view")

    util.remove_model(cr, "sms.send_sms")

    util.create_column(cr, "res_partner", "phone_sanitized", "varchar")
