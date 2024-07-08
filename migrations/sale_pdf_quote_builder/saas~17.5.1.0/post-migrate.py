import json

from psycopg2.extras import execute_values

from odoo.upgrade import util


def migrate(cr, version):
    # Migrate existing documents (either from the res.company or the sale.order.template)
    cr.execute("""
        WITH docs AS (
        INSERT INTO quotation_document(
                        ir_attachment_id, sequence, create_uid, write_uid, document_type, active, create_date, write_date
                    )
             SELECT id, 10, create_uid, write_uid, substr(res_field, 6), true, create_date, write_date
               FROM ir_attachment
              WHERE res_model = 'res.company'
                AND res_field IN ('sale_header', 'sale_footer')
          RETURNING id, ir_attachment_id
        )
        UPDATE ir_attachment a
           SET res_model = 'quotation.document',
               res_id = docs.id,
               name = CASE a.res_field WHEN 'sale_header' THEN c.sale_header_name ELSE c.sale_footer_name END,
               res_field = NULL
          FROM docs, res_company c
         WHERE a.id = docs.ir_attachment_id
           AND c.id = a.res_id
    """)

    cr.execute("""
            WITH docs AS (
            INSERT INTO quotation_document(
                            ir_attachment_id, sequence, create_uid, write_uid, document_type, active, create_date, write_date
                        )
                 SELECT id, 10, create_uid, write_uid, substr(res_field, 6), true, create_date, write_date
                   FROM ir_attachment
                  WHERE res_model = 'sale.order.template'
                    AND res_field IN ('sale_header', 'sale_footer')
              RETURNING id, ir_attachment_id
            ),
                 rel AS (
            INSERT INTO header_footer_quotation_template_rel(quotation_document_id, sale_order_template_id)
                 SELECT docs.id, a.res_id
                   FROM docs
                   JOIN ir_attachment a
                     ON a.id = docs.ir_attachment_id
            )
            UPDATE ir_attachment a
               SET res_model = 'quotation.document',
                   res_id = docs.id,
                   name = CASE a.res_field WHEN 'sale_header' THEN t.sale_header_name ELSE t.sale_footer_name END,
                   res_field = NULL
              FROM docs, sale_order_template t
             WHERE a.id = docs.ir_attachment_id
               AND t.id = a.res_id
        """)

    # Populate the sale.pdf.form.field with the values from the config parameter.
    cr.execute(
        """
        DELETE FROM ir_config_parameter
              WHERE "key" = 'sale_pdf_quote_builder.form_field_path_mapping'
          RETURNING value
    """
    )
    if cr.rowcount:
        previous_mapping = json.loads(cr.fetchone()[0])
        # The following mapping is already added in the sale.pdf.form.field data
        DATA_MAPPING = {
            "header_footer": {
                "amount_total": "amount_total",
                "amount_untaxed": "amount_untaxed",
                "client_order_ref": "client_order_ref",
                "delivery_date": "commitment_date",
                "name": "name",
                "partner_id__name": "partner_id.name",
                "user_id__name": "user_id.name",
                "validity_date": "validity_date",
            },
            "product_document": {
                "amount_total": "order_id.amount_total",
                "amount_untaxed": "order_id.amount_untaxed",
                "client_order_ref": "order_id.client_order_ref",
                "delivery_date": "order_id.commitment_date",
                "description": "name",
                "discount": "discount",
                "name": "order_id.name",
                "partner_id__name": "order_partner_id.name",
                "price_unit": "price_unit",
                "product_sale_price": "product_id.lst_price",
                "quantity": "product_uom_qty",
                "tax_excl_price": "price_subtotal",
                "tax_incl_price": "price_total",
                "taxes": "tax_ids",
                "uom": "product_uom.name",
                "user_id__name": "salesman_id.name",
                "validity_date": "order_id.validity_date",
            },
        }
        mapping_to_add = []
        for document_type, mapping in previous_mapping.items():
            new_type = "quotation_document" if document_type == "header_footer" else "product_document"
            for name, path in mapping.items():
                if name not in DATA_MAPPING[document_type]:
                    mapping_to_add.append((name, new_type, path))
        if mapping_to_add:
            execute_values(
                cr._obj,
                "INSERT INTO sale_pdf_form_field(name, document_type, path) VALUES %s",
                mapping_to_add,
            )

    # Remove olf fields, models and view
    util.remove_field(cr, "sale.order.template", "sale_header")
    util.remove_field(cr, "sale.order.template", "sale_header_name")
    util.remove_field(cr, "sale.order.template", "sale_footer")
    util.remove_field(cr, "sale.order.template", "sale_footer_name")

    util.remove_field(cr, "res.config.settings", "sale_header")
    util.remove_field(cr, "res.config.settings", "sale_header_name")
    util.remove_field(cr, "res.config.settings", "sale_footer")
    util.remove_field(cr, "res.config.settings", "sale_footer_name")

    util.remove_field(cr, "res.company", "sale_header")
    util.remove_field(cr, "res.company", "sale_header_name")
    util.remove_field(cr, "res.company", "sale_footer")
    util.remove_field(cr, "res.company", "sale_footer_name")

    util.remove_model(cr, "sale.pdf.quote.builder.dynamic.fields.wizard.line")
    util.remove_model(cr, "sale.pdf.quote.builder.dynamic.fields.wizard")
    util.remove_view(cr, "sale_pdf_quote_builder.res_config_settings_view_form")

    # Trigger the cron to parse existing documents, to link them to the correct form fields
    cron_id = util.ref(cr, "sale_pdf_quote_builder.cron_post_upgrade_assign_missing_form_fields")
    if cron_id:
        cr.execute(
            """
            INSERT INTO ir_cron_trigger(cron_id, call_at)
                 VALUES (%s, now() at time zone 'UTC' + interval '10 minutes')
            """,
            [cron_id],
        )
