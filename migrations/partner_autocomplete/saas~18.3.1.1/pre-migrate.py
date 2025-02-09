from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.partner", "partner_gid")
    util.remove_field(cr, "res.partner", "additional_info")
    util.remove_field(cr, "res.company", "partner_gid")
    util.remove_record(cr, "partner_autocomplete.ir_cron_partner_autocomplete")
    util.remove_record(cr, "partner_autocomplete.view_res_partner_form_inherit_partner_autocomplete")
    util.remove_record(cr, "partner_autocomplete.view_partner_simple_form_inherit_partner_autocomplete")
    util.remove_model(cr, "res.partner.autocomplete.sync")
