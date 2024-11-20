from odoo.upgrade import util


def migrate(cr, version):
    view = util.ref(cr, "payment_worldline.redirect_form")

    cr.execute(
        """
            UPDATE payment_provider
               SET state = 'disabled',
                   redirect_form_view_id = %s
             WHERE code = 'ogone'
               AND state = 'enabled'
         RETURNING id, name->>'en_US'
        """,
        [view],
    )
    if cr.rowcount:
        li = "".join(
            f"<li>{util.get_anchor_link_to_record('payment.provider', rid, name)}</li>" for rid, name in cr.fetchall()
        )
        summary = """
            The module 'Payment Provider: Ogone' has been removed, as Ogone is replaced by Worldline.<br/>
            Your existing Ogone payment providers have been changed to use Worldline instead.<br/>
            Your credentials and existing tokens were preserved and should still be working.<br/>
            You should still reconfigure a new webhook as its URL has changed.<br/>
            The providers have been disabled so you could ensure everything is still working as expected.<br/>
        """
        util.add_to_migration_reports(
            f"""
                <details>
                  <summary>{summary}</summary>
                  <ul>{li}</ul>
                </details>
            """,
            category="Payments",
            format="html",
        )
