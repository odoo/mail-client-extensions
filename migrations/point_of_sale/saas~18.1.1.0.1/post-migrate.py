import logging

from odoo.upgrade import util

_logger = logging.getLogger("odoo.upgrade.migrations.point_of_sale.18.1." + __name__)


def migrate(cr, version):
    cr.execute("SELECT id FROM pos_session WHERE state IN ('opened', 'opening_control')")
    pos_ids = [r[0] for r in cr.fetchall()]
    if pos_ids:
        _logger.log(
            util.NEARLYWARN if util.on_CI() else logging.WARNING,
            "%s PoS sessions were already open, generating its sequences",
            len(pos_ids),
        )
        util.iter_browse(util.env(cr)["pos.session"], pos_ids)._create_sequences()
