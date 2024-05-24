from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "account_invoice_extract.account_invoice_extract_no_credit",
        "iap_extract.iap_extract_no_credit",
        noupdate=False,
    )
    # Update template_fs otherwise mail/16.0.1.10/end-migrate.py won't set it correctly
    cr.execute(
        """
        UPDATE mail_template
           SET template_fs = 'iap_extract/data/mail_template_data.xml'
         WHERE id = %s
           AND template_fs = 'account_invoice_extract/data/mail_template_data.xml'
        """,
        [util.ref(cr, "iap_extract.iap_extract_no_credit")],
    )
