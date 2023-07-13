from odoo.upgrade import util


def migrate(cr, version):
    # Migrate 'account.edi.document' to 'l10n_mx_edi.document'
    query = """
        INSERT INTO l10n_mx_edi_document (datetime, picking_id, attachment_id, state, sat_state)
        SELECT
            picking.write_date,
            picking.id AS picking_id,
            picking.l10n_mx_edi_cfdi_attachment_id AS attachment_id,
            'picking_sent' AS state,
            picking.l10n_mx_edi_cfdi_sat_state AS sat_state
        FROM stock_picking picking
        WHERE picking.l10n_mx_edi_cfdi_state = 'sent'
    """
    util.explode_execute(cr, query, table="stock_picking", alias="picking")
