from odoo.upgrade import util


def migrate(cr, version):
    # === PAYMENT PROVIDER === #

    util.remove_field(cr, "payment.provider", "paypal_seller_account")
    util.remove_field(cr, "payment.provider", "paypal_use_ipn")

    cr.execute(
        """
           UPDATE payment_provider
              SET state='disabled'
            WHERE paypal_pdt_token IS NULL
              AND code = 'paypal'
        RETURNING id, name->'en_US'
        """
    )

    provider_disabled = cr.fetchall()
    if provider_disabled:
        util.add_to_migration_reports(
            """
                <details>
                <summary>
                    The following paypal provider have been disabled due to missing PDT Identity Token
                </summary>
                <ul>%s</ul>
                </details>
            """
            % "\n".join(
                f"<li>{util.get_anchor_link_to_record('payment.provider', provider_id, name)}</li>"
                for provider_id, name in provider_disabled
            ),
            category="Payment",
            format="html",
        )

    util.remove_view(cr, "payment_paypal.mail_template_paypal_invite_user_to_configure")
