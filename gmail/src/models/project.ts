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
    stageName: string;
    companyName: string;

    /**
     * Unserialize the project object (reverse JSON.stringify).
     */
    static fromJson(values: any): Project {
        const project = new Project();
        project.id = values.id;
        project.name = values.name;
        project.partnerName = values.partnerName;
        project.stageName = values.stageName;
        project.companyName = values.companyName;
        return project;
    }

    /**
     * Parse the dictionary return by the Odoo endpoint.
     */
    static fromOdooResponse(values: any): Project {
        const project = new Project();
        project.id = values.id;
        project.name = values.name;
        project.partnerName = values.partner_name;
        project.stageName = values.stage_name;
        project.companyName = values.company_name;
        return project;
    }

    /**
     * Make a RPC call to the Odoo database to search a project.
     */
    static searchProject(query: string): [Project[], ErrorMessage] {
        const url =
            PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") +
            URLS.SEARCH_PROJECT;
        const odooAccessToken = getAccessToken();

        const response = postJsonRpc(
            url,
            { query },
            { Authorization: "Bearer " + odooAccessToken },
        );

        if (!response?.length) {
            return [[], new ErrorMessage("http_error_odoo")];
        }

        return [
            response[0].map((values: any) => Project.fromOdooResponse(values)),
            new ErrorMessage(),
        ];
    }

    /**
     * Make a RPC call to the Odoo database to create a project
     * and return the newly created record.
     */
    static createProject(name: string): Project {
        const url =
            PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") +
            URLS.CREATE_PROJECT;
        const odooAccessToken = getAccessToken();

        const response = postJsonRpc(
            url,
            { name: name },
            { Authorization: "Bearer " + odooAccessToken },
        );

        const projectId = response ? response.id || null : null;
        if (!projectId) {
            return null;
        }

        return Project.fromJson({
            id: projectId,
            name: response.name,
        });
    }
}
