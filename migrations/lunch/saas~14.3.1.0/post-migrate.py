from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    env['lunch.alert'].with_context(active_test=False).search([])._sync_cron()
    env['lunch.supplier'].with_context(active_test=False).search([])._sync_cron()
