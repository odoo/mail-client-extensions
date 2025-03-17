from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "crm.action_mark_as_lost", noupdate=True)
