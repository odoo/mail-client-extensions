from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_br_avatax.view_product_template_form")
    util.remove_view(cr, "l10n_br_avatax.res_partner_view_form")

    for inh in util.for_each_inherit(cr, "account.external.tax.mixin"):
        table = util.table_of_model(cr, inh.model)
        if util.table_exists(cr, table):
            util.create_column(cr, table, "l10n_br_goods_operation_type_id", "integer")
            util.create_column(cr, table, "l10n_br_cnae_code_id", "integer")
