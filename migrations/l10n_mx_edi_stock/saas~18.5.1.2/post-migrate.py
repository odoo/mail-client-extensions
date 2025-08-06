from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
        UPDATE fleet_vehicle fv
           SET l10n_mx_transport_perm_number       = mv.name,
               l10n_mx_transport_insurer           = mv.transport_insurer,
               l10n_mx_transport_insurance_policy  = mv.transport_insurance_policy,
               l10n_mx_transport_perm_sct          = mv.transport_perm_sct,
               l10n_mx_vehicle_config              = mv.vehicle_config,
               l10n_mx_gross_vehicle_weight        = mv.gross_vehicle_weight,
               l10n_mx_environment_insurer         = mv.environment_insurer,
               l10n_mx_environment_insurance_policy= mv.environment_insurance_policy,
               l10n_mx_is_freight_vehicle = TRUE
          FROM l10n_mx_edi_vehicle mv
         WHERE fv._upg_orig_l10n_mx_vehicle_id = mv.id
     RETURNING fv.id, fv._upg_orig_l10n_mx_vehicle_id
    """)

    ids_mapping = {src_id: dst_id for dst_id, src_id in cr.fetchall()}
    if ids_mapping:
        util.replace_record_references_batch(cr, ids_mapping, "fleet.vehicle")

    # Change relation in l10n_mx_edi_trailer, from l10n_mx_edi_vehicle to fleet_vehicle and set new vehicle
    cr.execute("ALTER TABLE l10n_mx_edi_trailer DROP CONSTRAINT IF EXISTS l10n_mx_edi_trailer_vehicle_id_fkey")
    cr.execute("""
        UPDATE l10n_mx_edi_trailer tr
           SET vehicle_id = fv.id
          FROM fleet_vehicle fv
         WHERE tr.vehicle_id = fv._upg_orig_l10n_mx_vehicle_id;
    """)

    # Change relation in l10n_mx_edi_figure, from l10n_mx_edi_vehicle to fleet_vehicle and set new vehicle
    cr.execute("ALTER TABLE l10n_mx_edi_figure DROP CONSTRAINT IF EXISTS l10n_mx_edi_figure_vehicle_id_fkey")

    cr.execute("""
       UPDATE l10n_mx_edi_figure fig
          SET vehicle_id = fv.id
         FROM fleet_vehicle fv
        WHERE fig.vehicle_id = fv._upg_orig_l10n_mx_vehicle_id;
    """)

    # Set driver_id the figure_id.operator_id with type 01, and delete from relation in l10n_mx_edi_figure
    cr.execute("""
        UPDATE fleet_vehicle fv
           SET driver_id = fig.operator_id
          FROM l10n_mx_edi_figure fig
         WHERE fig.vehicle_id = fv.id
           AND fig.operator_id IS NOT NULL
           AND fig.type = '01'
    """)

    cr.execute("""
        UPDATE l10n_mx_edi_figure fig
           SET vehicle_id = NULL
          FROM fleet_vehicle fv
         WHERE fig.vehicle_id = fv.id
           AND fig.operator_id = fv.driver_id
           AND fig.type = '01'
    """)

    # Change relation in stock_picking from l10n_mx_edi_vehicle to fleet_vehicle, and assign the new vehicle
    cr.execute("ALTER TABLE stock_picking DROP CONSTRAINT IF EXISTS stock_picking_l10n_mx_edi_vehicle_id_fkey")
    cr.execute("""
        UPDATE stock_picking sp
           SET l10n_mx_edi_vehicle_id = fv.id
          FROM fleet_vehicle fv
         WHERE sp.l10n_mx_edi_vehicle_id = fv._upg_orig_l10n_mx_vehicle_id
    """)

    util.remove_model(cr, "l10n_mx_edi.vehicle")
    util.remove_view(cr, "l10n_mx_edi_stock.vehicle_form_view_hazard")
    util.remove_view(cr, "l10n_mx_edi_stock.vehicle_tree_view")
    util.remove_view(cr, "l10n_mx_edi_stock.vehicle_search_view")
    util.remove_view(cr, "l10n_mx_edi_stock.vehicle_form_view")
    util.make_field_non_stored(cr, "stock.picking", "l10n_mx_edi_gross_vehicle_weight", selectable=False)

    if ids_mapping:
        message = """
        [MIGRATION] l10n_mx_edi.vehicle removed; data moved to fleet.vehicle

        Summary:
        - The legacy model 'l10n_mx_edi.vehicle' has been removed.
        - All of its records were migrated to 'fleet.vehicle' (one row per vehicle).
        - Vehicle models were normalized using placeholder entries under the 'MX generic brand'.
        Each placeholder is named 'MX generic model + vehicle_model' and uses model_year = vehicle_model.

        Action required:
        - Review newly created placeholder models and backfill real brand/model data as needed.
        """

        util.add_to_migration_reports(
            message=message,
            category="data_migration",
            format="md",
        )
