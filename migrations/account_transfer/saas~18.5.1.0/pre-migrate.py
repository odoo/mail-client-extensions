from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.transfer.model.line", "analytic_account_ids")
    util.remove_field(cr, "account.transfer.model.line", "partner_ids")
    util.remove_field(cr, "account.transfer.model.line", "percent_is_readonly")
    util.rename_xmlid(cr, *util.expand_braces("account_transfer.account_{auto_,}transfer_rule"))
