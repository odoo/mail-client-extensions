import { buildView } from "../views/index";
import { updateCard, pushToRoot } from "./helpers";
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

    return updateCard(buildCreateTaskView(state, query));
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

    return pushToRoot(buildView(state));
}

export function buildCreateTaskView(state: State, query: string = "") {
    if (!state.searchedProjects) {
        // Initiate the search
        [state.searchedProjects, state.error] = Project.searchProject("");
    }

    const odooServerUrl = State.odooServerUrl;
    const partner = state.partner;
    const tasks = partner.tasks;
    const projects = state.searchedProjects;

    const projectSection = CardService.newCardSection().setHeader(
        "<b>" + _t("Create a task from an existing project") + "</b>",
    );

    const card = CardService.newCardBuilder();

    projectSection.addWidget(
        CardService.newTextInput()
            .setFieldName("search_project_query")
            .setTitle(_t("Search an existing project"))
            .setValue(query || "")
            .setOnChangeAction(actionCall(state, "onSearchProjectClick")),
    );

    projectSection.addWidget(
        CardService.newTextButton().setText(_t("Search")).setOnClickAction(actionCall(state, "onSearchProjectClick")),
    );

    for (let project of projects) {
        const projectCard = createKeyValueWidget(
            null,
            project.name,
            UI_ICONS.project,
            null,
            null,
            actionCall(state, "onSelectProject", { project: project }),
        );

        projectSection.addWidget(projectCard);
    }

    card.addSection(projectSection);

    const newProjectSection = CardService.newCardSection()
        .setHeader("<b>" + _t("Create a task from a new project") + "</b>")
        .addWidget(
            CardService.newTextInput().setFieldName("new_project_name").setTitle(_t("Project name")).setValue(""),
        );

    newProjectSection.addWidget(
        CardService.newTextButton()
            .setText(_t("Create a new project"))
            .setOnClickAction(actionCall(state, "onCreateProjectClick")),
    );

    card.addSection(newProjectSection);

    return card.build();
}
