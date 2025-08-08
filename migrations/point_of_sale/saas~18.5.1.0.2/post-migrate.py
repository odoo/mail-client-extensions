from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT id FROM pos_config")
    config_ids = [r[0] for r in cr.fetchall()]
    if config_ids:
        util.iter_browse(util.env(cr)["pos.config"], config_ids)._create_sequences()
