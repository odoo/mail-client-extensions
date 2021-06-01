import { buildView } from "../views/index";
import { updateCard, pushCard, pushToRoot } from "./helpers";
import { UI_ICONS } from "./icons";
import { createKeyValueWidget, actionCall, notify } from "./helpers";
import { URLS } from "../const";
import { ErrorMessage } from "../models/error_message";
import { Project } from "../models/project";
import { State } from "../models/state";
import { Task } from "../models/task";
import { logEmail } from "../services/log_email";
import { _t } from "../services/translation";

function onSearchProjectClick(state: State, parameters: any, inputs: any) {
    const inputQuery = inputs.search_project_query;
    const query = (inputQuery && inputQuery.length && inputQuery[0]) || "";
    const [projects, error] = Project.searchProject(query);

    state.error = error;
    state.searchedProjects = projects;

    const createTaskView = buildCreateTaskView(state, query, true);

    // If go back, show again the "Create Project" section, but do not show all old searches
    return parameters.hideCreateProjectSection ? updateCard(createTaskView) : pushCard(createTaskView);
}

function onCreateProjectClick(state: State, parameters: any, inputs: any) {
    const inputQuery = inputs.new_project_name;
    const projectName = (inputQuery && inputQuery.length && inputQuery[0]) || "";

    if (!projectName || !projectName.length) {
        return notify(_t("The project name is required"));
    }

    const project = Project.createProject(projectName);
    if (!project) {
        return notify(_t("Could not create the project"));
    }

    return onSelectProject(state, { project: project });
}

function onSelectProject(state: State, parameters: any) {
    const project = Project.fromJson(parameters.project);
    const task = Task.createTask(state.partner.id, project.id, state.email.body, state.email.subject);

    if (!task) {
        return notify(_t("Could not create the task"));
    }

    task.projectName = project.name;
    state.partner.tasks.push(task);

    const taskUrl =
        State.odooServerUrl +
        `/web#id=${task.id}&action=project_mail_plugin.project_task_action_form_edit&model=project.task&view_type=form`;

    // Open the URL to the Odoo task and update the card
    return CardService.newActionResponseBuilder()
        .setOpenLink(CardService.newOpenLink().setUrl(taskUrl))
        .setNavigation(pushToRoot(buildView(state)))
        .build();
}

export function buildCreateTaskView(state: State, query: string = "", hideCreateProjectSection: boolean = false) {
    if (!state.searchedProjects) {
        // Initiate the search
        [state.searchedProjects, state.error] = Project.searchProject("");
    }

    const odooServerUrl = State.odooServerUrl;
    const partner = state.partner;
    const tasks = partner.tasks;
    const projects = state.searchedProjects;

    const card = CardService.newCardBuilder();
    const projectSection = CardService.newCardSection().setHeader(
        "<b>" + _t("Create a Task in an existing Project") + "</b>",
    );

    projectSection.addWidget(
        CardService.newTextInput()
            .setFieldName("search_project_query")
            .setTitle(_t("Search a Project"))
            .setValue(query || "")
            .setOnChangeAction(
                actionCall(state, "onSearchProjectClick", { hideCreateProjectSection: hideCreateProjectSection }),
            ),
    );

    projectSection.addWidget(
        CardService.newTextButton()
            .setText(_t("Search"))
            .setOnClickAction(
                actionCall(state, "onSearchProjectClick", { hideCreateProjectSection: hideCreateProjectSection }),
            ),
    );

    if (!projects.length) {
        projectSection.addWidget(CardService.newTextParagraph().setText(_t("No project found.")));
    }

    for (let project of projects) {
        const projectCard = createKeyValueWidget(
            null,
            project.name,
            null,
            project.partnerName,
            null,
            actionCall(state, "onSelectProject", { project: project }),
        );

        projectSection.addWidget(projectCard);
    }

    card.addSection(projectSection);

    if (!hideCreateProjectSection) {
        const createProjectSection = CardService.newCardSection().setHeader(
            "<b>" + _t("Create a Task in a new Project") + "</b>",
        );

        createProjectSection.addWidget(
            CardService.newTextInput().setFieldName("new_project_name").setTitle(_t("Project Name")).setValue(""),
        );

        createProjectSection.addWidget(
            CardService.newTextButton()
                .setText(_t("Create Project & Task"))
                .setOnClickAction(actionCall(state, "onCreateProjectClick")),
        );
        card.addSection(createProjectSection);
    }

    return card.build();
}
