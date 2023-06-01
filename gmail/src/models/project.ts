import { postJsonRpc } from "../utils/http";
import { URLS } from "../const";
import { ErrorMessage } from "../models/error_message";
import { getAccessToken } from "src/services/odoo_auth";

/**
 * Represent a "project.project" record.
 */
export class Project {
    id: number;
    name: string;
    partnerName: string;

    /**
     * Unserialize the project object (reverse JSON.stringify).
     */
    static fromJson(values: any): Project {
        const project = new Project();
        project.id = values.id;
        project.name = values.name;
        project.partnerName = values.partnerName;
        return project;
    }

    /**
     * Parse the dictionary return by the Odoo endpoint.
     */
    static fromOdooResponse(values: any): Project {
        const project = new Project();
        project.id = values.project_id;
        project.name = values.name;
        project.partnerName = values.partner_name;
        return project;
    }

    /**
     * Make a RPC call to the Odoo database to search a project.
     */
    static searchProject(query: string): [Project[], ErrorMessage] {
        const url = PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") + URLS.SEARCH_PROJECT;
        const odooAccessToken = getAccessToken();

        const response = postJsonRpc(url, { search_term: query }, { Authorization: "Bearer " + odooAccessToken });

        if (!response) {
            return [[], new ErrorMessage("http_error_odoo")];
        }

        return [response.map((values: any) => Project.fromOdooResponse(values)), new ErrorMessage()];
    }

    /**
     * Make a RPC call to the Odoo database to create a project
     * and return the newly created record.
     */
    static createProject(name: string): Project {
        const url = PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") + URLS.CREATE_PROJECT;
        const odooAccessToken = getAccessToken();

        const response = postJsonRpc(url, { name: name }, { Authorization: "Bearer " + odooAccessToken });

        const projectId = response ? response.project_id || null : null;
        if (!projectId) {
            return null;
        }

        return Project.fromJson({
            id: projectId,
            name: response.name,
        });
    }
}
