from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
    UPDATE hr_employee
       SET ssnid = l10n_mx_nss
     WHERE l10n_mx_nss IS NOT NULL
    """
    )
    util.remove_field(cr, "hr.employee", "l10n_mx_nss")
