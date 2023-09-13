from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move", "is_l10n_br_avatax")
    util.remove_model(cr, "l10n_br.account.avatax")
    util.remove_view(cr, "l10n_br_avatax.move_form_inherit")
