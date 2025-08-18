from odoo.upgrade import util


def migrate(cr, version):
    # Migrate ai_agent attachments to ai_agent_source records (both binary and URL)
    cr.execute("""
        WITH emb_check AS (
            SELECT attachment_id,
                   bool_or(embedding_vector IS NULL) as has_empty
              FROM ai_embedding
          GROUP BY attachment_id
        )
        INSERT INTO ai_agent_source (
                    name, agent_id, attachment_id, url,
                    create_uid, write_uid, create_date, write_date,
                    type,
                    status,
                    is_active
                    )
             SELECT att.name, att.res_id, att.id, att.url,
                    ag.create_uid, ag.write_uid, ag.create_date, ag.write_date,
                    CASE
                        WHEN att.url IS NOT NULL AND att.url != '' THEN 'url'
                        ELSE 'binary'
                    END,
                    CASE
                        WHEN emb_check.has_empty THEN 'processing'
                        ELSE 'indexed'
                    END,
                    emb_check.has_empty IS NOT TRUE
               FROM ir_attachment att
               JOIN ai_agent ag
                 ON att.res_id = ag.id
          LEFT JOIN emb_check
                 ON att.id = emb_check.attachment_id
              WHERE att.res_model = 'ai.agent'
                AND att.res_id IS NOT NULL
        """)

    # Update attachments to point to new ai_agent_source records
    util.explode_execute(
        cr,
        """
        UPDATE ir_attachment att
           SET res_model = 'ai.agent.source',
               res_id = src.id
          FROM ai_agent_source AS src
         WHERE att.res_model = 'ai.agent'
           AND att.res_id = src.agent_id
           AND att.id = src.attachment_id
        """,
        table="ir_attachment",
        alias="att",
    )

    # Remove duplicate ai_embedding attachments based on checksum
    # Prioritize attachments with complete embeddings over incomplete ones
    cr.execute("""
        WITH emb_check AS (
            SELECT attachment_id,
                   bool_or(embedding_vector IS NULL) as has_empty
              FROM ai_embedding
          GROUP BY attachment_id
        ), dups AS (
          SELECT unnest(
                     (array_agg(att.id ORDER BY emb_check.has_empty, att.id))[2:]
                 ) AS att_id
            FROM ir_attachment att
       LEFT JOIN emb_check
              ON att.id = emb_check.attachment_id
           WHERE att.checksum IS NOT NULL
        GROUP BY att.checksum
          HAVING count(*) > 1
        )
        DELETE FROM ai_embedding e
              USING dups
              WHERE e.attachment_id = dups.att_id
    """)
