from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_mx_edi_stock.mx_edi_figure_1")
    util.remove_record(cr, "l10n_mx_edi_stock.mx_edi_vehicle")

    fields_mapping = {
        "name": "l10n_mx_transport_perm_number",
        "transport_insurer": "l10n_mx_transport_insurer",
        "transport_insurance_policy": "l10n_mx_transport_insurance_policy",
        "transport_perm_sct": "l10n_mx_transport_perm_sct",
        "vehicle_model": "model_year",
        "vehicle_config": "l10n_mx_vehicle_config",
        "vehicle_licence": "license_plate",
        "gross_vehicle_weight": "l10n_mx_gross_vehicle_weight",
        "trailer_ids": "l10n_mx_trailer_ids",
        "figure_ids": "l10n_mx_figure_ids",
        "environment_insurer": "l10n_mx_environment_insurer",
        "environment_insurance_policy": "l10n_mx_environment_insurance_policy",
    }
    util.merge_model(cr, "l10n_mx_edi.vehicle", "fleet.vehicle", drop_table=False, fields_mapping=fields_mapping)
    util.create_column(cr, "fleet_vehicle", "_upg_orig_l10n_mx_vehicle_id", "int4")

    cr.execute("""
            INSERT INTO fleet_vehicle_model_brand (name, active)
                 VALUES ('MX generic brand', TRUE)
              RETURNING id
            """)
    brand_id = cr.fetchone()[0]

    util.create_column(cr, "fleet_vehicle_model", "_upg_is_default_mx_model", "boolean")
    state_id = util.ref(cr, "fleet.fleet_vehicle_state_new_request")

    cr.execute(
        """
        WITH mx_models AS (
            SELECT COALESCE(trim(vehicle_model), 'unknown') vehicle_model,
                   array_agg(id) ids
              FROM l10n_mx_edi_vehicle
          GROUP BY 1
        ), new_models AS (
            INSERT INTO fleet_vehicle_model (
                            name,
                            brand_id, model_year, vehicle_type, power_unit, range_unit, active, _upg_is_default_mx_model
                        )
                 SELECT 'MX generic model ' || mx_models.vehicle_model,
                        %s, mx_models.vehicle_model, 'car', 'power', 'km', TRUE, TRUE
                   FROM mx_models
              RETURNING id, model_year
        )
        INSERT INTO fleet_vehicle (
                        active, model_year, model_id, state_id, license_plate,
                        odometer_unit, power_unit, co2_emission_unit, range_unit,
                        acquisition_date, contract_date_start,
                        _upg_orig_l10n_mx_vehicle_id,
                        name
                    )
             SELECT mv.active, mv.vehicle_model, m.id, %s, mv.vehicle_licence,
                    'kilometers', 'power', 'g/km', 'km',
                    CURRENT_DATE, CURRENT_DATE,
                    mv.id,
                    'MX generic model ' || mv.vehicle_model || '/' || mv.vehicle_licence
               FROM l10n_mx_edi_vehicle mv
               JOIN mx_models
                 ON mv.id = ANY(mx_models.ids)
               JOIN new_models m
                 ON m.model_year = mx_models.vehicle_model
        """,
        (brand_id, state_id),
    )
