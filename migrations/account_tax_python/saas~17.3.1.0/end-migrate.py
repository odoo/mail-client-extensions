from odoo.exceptions import ValidationError

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    python_taxes = env["account.tax"].search([("amount_type", "=", "code")])

    errors = []
    for tax in python_taxes:
        try:
            tax._check_amount_type_code_formula()
        except ValidationError:
            errors.append(
                "<li>On {link}, invalid formula: {formula}".format(
                    link=util.get_anchor_link_to_record("account.tax", tax.id, tax.name),
                    formula=util.html_escape(tax.formula),
                )
            )

    if errors:
        util.add_to_migration_reports(
            """
                <details>
                    <summary>
                        During the migration, some taxes having the <code>python</code> type are no longer valid.
                        Therefore, you should check those taxes to reconfigure them.
                        The main differences are the following:
                        First, <code>company</code> and <code>partner</code> are no longer accessible.
                        Then, you still have access to the <code>product</code> but only to the non relational fields (no method).
                        Finally, you still have access to <code>base</code>, <code>price_unit</code>, <code>quantity</code> but
                        also to <code>min</code> and <code>max</code>.
                    </summary>
                    <ul>{}</ul>
                </details>
            """.format("\n".join(errors)),
            category="Taxes",
            format="html",
        )
