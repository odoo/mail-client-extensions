from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "l10n.be.double.pay.recovery.wizard", "classic_holiday_pay")
