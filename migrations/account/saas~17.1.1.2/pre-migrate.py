from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.journal", "sale_activity_note")
    util.remove_field(cr, "account.journal", "sale_activity_user_id")
    util.remove_field(cr, "account.journal", "sale_activity_type_id")
    util.remove_field(cr, "res.config.settings", "module_account_taxcloud")
    util.remove_field(cr, "res.config.settings", "module_account_avatax")
    util.remove_field(cr, "analytic.mixin", "analytic_distribution_search")
