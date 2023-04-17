# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        r"""
              SELECT asset.id as asset_id, attachment.id as attachment_id, regexp_matches(asset.path, '^(/.+)\.custom\.(.+)\.(\w+)$') as matches
      INTO TEMPORARY _upgrade_custom_assets
                FROM ir_asset asset
           LEFT JOIN ir_attachment attachment ON attachment.url = asset.path
               WHERE asset.path LIKE '%.custom.%'
        """
    )
    cr.execute(
        """
             UPDATE ir_asset asset
                SET path = CONCAT('/_custom/', upgraded.matches[2], upgraded.matches[1], '.', upgraded.matches[3])
               FROM _upgrade_custom_assets upgraded
              WHERE upgraded.asset_id = asset.id
        """
    )
    cr.execute(
        """
             UPDATE ir_attachment attachment
                SET url = CONCAT('/_custom/', upgraded.matches[2], upgraded.matches[1], '.', upgraded.matches[3])
               FROM _upgrade_custom_assets upgraded
              WHERE upgraded.attachment_id = attachment.id
        """
    )
