import { Company } from "./company";
import { Lead } from "./lead";
import { Task } from "./task";
import { Ticket } from "./ticket";
import { postJsonRpc, postJsonRpcCached } from "../utils/http";
import { URLS } from "../const";
import { State } from "../models/state";
import { ErrorMessage } from "../models/error_message";

/**
 * Represent the current partner and all the information about him.
 */
export class Partner {
    id: number;
    name: string;
    email: string;

    image: string;
    isCompany: boolean;
    phone: string;
    mobile: string;

    company: Company;
    leads: Lead[];
    tickets: Ticket[];
    tasks: Task[];

    /**
     * Unserialize the partner object (reverse JSON.stringify).
     */
    static fromJson(values: any): Partner {
        const partner = new Partner();

        partner.id = values.id;
        partner.name = values.name;
        partner.email = values.email;

        partner.image = values.image;
        partner.isCompany = values.isCompany;
        partner.phone = values.phone;
        partner.mobile = values.mobile;

        partner.company = values.company ? Company.fromJson(values.company) : null;

        partner.leads = values.leads ? values.leads.map((leadValues: any) => Lead.fromJson(leadValues)) : null;

        partner.tickets = values.tickets
            ? values.tickets.map((ticketValues: any) => Ticket.fromJson(ticketValues))
            : null;

        partner.tasks = values.tasks ? values.tasks.map((taskValues: any) => Task.fromJson(taskValues)) : null;
        return partner;
    }

    static fromOdooResponse(values: any): Partner {
        const partner = new Partner();

        if (values.id && values.id > 0) {
            partner.id = values.id;
        }
        partner.name = values.name;
        partner.email = values.email;

        partner.image = values.image ? "data:image/png;base64," + values.image : null;
        partner.isCompany = values.is_company;
        partner.phone = values.phone;
        partner.mobile = values.mobile;

        if (values.company && values.company.id && values.company.id > 0) {
            partner.company = Company.fromOdooResponse(values.company);
        }

        return partner;
    }
    /**
     * Try to find information about the given email /name.
     *
     * If we are not logged to an Odoo database, enrich the email domain with IAP.
     * Otherwise fetch the partner on the user database.
     */
    static enrichPartner(email: string, name: string): [Partner, number[], ErrorMessage] {
        const odooServerUrl = State.odooServerUrl;
        const odooAccessToken = State.accessToken;

        if (odooServerUrl && odooAccessToken) {
            return this.getPartner(email, name);
        } else {
            const [partner, error] = this._enrichFromIap(email, name);
            return [partner, null, error];
        }
    }

    /**
     * Extract the email domain and send a request to IAP
     * to find information about the company.
     */
    static _enrichFromIap(email: string, name: string): [Partner, ErrorMessage] {
        const odooSharedSecret = State.odooSharedSecret;
        const userEmail = Session.getEffectiveUser().getEmail();

        const senderDomain = email.split("@").pop();

        const response = postJsonRpcCached(URLS.IAP_COMPANY_ENRICHMENT, {
            email: userEmail,
            domain: senderDomain,
            secret: odooSharedSecret,
        });

        const error = new ErrorMessage();
        if (!response) {
            error.setError("http_error_iap");
        } else if (response.error && response.error.length) {
            error.setError(response.error);
        }

        const partner = new Partner();
        partner.name = name;
        partner.email = email;

        if (response && response.name) {
            partner.company = Company.fromIapResponse(response);
        }

        return [partner, error];
    }

    /**
     * Create a "res.partner" with the given values in the Odoo database.
     */
    static savePartner(partnerValues: any): number {
        const url = State.odooServerUrl + URLS.PARTNER_CREATE;
        const accessToken = State.accessToken;

        const response = postJsonRpc(url, partnerValues, {
            Authorization: "Bearer " + accessToken,
        });

        return response && response.id;
    }

    /**
     * Fetch the given partner on the Odoo database and return all information about him.
     */
    static getPartner(email: string, name: string, partnerId: number = null): [Partner, number[], ErrorMessage] {
        const url = State.odooServerUrl + URLS.GET_PARTNER;
        const accessToken = State.accessToken;

        const response = postJsonRpc(
            url,
            { email: email, name: name, partner_id: partnerId },
            { Authorization: "Bearer " + accessToken },
        );

        if (!response || !response.partner) {
            const error = new ErrorMessage("http_error_odoo");
            const partner = Partner.fromJson({ name: name, email: email });
            return [partner, null, error];
        }

        const error = new ErrorMessage();

        if (response.enrichment_info && response.enrichment_info.type) {
            error.setError(response.enrichment_info.type, response.enrichment_info.info);
        } else if (response.partner.enrichment_info && response.partner.enrichment_info.type) {
            error.setError(response.partner.enrichment_info.type, response.partner.enrichment_info.info);
        }

        const partner = Partner.fromOdooResponse(response.partner);

        // Parse leads
        if (response.leads) {
            partner.leads = response.leads.map((leadValues: any) => Lead.fromOdooResponse(leadValues));
        }

        // Parse tickets
        if (response.tickets) {
            partner.tickets = response.tickets.map((ticketValues: any) => Ticket.fromOdooResponse(ticketValues));
        }

        // Parse tasks
        if (response.tasks) {
            partner.tasks = response.tasks.map((taskValues: any) => Task.fromOdooResponse(taskValues));
        }

        const odooUserCompanies = response.user_companies || null;

        return [partner, odooUserCompanies, error];
    }

    /**
     * Perform a search on the Odoo database and return the list of matched partners.
     */
    static searchPartner(query: string): [Partner[], ErrorMessage] {
        const url = State.odooServerUrl + URLS.SEARCH_PARTNER;
        const accessToken = State.accessToken;

        const response = postJsonRpc(url, { search_term: query }, { Authorization: "Bearer " + accessToken });

        if (!response || !response.partners) {
            return [[], new ErrorMessage("http_error_odoo")];
        }

        return [response.partners.map((values: any) => Partner.fromOdooResponse(values)), new ErrorMessage()];
    }

    /**
     * Manually enrich the given partner.
     */
    static enrichCompany(partnerId: number): [Company, ErrorMessage] {
        const url = State.odooServerUrl + URLS.ENRICH_COMPANY;
        const accessToken = State.accessToken;

        const response = postJsonRpc(url, { partner_id: partnerId }, { Authorization: "Bearer " + accessToken });

        if (!response) {
            return [null, new ErrorMessage("http_error_odoo")];
        }

        if (response.error) {
            return [null, new ErrorMessage("unknown", response.error)];
        }

        let error = new ErrorMessage();

        if (response.enrichment_info && response.enrichment_info.type) {
            error.setError(response.enrichment_info.type, response.enrichment_info.info);
        }

        if (error.code) {
            error.canCreateCompany = false;
        }

        const company = response.company ? Company.fromOdooResponse(response.company) : null;
        return [company, error];
    }
}
