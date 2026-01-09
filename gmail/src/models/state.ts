import { Email } from "./email";
import { Partner } from "./partner";
import { Project } from "./project";

/**
 * Object which contains all data for the application.
 *
 * This object is serialized, then given to the event handler and then
 * unserialize to retrieve the original object.
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
    static fromJson(values: any): State {
        const partnerValues = values.partner || {};
        const canCreatePartner = values.canCreatePartner;
        const emailValues = values.email || {};
        const partnersValues = values.searchedPartners;
        const projectsValues = values.searchedProjects;
        const canCreateProject = values.canCreateProject;

        const partner = Partner.fromJson(partnerValues);
        const email = Email.fromJson(emailValues);
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
}
