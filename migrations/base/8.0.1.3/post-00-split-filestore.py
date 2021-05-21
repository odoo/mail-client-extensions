import base64
import re
from os import environ as ENV
from os import path

from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager


def move_db_attachments_to_disk(cr):
    registry = RegistryManager.get(cr.dbname)
    keep_on_db = registry["ir.config_parameter"].get_param(cr, SUPERUSER_ID, "migration_keep_attachments_on_db")
    if keep_on_db:
        return

    registry["ir.config_parameter"].set_param(cr, SUPERUSER_ID, "ir_attachment.location", "file")

    iter_cur = cr._cnx.cursor("iter_cur")
    iter_cur.itersize = 1
    iter_cur.execute(
        """
        SELECT  id, db_datas
        FROM    ir_attachment
        WHERE   db_datas IS NOT NULL
        FOR UPDATE
        """
    )
    for _id, db_datas in iter_cur:
        if ENV.get("ODOO_MIG_8_ATTACHMENTS_NOT_B64ENCODED") and not re.search(
            "^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$", db_datas
        ):
            raw = db_datas
        else:
            raw = base64.b64decode(db_datas)
        fname, full_path = registry["ir.attachment"]._get_path(cr, SUPERUSER_ID, raw)
        if not path.exists(full_path):
            # NOTE: _file_write() hide exceptions, so we do it ourselves
            with open(full_path, "wb") as fh:
                fh.write(raw)
        cr.execute(
            """
            UPDATE  ir_attachment
            SET     db_datas = NULL
            ,       file_size = %s
            ,       store_fname = %s
            WHERE CURRENT OF iter_cur
            """,
            [len(raw), fname],
        )


def migrate(cr, version):
    move_db_attachments_to_disk(cr)
