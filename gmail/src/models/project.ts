import { URLS } from "../consts";
import { ErrorMessage } from "../models/error_message";
import { postJsonRpc } from "../utils/http";
import { User } from "./user";

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
    static async searchProject(user: User, query: string): Promise<[Project[], ErrorMessage]> {
        const response = await postJsonRpc(
            user.odooUrl + URLS.SEARCH_PROJECT,
            { query },
            { Authorization: "Bearer " + user.odooToken },
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
    static async createProject(user: User, name: string): Promise<Project> {
        const response = await postJsonRpc(
            user.odooUrl + URLS.CREATE_PROJECT,
            { name: name },
            { Authorization: "Bearer " + user.odooToken },
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
