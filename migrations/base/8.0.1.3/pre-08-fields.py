try:
    from openerp.addons.base.maintenance.migrations import util
except ImportError:
    from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # the fields are renamed, but for existing DBs they will cause issues
    # if we rename those old fields now
    util.remove_field(cr, "base.module.update", "update")
    util.remove_field(cr, "base.module.update", "add")
