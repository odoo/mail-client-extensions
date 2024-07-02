from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "pos_mercury"):
        query = """
        UPDATE pos_payment
           SET ticket = concat_ws(' ', ticket, concat('([Vantiv] card number: ', coalesce(mercury_card_number, 'N/A'),
                                                      ', card brand: ', coalesce(mercury_card_brand, 'N/A'),
                                                      ', owner: ', coalesce(mercury_card_owner_name, 'N/A'),
                                                      ', reference: ', coalesce(mercury_ref_no, 'N/A'),
                                                      ', record: ', coalesce(mercury_record_no, 'N/A'),
                                                      ', invoice: ', coalesce(mercury_invoice_no, 'N/A'), ')'))
         WHERE coalesce(mercury_card_number, '') != ''
        """
        util.explode_execute(cr, query, table="pos_payment")

        util.add_to_migration_reports(
            """
                <p><strong>IMPORTANT NOTICE</strong></p>
                <p>
                    The Worldpay (also went by Vantiv and Mercury) POS integration is no
                    longer supported in this version of Odoo and has been uninstalled.
                    Mercury payment metadata (e.g. Mercury reference number, record
                    number, ...) has been moved to the Ticket field on the payments.

                    See <a href="https://www.odoo.com/documentation/18.0/applications/sales/point_of_sale/payment_methods/terminals.html">
                    our documentation</a> for alternative ways to charge credit cards in
                    the POS.
                </p>
            """,
            category="Point Of Sale",
            format="html",
        )
    util.remove_module(cr, "pos_mercury")
