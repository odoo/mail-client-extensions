from odoo.upgrade import util


def migrate(cr, version):
    util.make_field_non_stored(cr, "hr.employee", "l10n_bd_disabled_dependent")
    util.make_field_non_stored(cr, "hr.employee", "l10n_bd_gazetted_war_founded_freedom_fighter")
