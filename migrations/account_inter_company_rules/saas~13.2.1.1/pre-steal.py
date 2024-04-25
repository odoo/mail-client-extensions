from odoo.upgrade import util


def migrate(cr, version):
    moved_fields = {
        "account.move": ["auto_generated", "auto_invoice_id"],
        "res.company": ["rule_type", "intercompany_user_id", "intercompany_transaction_message"],
        "res.config.settings": [
            "rule_type",
            "intercompany_user_id",
            "intercompany_transaction_message",
            "rules_company_id",
        ],
    }

    for model in moved_fields:
        for field in moved_fields[model]:
            util.move_field_to_module(
                cr, model, field, "sale_purchase_inter_company_rules", "account_inter_company_rules"
            )

    views = """
        view_company_inter_change_inherit_form
        res_config_settings_view_form
    """
    for view in util.splitlines(views):
        util.rename_xmlid(cr, f"sale_purchase_inter_company_rules.{view}", f"account_inter_company_rules.{view}")

    util.remove_column(cr, "res_config_settings", "intercompany_transaction_message")
