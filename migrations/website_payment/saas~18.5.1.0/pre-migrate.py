from odoo.upgrade import util


def migrate(cr, version):
    fields_to_remove = [
        "first_provider_label",
        "is_stripe_supported_country",
        "providers_state",
    ]
    for field in fields_to_remove:
        util.remove_field(cr, "res.config.settings", field)
