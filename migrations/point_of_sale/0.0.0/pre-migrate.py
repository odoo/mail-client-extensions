import uuid

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.column_exists(cr, "pos_config", "access_token") and util.version_between("18.0", "19.0"):
        cr.execute(
            """
          SELECT unnest(array_agg(id)) AS id
            FROM pos_config
        GROUP BY access_token
          HAVING COUNT(*) > 1
        ORDER BY id
            """
        )
        access_token_map = {id_: str(uuid.uuid4().hex[:16]) for (id_,) in cr.fetchall()}
        if access_token_map:
            util.bulk_update_table(cr, "pos_config", "access_token", access_token_map)
            util._logger.warning(
                "Multiple PoS Config records had duplicate access tokens; new unique tokens were automatically assigned during the upgrade."
            )
