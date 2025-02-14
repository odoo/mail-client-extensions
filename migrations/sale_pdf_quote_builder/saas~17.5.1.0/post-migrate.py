from psycopg2.extras import execute_values

from odoo.upgrade import util
from odoo.upgrade.util import json


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
               name =  CASE
                        a.res_field WHEN 'sale_header'
                        THEN COALESCE( c.sale_header_name, 'Company quote header: ' || c.name)
                        ELSE COALESCE( c.sale_footer_name, 'Company quote footer: ' || c.name)
                       END,
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
                   name = CASE
                            a.res_field WHEN 'sale_header'
                            THEN COALESCE(t.sale_header_name, 'Quotation template header: ' || t.name)
                            ELSE COALESCE(t.sale_footer_name, 'Quotation template footer: ' || t.name)
                          END,
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

        mapping_to_add = []
        for document_type, mapping in previous_mapping.items():
            new_type = "quotation_document" if document_type == "header_footer" else "product_document"
            for name, path in mapping.items():
                mapping_to_add.append((name, new_type, path))
        if mapping_to_add:
            execute_values(
                cr._obj,
                """
                INSERT INTO sale_pdf_form_field(name, document_type, path) VALUES %s
                ON CONFLICT DO NOTHING;
                """,
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
