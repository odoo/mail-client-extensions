from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_accountant.product_template_form_view")
    util.remove_field(cr, "account.change.lock.date", "exception_needed")
