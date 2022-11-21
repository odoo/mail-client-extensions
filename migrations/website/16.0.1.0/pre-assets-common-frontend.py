# -*- coding: utf-8 -*-


def migrate(cr, version):
    """
    Convert all ir.asset records and ir.attachment records which are the result
    of a SCSS customization made via the HTML/SCSS editor. Indeed, in 16.0, the
    assets_common bundle stopped being used for frontend screens as all the
    common files have been put inside the assets_frontend bundle directly. Custo
    that were made to those files were marked as being part of assets_common and
    now should be marked as being part of assets_frontend.

    This is especially important for the automatic SCSS custo that are made
    while changing some themes configuration (like your website font-size).
    Those are made to variable sub-assets (typically _assets_primary_variables)
    but were still marked as part of assets_common and should now be marked as
    part of assets_frontend to allow further theme customizations.

    Note: this does not handle the possibility of a customization that was made
    in a common file that does exist in the frontend bundle anymore. That is
    a recurring problem that happens at every migration, a generic solution
    would need to be found if not already (when the assets were regrouped, as a
    first step for 16.0, all common files were added in frontend, none was
    entirely removed from the bundle).
    """

    cr.execute(
        """
        /*
        First, select all ir.asset records that are there to replace a file
        in the assets_common bundle. Join those on their related ir.attachment
        records (based on their URL / website_id).
        */
        WITH upd AS (
            SELECT asset.id AS asset_id,
                   attach.id AS attach_id
              FROM ir_asset AS asset
              JOIN ir_attachment AS attach
                ON asset.website_id = attach.website_id
               AND asset.path = attach.url
             WHERE asset.directive = 'replace'
               AND asset.path LIKE '%.custom.web.assets!_common.scss' ESCAPE '!'
        ),
        /*
        For each of those ir.attachment records, replace the url field
        accordingly ("assets_frontend" inside instead of "assets_common")
        */
        dummy AS (
            UPDATE ir_attachment
               SET url = REPLACE(url, '.custom.web.assets_common.scss', '.custom.web.assets_frontend.scss')
              FROM upd
             WHERE id = upd.attach_id
        )
        /*
        For each of those ir.asset records, replace the mentions to
        assets_common by mentions to assets_frontend.
        */
        UPDATE ir_asset
           SET name = REPLACE(name, 'assets_common', 'assets_frontend'),
               path = REPLACE(path, '.custom.web.assets_common.scss', '.custom.web.assets_frontend.scss'),
               bundle = CASE
                            WHEN bundle in ('web.assets_common', 'web._assets_common_styles')
                            THEN 'web.assets_frontend'
                            ELSE bundle
                        END
          FROM upd
         WHERE id = upd.asset_id
    """
    )
