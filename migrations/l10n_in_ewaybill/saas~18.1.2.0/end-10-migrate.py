from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
        CREATE UNLOGGED TABLE _upg_l10n_in_ewaybill_so_data_temp(
            move_id integer,
            warehouse_address_id integer,
            PRIMARY KEY(move_id, warehouse_address_id)
        )
    """)
    cr.execute("""
        CREATE UNLOGGED TABLE _upg_l10n_in_ewaybill_po_data_temp(
            move_id integer,
            warehouse_address_id integer,
            PRIMARY KEY(move_id, warehouse_address_id)
        )
    """)
    if util.module_installed(cr, "l10n_in_sale_stock"):
        cr.execute(
            """
            WITH warehouse_address_from_so as (
                SELECT aml.move_id as move_id, sw.partner_id as warehouse_address_id, count(DISTINCT sw.id) as warehouse_count
                  FROM account_move_line aml
                  JOIN account_edi_document edi_doc ON edi_doc.move_id = aml.move_id
                  JOIN account_edi_format aef ON aef.id = edi_doc.edi_format_id
                  JOIN sale_order_line_invoice_rel AS solir ON solir.invoice_line_id = aml.id
                  JOIN sale_order_line AS sol ON sol.id = solir.order_line_id
                  JOIN sale_order AS so ON so.id = sol.order_id
                  JOIN stock_warehouse AS sw ON sw.id = so.warehouse_id
                 WHERE aef.code = 'in_ewaybill_1_03'
              GROUP BY sw.partner_id, aml.move_id
            )
            INSERT INTO _upg_l10n_in_ewaybill_so_data_temp
            SELECT move_id, warehouse_address_id
              FROM warehouse_address_from_so
             WHERE warehouse_count = 1
            """
        )
    if util.module_installed(cr, "l10n_in_purchase_stock"):
        cr.execute(
            """
            WITH warehouse_address_from_po as (
                SELECT  aml.move_id as move_id, sw.partner_id as warehouse_address_id, count(DISTINCT sw.id) as warehouse_count
                  FROM account_move_line aml
                  JOIN account_edi_document edi_doc ON edi_doc.move_id = aml.move_id
                  JOIN account_edi_format aef ON aef.id = edi_doc.edi_format_id
                  JOIN stock_move sm ON aml.purchase_line_id = sm.purchase_line_id
                  JOIN stock_warehouse sw ON sm.warehouse_id = sw.id
                 WHERE aef.code = 'in_ewaybill_1_03'
                 AND aml.purchase_line_id IS NOT NULL
                GROUP BY aml.move_id, sw.partner_id
            )
            INSERT INTO _upg_l10n_in_ewaybill_po_data_temp
            SELECT move_id, warehouse_address_id
              FROM warehouse_address_from_po
             WHERE warehouse_count = 1
            """
        )
    util.explode_execute(
        cr,
        """
        WITH _new AS (
            INSERT INTO l10n_in_ewaybill(
                account_move_id, company_id, partner_bill_to_id, partner_bill_from_id,
                partner_ship_to_id, partner_ship_from_id, type_id, distance, mode, vehicle_no,
                vehicle_type, transportation_doc_no, transportation_doc_date, transporter_id,
                state, cancel_reason, cancel_remarks, error_message, blocking_level
            )
            SELECT
                am.id AS account_move_id,
                am.company_id AS company_id,
                am.partner_id AS partner_bill_to_id,
                rc.partner_id AS partner_bill_from_id,
                COALESCE(am.l10n_in_ewaybill_port_partner_id, am.partner_shipping_id) AS partner_ship_to_id,
                COALESCE(sdt.warehouse_address_id, pdt.warehouse_address_id, rc.partner_id) AS partner_ship_from_id,
                am.l10n_in_type_id AS type_id,
                am.l10n_in_distance AS distance,
                NULLIF(am.l10n_in_mode,'0') AS mode,
                am.l10n_in_vehicle_no AS vehicle_no,
                am.l10n_in_vehicle_type AS vehicle_type,
                am.l10n_in_transportation_doc_no AS transportation_doc_no,
                am.l10n_in_transportation_doc_date AS transportation_doc_date,
                am.l10n_in_transporter_id AS transporter_id,
                CASE
                    WHEN am.edi_state = 'sent' THEN 'generated'
                    WHEN am.edi_state = 'cancelled' THEN 'cancel'
                    ELSE 'pending'
                END AS state,
                am.l10n_in_edi_cancel_reason AS cancel_reason,
                am.l10n_in_edi_cancel_remarks AS cancel_remarks,
                edi_doc.error AS error_message,
                NULLIF(edi_doc.blocking_level, 'info') AS blocking_level
            FROM account_edi_document edi_doc
            JOIN account_move am ON am.id = edi_doc.move_id
            JOIN account_edi_format aef ON aef.id = edi_doc.edi_format_id
            JOIN res_company rc ON rc.id = am.company_id
            LEFT JOIN _upg_l10n_in_ewaybill_so_data_temp sdt ON sdt.move_id = edi_doc.move_id
            LEFT JOIN _upg_l10n_in_ewaybill_po_data_temp pdt ON pdt.move_id = edi_doc.move_id
           WHERE aef.code = 'in_ewaybill_1_03'
             AND {parallel_filter}
         RETURNING id, account_move_id
        )
        UPDATE ir_attachment a
          SET res_id = _new.id, res_model = 'l10n.in.ewaybill', res_field = 'attachment_file'
          FROM _new
          JOIN account_edi_document d
            ON d.move_id = _new.account_move_id
          JOIN account_edi_format aef
            ON aef.id = d.edi_format_id
         WHERE a.id = d.attachment_id
           AND aef.code = 'in_ewaybill_1_03'
        """,
        "account_edi_document",
        "edi_doc",
    )
    cr.execute("DROP TABLE _upg_l10n_in_ewaybill_so_data_temp")
    cr.execute("DROP TABLE _upg_l10n_in_ewaybill_po_data_temp")
    cr.execute("""
        DELETE FROM account_edi_document aed
         USING account_edi_format aef
         WHERE aef.code = 'in_ewaybill_1_03'
          AND aef.id=aed.edi_format_id
    """)
    fields = util.splitlines(
        """
        l10n_in_edi_ewaybill_show_send_button
        l10n_in_edi_ewaybill_direct_api
        l10n_in_transporter_id
        l10n_in_transportation_doc_date
        l10n_in_transportation_doc_no
        l10n_in_type_id
        l10n_in_mode
        l10n_in_vehicle_no
        l10n_in_vehicle_type
        l10n_in_distance
        l10n_in_ewaybill_port_partner_id
        """
    )
    for f in fields:
        util.remove_field(cr, "account.move", f)
    util.remove_record(cr, "l10n_in_ewaybill.edi_in_ewaybill_json_1_03")

    CRON_CODE = """
    domain = [('account_move_id', '!=', False), ('state', '!=', 'pending'), ('attachment_file', '!=', False)]
    total = model.search_count(domain)
    for i, rec in enumerate(model.search(domain, limit=100), 1):
        rec._set_data_from_attachment()
        remaining = total - i
        env['ir.cron']._notify_progress(done=i, remaining=remaining, deactivate=(remaining == 0))
    """
    util.create_cron(cr, "Set l10nIn ewaybill data", "l10n.in.ewaybill", CRON_CODE)
