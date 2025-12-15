import { Project } from "../models/project";
import { State } from "../models/state";
import { Task } from "../models/task";
import { User } from "../models/user";
import {
    ActionCall,
    EventResponse,
    Notify,
    PopOneCardAndUpdate,
    registerEventHandler,
    UpdateCard,
} from "../utils/actions";
import {
    Button,
    ButtonsList,
    Card,
    CardSection,
    DecoratedText,
    Image,
    TextInput,
    TextParagraph,
} from "../utils/components";
import { UI_ICONS } from "./icons";
import { getPartnerView } from "./partner";

async function onSearchProjectClick(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    const query = formInputs.search_project_query || "";
    const [projects, error] = await Project.searchProject(user, query);
    if (error.code) {
        return new Notify(error.toString(_t));
    }

    state.searchedProjects = projects;
    return new UpdateCard(getCreateTaskView(state, _t, user, query));
}
registerEventHandler(onSearchProjectClick);

function onCreateProjectViewClick(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): EventResponse {
    return new UpdateCard(getCreateProjectView(state, _t));
}
registerEventHandler(onCreateProjectViewClick);

async function onCreateProjectClick(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    const projectName = formInputs.new_project_name || "";
    if (!projectName.length) {
        return new Notify(_t("The project name is required"));
    }

    const project = await Project.createProject(user, projectName);
    if (!project) {
        return new Notify(_t("Could not create the project"));
    }

    return onSelectProject(state, _t, user, { project: project }, {});
}
registerEventHandler(onCreateProjectClick);

async function onSelectProject(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    const project = Project.fromJson(args.project);
    const result = await Task.createTask(user, state.partner, project.id, state.email);

    if (!result) {
        return new Notify(_t("Could not create the task"));
    }

    const [task, partner] = result;
    state.partner = partner;
    state.partner.tasks.push(task);
    state.partner.taskCount += 1;

    return new PopOneCardAndUpdate(getPartnerView(state, _t, user));
}
registerEventHandler(onSelectProject);

export function getCreateTaskView(
    state: State,
    _t: Function,
    user: User,
    query: string = "",
    noProject: boolean = false,
): Card {
    const projects = state.searchedProjects;

    const card = new Card();

    if (!noProject) {
        const projectSection = new CardSection();
        projectSection.setHeader("<b>" + _t("Create a Task in an existing Project") + "</b>");

        projectSection.addWidget(
            new TextInput(
                "search_project_query",
                _t("Search a Project"),
                new ActionCall(state, onSearchProjectClick),
                "",
                query || "",
            ),
        );

        const actionButtonSet = new ButtonsList();
        actionButtonSet.addButton(
            new Button(_t("Search"), new ActionCall(state, onSearchProjectClick)),
        );
        if (state.canCreateProject) {
            actionButtonSet.addButton(
                new Button(
                    _t("Create Project"),
                    new ActionCall(state, onCreateProjectViewClick),
                    "#875a7b",
                ),
            );
        }
        projectSection.addWidget(actionButtonSet);

        if (!projects.length) {
            projectSection.addWidget(new TextParagraph(_t("No project found.")));
        }
        for (let project of projects) {
            const bottomLabel = [project.companyName, project.partnerName, project.stageName];
            const projectCard = new DecoratedText(
                undefined,
                project.name,
                undefined,
                bottomLabel.filter((l) => l).join(" - "),
                undefined,
                new ActionCall(state, onSelectProject, { project: project }),
            );

            projectSection.addWidget(projectCard);
        }
        card.addSection(projectSection);
    } else if (state.canCreateProject) {
        return getCreateProjectView(state, _t);
    } else {
        const noProjectSection = new CardSection();

        noProjectSection.addWidget(new Image(UI_ICONS.empty_folder));

        noProjectSection.addWidget(new TextParagraph("<b>" + _t("No project") + "</b>"));

        noProjectSection.addWidget(
            new TextParagraph(
                _t(
                    "There are no project in your database. Please ask your project manager to create one.",
                ),
            ),
        );

        card.addSection(noProjectSection);
    }

    return card;
}

/**
 * Card used to create a new project (and to create the task in that project).
 */
export function getCreateProjectView(state: State, _t: Function): Card {
    const createProjectSection = new CardSection();
    const card = new Card([createProjectSection]);

    createProjectSection.setHeader("<b>" + _t("Create a Task in a new Project") + "</b>");

    createProjectSection.addWidget(new TextInput("new_project_name", _t("Project Name")));

    createProjectSection.addWidget(
        new Button(_t("Create Project & Task"), new ActionCall(state, onCreateProjectClick)),
    );
    return card;
}
