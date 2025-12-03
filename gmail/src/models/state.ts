import { Email } from "./email";
import { Partner } from "./partner";
import { Project } from "./project";
import { ErrorMessage } from "./error_message";
import { getAccessToken, getOdooAuthUrl } from "../services/odoo_auth";
import { getOdooServerUrl } from "src/services/app_properties";

/**
 * Object which contains all data for the application.
 *
 * In App-Script, all event handlers are function and not method. We can only pass string
 * as arguments. So this object is serialized, then given to the event handler and then
 * unserialize to retrieve the original object.
 *
 * That's how we manage the state of the application without performing a big amount of
 * read / write in the cache.
 */

export class State {
    // Contact of the current card
    partner: Partner;
    canCreatePartner: boolean;
    // Opened email with headers
    email: Email;
    // Searched partners in the search view
    searchedPartners: Partner[];
    // Searched projects in the search view
    searchedProjects: Project[];
    canCreateProject: boolean;

    constructor(
        partner: Partner,
        canCreatePartner: boolean,
        email: Email,
        partners: Partner[],
        searchedProjects: Project[],
        canCreateProject: boolean,
    ) {
        this.partner = partner;
        this.canCreatePartner = canCreatePartner;
        this.email = email;
        this.searchedPartners = partners;
        this.searchedProjects = searchedProjects;
        this.canCreateProject = canCreateProject;
    }

    toJson(): string {
        return JSON.stringify(this);
    }

    /**
     * Unserialize the state object (reverse JSON.stringify).
     */
    static fromJson(json: string): State {
        const values = JSON.parse(json);

        const partnerValues = values.partner || {};
        const canCreatePartner = values.canCreatePartner;
        const emailValues = values.email || {};
        const errorValues = values.error || {};
        const partnersValues = values.searchedPartners;
        const projectsValues = values.searchedProjects;
        const canCreateProject = values.canCreateProject;

        const partner = Partner.fromJson(partnerValues);
        const email = Email.fromJson(emailValues);
        const error = ErrorMessage.fromJson(errorValues);
        const searchedPartners = partnersValues
            ? partnersValues.map((partnerValues: any) => Partner.fromJson(partnerValues))
            : null;
        const searchedProjects = projectsValues
            ? projectsValues.map((projectValues: any) => Project.fromJson(projectValues))
            : null;

        return new State(
            partner,
            canCreatePartner,
            email,
            searchedPartners,
            searchedProjects,
            canCreateProject,
        );
    }

    /**
     * Cache / user properties management.
     *
     * Introduced with static getter / setter because they are shared between all the
     * application cards.
     */
    static get accessToken() {
        const accessToken = getAccessToken();
        return accessToken?.length && accessToken;
    }

    static get isLogged(): boolean {
        return !!this.accessToken;
    }

    /**
     * Return the URL require to login to the Odoo database.
     */
    static get odooLoginUrl(): string {
        const loginUrl = getOdooAuthUrl();
        return loginUrl?.length && loginUrl;
    }

    /**
     * Dictionary which inform us on which record we already logged the email.
     * So the user can not log 2 times the same email on the same record.
     * This is stored into the cache, so we don't need to modify the Odoo models.
     *
     * Note: the cache expire after 6 hours.
     *
     * Returns:
     *     {
     *         "partners": [3, 6], // email already logged on the partner 3 and 6
     *         "leads": [7, 14],
     *     }
     */
    static getLoggingState(messageId: string) {
        const cache = CacheService.getUserCache();
        const loggingStateStr = cache.get(
            "ODOO_LOGGING_STATE_" + getOdooServerUrl() + "_" + messageId,
        );

        const defaultValues: Record<string, number[]> = {
            "res.partner": [],
            "crm.lead": [],
            "helpdesk.ticket": [],
            "project.task": [],
        };

        if (!loggingStateStr || !loggingStateStr.length) {
            return defaultValues;
        }
        return { ...defaultValues, ...JSON.parse(loggingStateStr) };
    }

    /**
     * Save the fact that we logged the email on the record, in the cache.
     *
     * Returns:
     *     True if the record was not yet marked as "logged"
     *     False if we already logged the email on the record
     */
    static setLoggingState(messageId: string, res_model: string, res_id: number): boolean {
        const loggingState = this.getLoggingState(messageId);
        if (loggingState[res_model].indexOf(res_id) < 0) {
            loggingState[res_model].push(res_id);
            const cache = CacheService.getUserCache();

            // The cache key depend on the current email open and on the Odoo database
            const cacheKey = "ODOO_LOGGING_STATE_" + getOdooServerUrl() + "_" + messageId;

            cache.put(
                cacheKey,
                JSON.stringify(loggingState),
                21600, // 6 hours, maximum cache life time
            );
            return true;
        }
        return false;
    }

    /**
     * Check if the email has not been logged on the record.
     *
     * Returns:
     *     True if the record was not yet marked as "logged"
     *     False if we already logged the email on the record
     */
    static checkLoggingState(messageId: string, res_model: string, res_id: number): boolean {
        const loggingState = this.getLoggingState(messageId);
        return loggingState[res_model].indexOf(res_id) < 0;
    }
}
