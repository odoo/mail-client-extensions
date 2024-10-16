from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "l10n_mx_edi_addenda", "_migration_view_id", "int4")
    cr.execute(
        """
            INSERT INTO l10n_mx_edi_addenda (name, arch, _migration_view_id)
                 SELECT view.name, view.arch_prev, view.id
                   FROM ir_ui_view view
                  WHERE view.l10n_mx_edi_addenda_flag = TRUE
        """,
    )
    partner_query = """
        UPDATE res_partner p
           SET l10n_mx_edi_addenda_id = addenda.id
          FROM l10n_mx_edi_addenda addenda
         WHERE p.l10n_mx_edi_addenda = addenda._migration_view_id
    """
    util.explode_execute(cr, partner_query, table="res_partner", alias="p")

    util.remove_column(cr, "l10n_mx_edi_addenda", "_migration_view_id", "int4")
    util.remove_column(cr, "res_partner", "l10n_mx_edi_addenda")
    util.remove_column(cr, "ir_ui_view", "l10n_mx_edi_addenda_flag")

    am_query = """
        UPDATE account_move m
           SET l10n_mx_edi_addenda_id = partner.l10n_mx_edi_addenda_id
          FROM res_partner partner
         WHERE partner.l10n_mx_edi_addenda_id IS NOT NULL
           AND (m.partner_id = partner.id OR m.commercial_partner_id = partner.id)
           AND {parallel_filter}
    """
    util.explode_execute(cr, am_query, table="account_move", alias="m")
