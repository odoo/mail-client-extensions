# -*- coding: utf-8 -*-
from odoo.addons.base.models.ir_asset import DEFAULT_SEQUENCE

from odoo.upgrade import util


def migrate(cr, version):
    """
    The previous assets management had two ways of ordering the bundle
    construction from the XML views: inheritance and priority.
    The new assets management system does not have a true inheritance mechanism.
    The whole bundle construction order is thus only based on the
    ir_asset.sequence column.

    With the 'post-10-assets-management' script, we try to do the migration
    from one system to another, keeping only one ordering dimension by
    translating the former priority field of an XML view into the sequence field
    of an ir_asset record (sequence field takes the previous priority value).
    This is obviously not sufficient enough to express the same bundle
    construction order.

    Also, subsequent module upgrade (they are always upgraded after base)
    may have created some other ir_asset records which were not available at the
    time the post upgrade migration script of the base module was run. Thus the
    knowledge available was incomplete to express a coherent bundle construction
    order.

    Given the previous paragraphs, we came to the conclusion that a pass should
    be done after the whole upgrade process to reorder some ir_asset records.

    Thus the following query is an effort to ensure that, within a given bundle,
    ir_asset records targeting some other asset will be applied in a
    coherent order by modifying their sequences s.t. a targeting ir_asset record
    comes after its target. Also, if the target is not found in the other
    ir_asset records, we assume that it must be found in the manifests and thus
    we instead ensure that this record's sequence will be applied after the
    assets definition from the manifests by adding at least the DEFAULT_SEQUENCE
    value to its sequence.
    (see DEFAULT_SEQUENCE in odoo.addons.base.models.ir_asset)

    Disclaimer: it can subsist somewhere into the wild some wizardrical
                use cases that may fail to migrate properly.
    """

    # TODO: remove this horror
    path_column = "path"
    if util.column_exists(cr, "ir_asset", "glob"):
        path_column = "glob"

    join_conditions = [
        f"src.target = target.{path_column}",
        "src.bundle = target.bundle",
        "src.id != target.id",
    ]
    more_fields = []

    has_website = util.column_exists(cr, "ir_asset", "website_id")
    if has_website:
        more_fields.append("website_id")
        join_conditions.append(
            """
            (
                target.website_id IS NULL
             OR src.website_id = target.website_id
            )
            """
        )

    query = f"""
-- -------------------------------------------------------------------------------------------------
-- 1. normalized_ir_asset = all ir_asset records but normalized
-- -------------------------------------------------------------------------------------------------
-- NB: we use WITH RECURSIVE though only the second CTE is recursive. This is a pgsql requirement.
WITH RECURSIVE normalized_ir_asset AS (
    -- Applied normalizations:
    --     -> [target] and [{path_column}] will never starts with the '/' separator
    --     -> records with 'remove' [directive] will be treated as any directive having a [target]
    -- (this CTE is not recursive)
    SELECT
        id,
        sequence,
        bundle,
        CASE WHEN directive = 'remove'
            THEN NULL
            ELSE ARRAY_TO_STRING(ARRAY_REMOVE(STRING_TO_ARRAY({path_column}, '/'), ''), '/')
        END AS {path_column},
        CASE WHEN directive = 'remove'
            THEN ARRAY_TO_STRING(ARRAY_REMOVE(STRING_TO_ARRAY({path_column}, '/'), ''), '/')
            ELSE ARRAY_TO_STRING(ARRAY_REMOVE(STRING_TO_ARRAY(target, '/'), ''), '/')
        END AS target
        {','.join(["", *more_fields])}
    FROM ir_asset
)

-- -------------------------------------------------------------------------------------------------
-- 2. ir_asset_to_update = all ir_asset records having targets + their new_sequence to update
-- -------------------------------------------------------------------------------------------------
, ir_asset_to_update AS (
    -- Initial term: all ir_asset having a target that
    -- either points to another ir_asset without target
    --     or points to an unknown asset line (i.e. in the manifests)
    SELECT src.id,
           COALESCE(target.sequence, {DEFAULT_SEQUENCE}) + src.sequence AS new_sequence,
           src.bundle,
           src.{path_column}
           {',src.'.join(["", *more_fields])}
      FROM normalized_ir_asset src
 LEFT JOIN normalized_ir_asset target ON {' AND '.join(join_conditions)}
     WHERE src.target IS NOT NULL
       AND target.target IS NULL

    -- Recursive term: all ir_asset targeting an ir_asset in the recursive set
    UNION DISTINCT
    SELECT src.id,
           target.new_sequence + src.sequence AS new_sequence,
           src.bundle,
           src.{path_column}
           {',src.'.join(["", *more_fields])}
      FROM normalized_ir_asset src
      JOIN ir_asset_to_update target ON {' AND '.join(join_conditions)}
)

-- -------------------------------------------------------------------------------------------------
-- 3. perform the actual ir_asset update based on the ir_asset_to_update CTE
-- -------------------------------------------------------------------------------------------------
UPDATE ir_asset
   SET sequence = ir_asset_to_update.new_sequence
  FROM ir_asset_to_update
 WHERE ir_asset.id = ir_asset_to_update.id;
    """

    cr.execute(query)
