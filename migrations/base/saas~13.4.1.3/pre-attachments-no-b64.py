# -*- coding: utf-8 -*-


def migrate(cr, version):
    # attachments are now stored raw in database.
    # try to decode the base64 data
    parallel_safe = "PARALLEL SAFE" if cr._cnx.server_version >= 90600 else ""
    try_b64 = f"""
        CREATE FUNCTION try_b64(bytea) RETURNS bytea AS $$
        BEGIN
            RETURN decode(encode($1, 'escape'), 'base64');
        EXCEPTION WHEN OTHERS THEN
            RETURN $1;
        END
        $$ LANGUAGE plpgsql IMMUTABLE RETURNS NULL ON NULL INPUT {parallel_safe};
    """

    cr.execute(try_b64)
    cr.execute("UPDATE ir_attachment SET db_datas = try_b64(db_datas) WHERE db_datas IS NOT NULL")
    cr.execute("DROP FUNCTION try_b64(bytea);")
