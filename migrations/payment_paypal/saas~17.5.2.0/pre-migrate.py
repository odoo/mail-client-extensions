from odoo.upgrade import util


def migrate(cr, version):
    # === PAYMENT PROVIDER === #

    util.remove_field(cr, "payment.provider", "paypal_pdt_token")

    cr.execute(
        """
        UPDATE payment_provider pp
           SET redirect_form_view_id = NULL,
               state='disabled'
         WHERE code = 'paypal'
        RETURNING pp.id,
                  pp.name
        """,
    )
    provider_disabled = cr.fetchall()
    if provider_disabled:
        util.add_to_migration_reports(
            message=f"""
                <details>
                    <summary>
                        Odoo updated to a new version of PayPal, you will need to update your configuration according to the documentation available at <a href="https://www.odoo.com/documentation/18.0/applications/finance/payment_providers/paypal.html">https://www.odoo.com/documentation/18.0/applications/finance/payment_providers/paypal.html</a><br>
                        The following payment providers have been disabled:
                    </summary>
                <ul>
                    {
                "".join(
                    f"<li>{util.get_anchor_link_to_record('payment.provider', provider_id, name)}</li>"
                    for provider_id, name in provider_disabled
                )
            }
                </ul>
                </details>
            """,
            category="Payment",
            format="html",
        )

    util.remove_view(cr, "payment_paypal.redirect_form")
