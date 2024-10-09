from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(
        cr,
        "l10n_hu.BUDAHUHB",
        "l10n_hu.COBAHUHX",
        "l10n_hu.FHKBHUHB",
        "l10n_hu.INCNHUHB",
        "l10n_hu.MAVOHUHB",
        "l10n_hu.TAKBHUHB",
    )
