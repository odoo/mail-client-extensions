from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
    UPDATE hr_employee
       SET disabled = l10n_bd_disabled
     WHERE l10n_bd_disabled is true
    """)
    util.remove_field(cr, "hr.employee", "l10n_bd_disabled")
