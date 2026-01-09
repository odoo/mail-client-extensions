import { URLS } from "../consts";
import { postJsonRpc } from "../utils/http";
import { Email } from "./email";
import { Partner } from "./partner";
import { User } from "./user";

/**
 * Represent a "crm.lead" record.
 */
export class Lead {
    id: number;
    name: string;
    revenuesDescription: string;

    /**
     * Make a RPC call to the Odoo database to create a lead
     * and return the ID of the newly created record.
     */
    static async createLead(
        user: User,
        partner: Partner,
        email: Email,
    ): Promise<[Lead, Partner] | null> {
        const [body, _, attachmentsParsed] = await email.getBodyAndAttachments();

        const response = await postJsonRpc(
            user.odooUrl + URLS.CREATE_LEAD,
            {
                email_body: body,
                email_subject: email.subject,
                partner_id: partner.id,
                partner_email: partner.email,
                partner_name: partner.name,
                attachments: attachmentsParsed[0],
            },
            { Authorization: "Bearer " + user.odooToken },
        );

        if (!response?.id) {
            return null;
        }
        if (!partner.id) {
            partner.id = response.partner_id;
            partner.image = response.partner_image;
            partner.isWritable = true;
        }
        return [Lead.fromOdooResponse(response), partner];
    }

    /**
     * Unserialize the lead object (reverse JSON.stringify).
     */
    static fromJson(values: any): Lead {
        const lead = new Lead();
        lead.id = values.id;
        lead.name = values.name;
        lead.revenuesDescription = values.revenuesDescription;
        return lead;
    }

    /**
     * Parse the dictionary returned by the Odoo database endpoint.
     */
    static fromOdooResponse(values: any): Lead {
        const lead = new Lead();
        lead.id = values.id;
        lead.name = values.name;
        lead.revenuesDescription = values.revenues_description;
        return lead;
    }
}
