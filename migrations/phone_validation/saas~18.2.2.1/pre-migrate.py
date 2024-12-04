from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "sms"):
        util.rename_xmlid(cr, "sms.res_partner_view_search", "phone_validation.res_partner_view_search")
        for fname in (
            "phone_sanitized",
            "phone_sanitized_blacklisted",
            "phone_blacklisted",
            "mobile_blacklisted",
            "phone_mobile_search",
        ):
            util.move_field_to_module(cr, "res.partner", fname, "sms", "phone_validation")
    else:
        util.create_column(cr, "res_partner", "phone_sanitized", "varchar")

    util.remove_field(cr, "mail.thread.phone", "mobile_blacklisted")
