from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "payment_sepa_direct_debit.payment_provider_kanban")
