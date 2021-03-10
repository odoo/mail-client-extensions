import { postJsonRpc } from "../utils/http";
import { isTrue } from "../utils/format";
import { URLS } from "../const";
import { State } from "../models/state";

/**
 * Represent a "crm.lead" record.
 */
export class Lead {
    id: number;
    name: string;
    expectedRevenue: string;
    probability: number;
    recurringRevenue: string;
    recurringPlan: string;

    /**
     * Make a RPC call to the Odoo database to create a lead
     * and return the ID of the newly created record.
     */
    static createLead(partnerId: number, emailBody: string, emailSubject: string): number {
        const url = State.odooServerUrl + URLS.CREATE_LEAD;
        const accessToken = State.accessToken;

        const response = postJsonRpc(
            url,
            { email_body: emailBody, email_subject: emailSubject, partner_id: partnerId },
            { Authorization: "Bearer " + accessToken },
        );

        return response ? response.lead_id || null : null;
    }

    /**
     * Unserialize the lead object (reverse JSON.stringify).
     */
    static fromJson(values: any): Lead {
        const lead = new Lead();
        lead.id = values.id;
        lead.name = values.name;
        lead.expectedRevenue = values.expectedRevenue;
        lead.probability = values.probability;
        lead.recurringRevenue = values.recurringRevenue;
        lead.recurringPlan = values.recurringPlan;
        return lead;
    }

    /**
     * Parse the dictionary returned by the Odoo database endpoint.
     */
    static fromOdooResponse(values: any): Lead {
        const lead = new Lead();
        lead.id = values.lead_id;
        lead.name = values.name;
        lead.expectedRevenue = values.expected_revenue;
        lead.probability = values.probability;

        if (isTrue(values.recurring_revenue) && isTrue(values.recurring_plan)) {
            lead.recurringRevenue = values.recurring_revenue;
            lead.recurringPlan = values.recurring_plan;
        }

        return lead;
    }
}
