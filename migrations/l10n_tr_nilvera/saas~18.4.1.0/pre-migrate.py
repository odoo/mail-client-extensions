from odoo.upgrade import util


def migrate(cr, version):
    def bool_adapter(leaf, _or, _neg):
        left, op, right = leaf
        if isinstance(right, str):
            right = right == "sandbox"
        elif isinstance(right, list):
            right = [val == "sandbox" for val in right]
        return [(left, op, right)]

    util.alter_column_type(cr, "res_company", "l10n_tr_nilvera_environment", "bool", using="{0} = 'sandbox'")
    util.rename_field(
        cr, "res.company", "l10n_tr_nilvera_environment", "l10n_tr_nilvera_use_test_env", domain_adapter=bool_adapter
    )
    util.rename_field(
        cr,
        "res.config.settings",
        "l10n_tr_nilvera_environment",
        "l10n_tr_nilvera_use_test_env",
        domain_adapter=bool_adapter,
    )
