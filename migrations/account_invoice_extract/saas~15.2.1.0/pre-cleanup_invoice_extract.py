def migrate(cr, version):
    cr.execute("DELETE FROM account_invoice_extract_words WHERE invoice_id IS NULL")
