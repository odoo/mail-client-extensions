# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import models

from odoo.upgrade import util


class Partner(models.Model):
    _inherit = "res.partner"
    _module = "base"

    def _prepare_display_address(self, without_company=False):
        address_format, args = super()._prepare_display_address(without_company=without_company)
        if self.env.context.get("upgrade_ignore_unknown_keys"):
            args = defaultdict(str, args)
        return address_format, args


def migrate(cr, version):
    util.create_column(cr, "res_company", "company_details", "text")
    util.create_column(cr, "res_company", "layout_background", "character varying", default="Blank")
    cr.execute("UPDATE ir_model_data SET noupdate = True WHERE model = 'res.currency' AND module = 'base'")

    def curmap(f, t):
        a, b = util.ref(cr, f"base.{f}"), util.ref(cr, f"base.{t}")
        if a and b:
            util.remove_record(cr, f"base.rate{f}")
            return {a: b}
        if a:
            util.rename_xmlid(cr, f"base.{f}", f"base.{t}")
            util.rename_xmlid(cr, f"base.rate{f}", f"base.rate{t}")
        return {}

    currency_mapping = {**curmap("QTQ", "GTQ"), **curmap("UAG", "UAH")}
    if currency_mapping:
        if util.module_installed(cr, "account"):
            # adjust amount_currency when currency_id and company_currency_id point to different definitions of the same currency
            # and the outdated one is going to be replaced by the newer one (resulting in currency_id = company_currency_id)
            for k, v in currency_mapping.items():
                query = cr.mogrify(
                    """
                    UPDATE account_move_line
                       SET amount_currency = balance
                     WHERE amount_currency != balance
                       AND currency_id IN %s
                       AND company_currency_id IN %s
                       AND currency_id != company_currency_id
                    """,
                    [(k, v), (k, v)],
                ).decode()
                util.explode_execute(cr, query, table="account_move_line")
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
