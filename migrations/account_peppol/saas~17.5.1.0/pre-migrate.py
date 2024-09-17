from odoo.upgrade import util


def migrate(cr, version):
    def adapter(leaf, _or, _neg):
        # (..., '=', True) => (..., '=', 'valid')
        # (..., '=', False) => (..., '!=', 'valid')
        # (..., '!=', True) => (..., '!=', 'valid')
        # (..., '!=', False) => (..., '=', 'valid')
        left, op, right = leaf
        if (op, bool(right)) in [("=", False), ("!=", True)]:
            op = "!="
        return [(left, op, "valid")]

    for field in ("account_peppol_validity_last_check", "account_peppol_verification_label"):
        util.remove_field(cr, "res.partner", field)

    util.rename_field(
        cr, "res.partner", "account_peppol_is_endpoint_valid", "peppol_verification_state", domain_adapter=adapter
    )
    util.alter_column_type(
        cr,
        "res_partner",
        "peppol_verification_state",
        "varchar",
        using="CASE {0} WHEN true THEN 'valid' ELSE 'not_verified' END",
    )
    util.make_field_company_dependent(
        cr, "res.partner", "peppol_verification_state", "selection", default_value="not_verified"
    )

    util.remove_view(cr, "account_peppol.res_partner_view_tree")
