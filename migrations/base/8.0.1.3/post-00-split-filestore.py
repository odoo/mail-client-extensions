import base64
from os import environ as ENV, path
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager


SAAS = bool(ENV.get("OE_SAAS_MIGRATION"))
MOVE_TO_FILESTORE = bool(ENV.get("OE_MOVE_ATTACHMENTS_TO_FILESTORE"))

def move_db_attachments_to_disk(cr):
    registry = RegistryManager.get(cr.dbname)
    keep_on_db = registry['ir.config_parameter'].get_param(
        cr, SUPERUSER_ID, 'migration_keep_attachments_on_db')
    if keep_on_db:
        return

    registry['ir.config_parameter'].set_param(
        cr, SUPERUSER_ID, 'ir_attachment.location', 'file')

    iter_cur = cr._cnx.cursor("iter_cur")
    iter_cur.itersize = 1
    iter_cur.execute("""
        SELECT  id, db_datas
        FROM    ir_attachment
        WHERE   db_datas IS NOT NULL
        FOR UPDATE
        """)
    for id, db_datas in iter_cur:
        raw = base64.b64decode(db_datas)
        fname, full_path = \
            registry['ir.attachment']._get_path(cr, SUPERUSER_ID, raw)
        if not path.exists(full_path):
            # NOTE: _file_write() hide exceptions, so we do it ourselves
            with open(full_path, 'wb') as fh:
                fh.write(raw)
        cr.execute("""
            UPDATE  ir_attachment
            SET     db_datas = NULL
            ,       file_size = %s
            ,       store_fname = %s
            WHERE CURRENT OF iter_cur
            """, [len(raw), fname])

    if SAAS:
        cr.execute("""
            -- NOTE: since we rename the migrated database in SaaS, we should
            --       purge the table.
            VACUUM FULL ir_attachment;
            """)

def migrate(cr, version):
    if MOVE_TO_FILESTORE:
        move_db_attachments_to_disk(cr)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.ERROR)
    from openerp.addons.base.maintenance.migrations import util
    from openerp.api import Environment

    def main(cr, _):
        with Environment.manage():
            move_db_attachments_to_disk(cr)

    util.main(main)
