from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "account_invoice_extract") and util.table_exists(cr, "account_invoice_extract_words"):
        # Steal the model/fields from account_invoice_extract to move them in iap_extract
        util.move_model(cr, "account.invoice_extract.words", "account_invoice_extract", "iap_extract")
        util.rename_model(cr, "account.invoice_extract.words", "iap.extracted.words")

        # And generify it by adding a res_model and res_id (instead of invoice_id)
        util.create_column(cr, "iap_extracted_words", "res_model", "varchar")
        util.create_column(cr, "iap_extracted_words", "res_id", "int4")
        query = """
            UPDATE iap_extracted_words w
               SET res_model = 'account.move',
                   res_id = w.invoice_id
        """
        util.explode_execute(cr, query, table="iap_extracted_words", alias="w")
        util.remove_field(cr, "iap.extracted.words", "invoice_id")
        util.rename_xmlid(
            cr, "account_invoice_extract.access_account_invoice_extract_words", "iap_extract.access_iap_extracted_words"
        )
