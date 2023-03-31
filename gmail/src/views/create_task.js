function onSearchProjectClick(state, parameters, inputs) {
    var inputQuery = inputs.search_project_query;
    var query = (inputQuery && inputQuery.length && inputQuery[0]) || "";
    var _a = Project.searchProject(query),
        projects = _a[0],
        error = _a[1];
    state.error = error;
    state.searchedProjects = projects;
    var createTaskView = buildCreateTaskView(state, query, true);
    // If go back, show again the "Create Project" section, but do not show all old searches
    return parameters.hideCreateProjectSection ? (0, updateCard)(createTaskView) : (0, pushCard)(createTaskView);
}
function onCreateProjectClick(state, parameters, inputs) {
    var inputQuery = inputs.new_project_name;
    var projectName = (inputQuery && inputQuery.length && inputQuery[0]) || "";
    if (!projectName || !projectName.length) {
        return (0, notify)((0, _t)("The project name is required"));
    }
    var project = Project.createProject(projectName);
    if (!project) {
        return (0, notify)((0, _t)("Could not create the project"));
    }
    return onSelectProject(state, { project: project });
}
function onSelectProject(state, parameters) {
    var project = Project.fromJson(parameters.project);
    var task = Task.createTask(state.partner.id, project.id, state.email.body, state.email.subject);
    if (!task) {
        return (0, notify)((0, _t)("Could not create the task"));
    }
    task.projectName = project.name;
    state.partner.tasks.push(task);
    var taskUrl =
        State.odooServerUrl +
        "/web#id=".concat(
            task.id,
            "&action=project_mail_plugin.project_task_action_form_edit&model=project.task&view_type=form",
        );
    // Open the URL to the Odoo task and update the card
    return CardService.newActionResponseBuilder()
        .setOpenLink(CardService.newOpenLink().setUrl(taskUrl))
        .setNavigation((0, pushToRoot)((0, buildView)(state)))
        .build();
}
function buildCreateTaskView(state, query, hideCreateProjectSection) {
    var _a;
    if (query === void 0) {
        query = "";
    }
    if (hideCreateProjectSection === void 0) {
        hideCreateProjectSection = false;
    }
    var noProject = false;
    if (!state.searchedProjects) {
        // Initiate the search
        (_a = Project.searchProject("")), (state.searchedProjects = _a[0]), (state.error = _a[1]);
        noProject = !state.searchedProjects.length;
    }
    var odooServerUrl = State.odooServerUrl;
    var partner = state.partner;
    var tasks = partner.tasks;
    var projects = state.searchedProjects;
    var card = CardService.newCardBuilder();
    if (!noProject) {
        var projectSection = CardService.newCardSection().setHeader(
            "<b>" + (0, _t)("Create a Task in an existing Project") + "</b>",
        );
        projectSection.addWidget(
            CardService.newTextInput()
                .setFieldName("search_project_query")
                .setTitle((0, _t)("Search a Project"))
                .setValue(query || "")
                .setOnChangeAction(
                    (0, actionCall)(state, "onSearchProjectClick", {
                        hideCreateProjectSection: hideCreateProjectSection,
                    }),
                ),
        );
        projectSection.addWidget(
            CardService.newTextButton()
                .setText((0, _t)("Search"))
                .setOnClickAction(
                    (0, actionCall)(state, "onSearchProjectClick", {
                        hideCreateProjectSection: hideCreateProjectSection,
                    }),
                ),
        );
        if (!projects.length) {
            projectSection.addWidget(CardService.newTextParagraph().setText((0, _t)("No project found.")));
        }
        for (var _i = 0, projects_1 = projects; _i < projects_1.length; _i++) {
            var project = projects_1[_i];
            var projectCard = (0, createKeyValueWidget)(
                null,
                project.name,
                null,
                project.partnerName,
                null,
                (0, actionCall)(state, "onSelectProject", { project: project }),
            );
            projectSection.addWidget(projectCard);
        }
        card.addSection(projectSection);
    }
    if (!hideCreateProjectSection && state.canCreateProject) {
        var createProjectSection = CardService.newCardSection().setHeader(
            "<b>" + (0, _t)("Create a Task in a new Project") + "</b>",
        );
        createProjectSection.addWidget(
            CardService.newTextInput()
                .setFieldName("new_project_name")
                .setTitle((0, _t)("Project Name"))
                .setValue(""),
        );
        createProjectSection.addWidget(
            CardService.newTextButton()
                .setText((0, _t)("Create Project & Task"))
                .setOnClickAction((0, actionCall)(state, "onCreateProjectClick")),
        );
        card.addSection(createProjectSection);
    } else if (noProject) {
        var noProjectSection = CardService.newCardSection();
        noProjectSection.addWidget(CardService.newImage().setImageUrl(UI_ICONS.empty_folder));
        noProjectSection.addWidget(CardService.newTextParagraph().setText("<b>" + (0, _t)("No project") + "</b>"));
        noProjectSection.addWidget(
            CardService.newTextParagraph().setText(
                (0, _t)("There are no project in your database. Please ask your project manager to create one."),
            ),
        );
        card.addSection(noProjectSection);
    }
    return card.build();
}
