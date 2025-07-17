import { postJsonRpc } from "../utils/http";
import { URLS } from "../const";
import { getAccessToken } from "src/services/odoo_auth";
import { _t } from "../services/translation";
import { Partner } from "./partner";

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
    static createLead(
        partner: Partner,
        emailBody: string,
        emailSubject: string,
    ): [Lead, Partner] | null {
        const url =
            PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") + URLS.CREATE_LEAD;
        const accessToken = getAccessToken();
        const response = postJsonRpc(
            url,
            {
                email_body: emailBody,
                email_subject: emailSubject,
                partner_id: partner.id,
                partner_email: partner.email,
                partner_name: partner.name,
            },
            { Authorization: "Bearer " + accessToken },
        );

        if (!response?.id) {
            return null;
        }
        if (!partner.id) {
            partner.id = response.partner_id;
            partner.image = response.partner_image;
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
