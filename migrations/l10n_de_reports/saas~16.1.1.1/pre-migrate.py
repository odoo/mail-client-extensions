from odoo.upgrade import util


def migrate(cr, version):
    if not util.column_exists(cr, "res_partner", "l10n_de_datev_identifier_customer"):
        util.create_column(cr, "res_partner", "l10n_de_datev_identifier_customer", "int4")

        query = """
            UPDATE res_partner partn
               SET l10n_de_datev_identifier_customer = partn.l10n_de_datev_identifier
             WHERE partn.l10n_de_datev_identifier != 0
        """

        util.parallel_execute(cr, util.explode_query_range(cr, query, table="res_partner", alias="partn"))

    util.remove_record(cr, "l10n_de_reports.datev_start_count")
    util.remove_record(cr, "l10n_de_reports.datev_start_count_vendors")
