from odoo.upgrade import util


def migrate(cr, version):
    for i in range(4):
        util.force_noupdate(cr, f"digest.digest_tip_digest_{i}", noupdate=False)
