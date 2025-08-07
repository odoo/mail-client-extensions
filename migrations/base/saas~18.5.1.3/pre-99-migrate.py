from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
        CREATE TABLE ir_actions_server_history (
            id SERIAL NOT NULL PRIMARY KEY,
            action_id INTEGER,
            code TEXT,
            create_uid INTEGER,
            write_uid INTEGER,
            create_date TIMESTAMP WITHOUT TIME ZONE,
            write_date TIMESTAMP WITHOUT TIME ZONE
        )
    """)
    cr.execute("""
        INSERT INTO ir_actions_server_history (
                        action_id,
                        code,
                        create_uid,
                        create_date,
                        write_uid,
                        write_date
                    )
             SELECT a.id,
                    a.code,
                    a.write_uid,
                    a.write_date,
                    a.write_uid,
                    a.write_date
               FROM ir_act_server a
              WHERE a.state = 'code'
    """)

    util.remove_field(cr, "ir.model.fields", "complete_name")
    cr.execute("DROP INDEX IF EXISTS ir_model_constraint__type_index")

    util.remove_field(cr, "res.lang", "short_time_format")
    util.remove_field(cr, "res.lang", "short_date_format")

    util.rename_xmlid(cr, "account_intrastat.xi", "base.xi")

    # convert column ir_model_fields.translate
    # the below code is the best effort to convert and fill the translate column
    # the result could be incorrect in some cases
    # 1. fields.Html(translate=True, sanitize=False)
    #     should be 'default' but is filled with 'html_translate'
    #     (we don't have this use case, and this field is not recommended)
    # 2. fields.Text(translate=xml_translate)
    #     should be 'xml_translate' but is filled with 'default'
    # The filled data is mainly used by registry._database_translated_fields to
    # avoid converting the column type from jsonb to varchar and losing translations
    # when the translate attribute is overridden. The incorrect data is acceptable.
    # Also, the data will be corrected during installing modules
    cr.execute("""
        ALTER TABLE ir_model_fields
          ALTER COLUMN translate TYPE VARCHAR
            USING (
              CASE
                WHEN translate IS NOT TRUE THEN NULL
                WHEN model = 'ir.ui.view' AND name = 'arch_db' THEN 'xml_translate'
                WHEN model = 'theme.ir.ui.view' AND name = 'arch' THEN 'xml_translate'
                WHEN ttype = 'html' THEN 'html_translate'
                ELSE 'standard'
              END
            )
    """)
    registry = util.env(cr).registry
    # refill registry._database_translated_fields with new translate data
    cr.execute("SELECT model || '.' || name, translate FROM ir_model_fields WHERE translate IS NOT NULL")
    registry._database_translated_fields = dict(cr.fetchall())
