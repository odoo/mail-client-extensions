from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        util.format_query(
            cr,
            """
                CREATE FUNCTION format_transaction_details(data JSONB, prefix TEXT) RETURNS TEXT AS
                $body$
                    DECLARE
                        key TEXT;
                        val JSONB;
                        result TEXT := '';
                    BEGIN
                        IF jsonb_typeof(data) = 'object' THEN
                            FOR key, val IN SELECT * FROM jsonb_each(data) LOOP
                                result := result || prefix || '<b>' || {escape_key} || ':</b> ';
                                IF jsonb_typeof(val) IN ('object', 'array') THEN
                                    result := result || E'\n' || format_transaction_details(val, prefix || '  ');
                                ELSE
                                    result := result || {escape_val} || E'\n';
                                END IF;
                            END LOOP;
                        ELSIF jsonb_typeof(data) = 'array' THEN
                            result := format_transaction_details(
                                ( -- Transform array into dict with indices as keys
                                    SELECT jsonb_object_agg(i - 1, elem)
                                    FROM jsonb_array_elements(data) WITH ORDINALITY AS t(elem, i)
                                ),
                                prefix || '  '
                            );
                        ELSE -- scalar values
                            result := prefix || {escape_data}::TEXT;
                        END IF;
                        RETURN result;
                    END;
                $body$ LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE;
            """,
            escape_key=util.pg_html_escape("key"),
            escape_val=util.pg_html_escape("val::TEXT"),
            escape_data=util.pg_html_escape("data::TEXT"),
        ),
    )

    query = cr.mogrify(
        """
            INSERT INTO mail_message(
                model,
                res_id,
                author_id,
                message_type,
                date,
                body
            )
            SELECT 'account.move',
                   move_id,
                   %(root_id)s,
                   'notification',
                   NOW() at time zone 'UTC',
                   '<div><pre>' || format_transaction_details(transaction_details::JSONB, '') || '</pre></div>'
              FROM account_bank_statement_line
             WHERE transaction_details IS NOT NULL
               AND {parallel_filter}
        """,
        {"root_id": util.ref(cr, "base.partner_root")},
    ).decode()
    util.explode_execute(cr, query, table="account_bank_statement_line")

    cr.execute("DROP FUNCTION IF EXISTS format_transaction_details(JSONB, TEXT);")
