from odoo.upgrade import util


def migrate(cr, version):
    util.make_field_non_stored(cr, "hr.employee", "l10n_lt_working_capacity")
