from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "account_disallowed_expenses_fleet.search_template_extra_options")
