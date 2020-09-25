# -*- coding: utf-8 -*-


def migrate(cr, version):
    # attachments are now stored raw in database.
    # decode the base64 data
    cr.execute(
        """
            UPDATE ir_attachment
               SET db_datas = decode(encode(db_datas, 'escape'), 'base64')
             WHERE db_datas IS NOT NULL
        """
    )
