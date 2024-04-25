from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "res.company", "auto_validation", "auto_validation_old")
    util.create_column(cr, "res_company", "auto_validation", "boolean", default=False)
    cr.execute("UPDATE res_company SET auto_validation=TRUE WHERE auto_validation_old='validated'")
    util.remove_field(cr, "res.company", "auto_validation_old")
    util.remove_field(cr, "res.config.settings", "auto_validation")

    util.remove_column(cr, "res_config_settings", "rule_type")
    util.remove_column(cr, "res_config_settings", "applicable_on")
    util.remove_column(cr, "res_config_settings", "rules_company_id")
    util.remove_column(cr, "res_config_settings", "warehouse_id")
