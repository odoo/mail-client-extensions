from odoo.upgrade import util


def migrate(cr, version):
    # computed stored field from `l10n_ro_efactura`; don't recompute it
    util.create_column(cr, "account_move", "l10n_ro_edi_state", "varchar")
    util.remove_field(cr, "account.move.send", "l10n_ro_edi_warnings")

    # change selection values of romanian move and document's state from:
    # "invoice_sending" -> "invoice_sent"
    # "invoice_sent" -> "invoice_validated"
    # the update order must be done starting from sent->validated, and sending->sent after
    util.change_field_selection_values(
        cr,
        "account.move",
        "l10n_ro_edi_state",
        {"invoice_sent": "invoice_validated", "invoice_sending": "invoice_sent"},
    )
    util.change_field_selection_values(
        cr,
        "l10n_ro_edi.document",
        "state",
        {"invoice_sent": "invoice_validated", "invoice_sending": "invoice_sent"},
    )

    if util.module_installed(cr, "l10n_ro_efactura_synchronize"):
        # `l10n_ro_edi_index` already exists thanks to `l10n_ro_efactura_synchronize`
        util.move_field_to_module(
            cr, "account.move", "l10n_ro_edi_index", "l10n_ro_efactura_synchronize", "l10n_ro_edi"
        )

    elif util.table_exists(cr, "l10n_ro_edi_document"):
        # 'l10n_ro_edi.document' model was in module 'l10n_ro_efactura' that is
        # merged with 'l10n_ro_edi' in saas~17.4, 'l10n_ro_efactura' may be uninstalled
        # set account_move.l10n_ro_edi_index to the first found related document with key_loading information
        util.create_column(cr, "account_move", "l10n_ro_edi_index", "varchar")
        cr.execute("""
            WITH document_with_index AS (
                SELECT DISTINCT ON (invoice_id)
                       invoice_id,
                       key_loading
                  FROM l10n_ro_edi_document
                 WHERE key_loading IS NOT NULL
              ORDER BY invoice_id,
                       datetime DESC,
                       id DESC
            )
            UPDATE account_move move
               SET l10n_ro_edi_index = document_with_index.key_loading
              FROM document_with_index
             WHERE document_with_index.invoice_id = move.id;
        """)
