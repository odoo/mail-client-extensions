# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "company_details", "text")
    util.create_column(cr, "res_company", "layout_background", "character varying", default="Blank")
    cr.execute("UPDATE ir_model_data SET noupdate = True WHERE model = 'res.currency' AND module = 'base'")

    def curmap(f, t):
        a, b = util.ref(cr, f"base.{f}"), util.ref(cr, f"base.{t}")
        if a and b:
            util.if_unchanged(cr, f"base.rate{f}", util.remove_record)
            return {a: b}
        if a:
            util.rename_xmlid(cr, f"base.{f}", f"base.{t}")
            util.rename_xmlid(cr, f"base.rate{f}", f"base.rate{t}")
        return {}

    currency_mapping = {**curmap("QTQ", "GTQ"), **curmap("UAG", "UAH")}
    if currency_mapping:
        util.replace_record_references_batch(cr, currency_mapping, "res.currency", replace_xmlid=False)

    # Remove the currency
    currencies = ["CYP", "ECS", "ZRZ", "ITL", "RUR", "PLZ", "SKK", "YUM", "QTQ", "UAG"]
    for currency in currencies:
        if not util.delete_unused(cr, f"base.{currency}"):
            util.force_noupdate(cr, f"base.rate{currency}")

    util.create_column(cr, "ir_mail_server", "from_filter", "varchar")
    util.create_column(cr, "ir_mail_server", "smtp_authentication", "varchar", default="login")
    util.create_column(cr, "ir_mail_server", "smtp_ssl_certificate", "bytea")
    util.create_column(cr, "ir_mail_server", "smtp_ssl_private_key", "bytea")
    util.rename_xmlid(cr, "mail.icp_mail_catchall_alias", "base.icp_mail_catchall_alias")
    util.rename_xmlid(cr, "mail.icp_mail_bounce_alias", "base.icp_mail_bounce_alias")

    # We moved the states from l10n_ec to base for Ecuador
    for i in range(1, 25):
        util.rename_xmlid(cr, f"l10n_ec.state_ec_{i}", f"base.state_ec_{i:02}")
