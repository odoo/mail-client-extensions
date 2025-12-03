import { buildView } from "../views/index";
import { updateCard, pushCard, pushToRoot } from "./helpers";
import { UI_ICONS } from "./icons";
import { createKeyValueWidget, actionCall, notify } from "./helpers";
import { getOdooServerUrl } from "src/services/app_properties";
import { Project } from "../models/project";
import { State } from "../models/state";
import { Task } from "../models/task";
import { _t } from "../services/translation";
import { getOdooRecordURL } from "src/services/odoo_redirection";

function onSearchProjectClick(state: State, parameters: any, inputs: any) {
    const query = inputs.search_project_query || "";
    const [projects, error] = Project.searchProject(query);
    if (error.code) {
        return notify(error.message);
    }

    state.searchedProjects = projects;
    return updateCard(buildCreateTaskView(state, query));
}

function onCreateProjectViewClick(state: State, parameters: any, inputs: any) {
    return updateCard(buildCreateProjectView(state));
}

function onCreateProjectClick(state: State, parameters: any, inputs: any) {
    const projectName = inputs.new_project_name || "";
    if (!projectName.length) {
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
    const result = Task.createTask(state.partner, project.id, state.email);

    if (!result) {
        return notify(_t("Could not create the task"));
    }

    const [task, partner] = result;
    state.partner = partner;
    state.partner.tasks.push(task);
    state.partner.taskCount += 1;

    const taskUrl = getOdooRecordURL("project.task", task.id);
    return pushToRoot(buildView(state));
}

export function buildCreateTaskView(state: State, query: string = "") {
    let noProject = false;
    if (!state.searchedProjects) {
        // Initiate the search
        const [searchedProjects, error] = Project.searchProject("");
        if (error.code) {
            return notify(error.message);
        }

        state.searchedProjects = searchedProjects;
        noProject = !state.searchedProjects.length;
    }

    const projects = state.searchedProjects;

    const card = CardService.newCardBuilder();

    if (!noProject) {
        const projectSection = CardService.newCardSection().setHeader(
            "<b>" + _t("Create a Task in an existing Project") + "</b>",
        );

        projectSection.addWidget(
            CardService.newTextInput()
                .setFieldName("search_project_query")
                .setTitle(_t("Search a Project"))
                .setValue(query || "")
                .setOnChangeAction(actionCall(state, onSearchProjectClick.name, {})),
        );

        const actionButtonSet = CardService.newButtonSet();
        actionButtonSet.addButton(
            CardService.newTextButton()
                .setText(_t("Search"))
                .setOnClickAction(actionCall(state, onSearchProjectClick.name, {})),
        );
        if (state.canCreateProject) {
            actionButtonSet.addButton(
                CardService.newTextButton()
                    .setText(_t("Create Project"))
                    .setBackgroundColor("#875a7b")
                    .setOnClickAction(actionCall(state, onCreateProjectViewClick.name, {})),
            );
        }
        projectSection.addWidget(actionButtonSet);

        if (!projects.length) {
            projectSection.addWidget(
                CardService.newTextParagraph().setText(_t("No project found.")),
            );
        }
        for (let project of projects) {
            const bottomLabel = [project.companyName, project.partnerName, project.stageName];
            const projectCard = createKeyValueWidget(
                null,
                project.name,
                null,
                bottomLabel.filter((l) => l).join(" - "),
                null,
                actionCall(state, onSelectProject.name, { project: project }),
            );

            projectSection.addWidget(projectCard);
        }
        card.addSection(projectSection);
    } else if (state.canCreateProject) {
        return buildCreateProjectView(state);
    } else {
        const noProjectSection = CardService.newCardSection();

        noProjectSection.addWidget(CardService.newImage().setImageUrl(UI_ICONS.empty_folder));

        noProjectSection.addWidget(
            CardService.newTextParagraph().setText("<b>" + _t("No project") + "</b>"),
        );

        noProjectSection.addWidget(
            CardService.newTextParagraph().setText(
                _t(
                    "There are no project in your database. Please ask your project manager to create one.",
                ),
            ),
        );

        card.addSection(noProjectSection);
    }

    return card.build();
}

export function buildCreateProjectView(state: State) {
    const card = CardService.newCardBuilder();

    const createProjectSection = CardService.newCardSection().setHeader(
        "<b>" + _t("Create a Task in a new Project") + "</b>",
    );

    createProjectSection.addWidget(
        CardService.newTextInput()
            .setFieldName("new_project_name")
            .setTitle(_t("Project Name"))
            .setValue(""),
    );

    createProjectSection.addWidget(
        CardService.newTextButton()
            .setText(_t("Create Project & Task"))
            .setOnClickAction(actionCall(state, onCreateProjectClick.name)),
    );
    card.addSection(createProjectSection);

    return card.build();
}
