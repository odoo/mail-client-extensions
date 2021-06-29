# -*- coding: utf-8 -*-


def migrate(cr, version):
    # ===========================================================
    # Task 2526717 : Agent / Fiduciary for XML exports
    # ===========================================================

    # Look for the agent in the ir_config_parameter and transfer its id to res_company if it exists.
    cr.execute(
        """
          WITH config_param AS (
              SELECT CAST(icp.value AS INT) val,
                     rc.id comp_id
                FROM ir_config_parameter icp
                JOIN res_company rc ON icp.key = 'l10n_be_reports.xml_export_representative_' || rc.id
          ),
               update_company AS (
                   UPDATE res_company rc
                      SET account_representative_id = cp.val
                     FROM config_param cp
                    WHERE rc.id = cp.comp_id
                RETURNING cp.comp_id
               )
        DELETE
          FROM ir_config_parameter icp USING update_company uc
         WHERE icp.key = 'l10n_be_reports.xml_export_representative_' || uc.comp_id;
    """
    )
