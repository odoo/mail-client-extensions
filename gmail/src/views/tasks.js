function onCreateTask(state) {
    return (0, buildCreateTaskView)(state);
}
function onLogEmailOnTask(state, parameters) {
    var taskId = parameters.taskId;
    if (State.checkLoggingState(state.email.messageId, "tasks", taskId)) {
        (0, logEmail)(taskId, "project.task", state.email);
        if (!state.error.code) {
            State.setLoggingState(state.email.messageId, "tasks", taskId);
        }
        return (0, updateCard)((0, buildView)(state));
    }
    return (0, notify)((0, _t)("Email already logged on the task"));
}
function onEmailAlreradyLoggedOnTask() {
    return (0, notify)((0, _t)("Email already logged on the task"));
}
function buildTasksView(state, card) {
    var odooServerUrl = State.odooServerUrl;
    var partner = state.partner;
    var tasks = partner.tasks;
    if (!tasks) {
        return;
    }
    var loggingState = State.getLoggingState(state.email.messageId);
    var tasksSection = CardService.newCardSection().setHeader("<b>" + (0, _t)("Tasks (%s)", tasks.length) + "</b>");
    var cids = state.odooCompaniesParameter;
    if (state.partner.id) {
        tasksSection.addWidget(
            CardService.newTextButton()
                .setText((0, _t)("Create"))
                .setOnClickAction((0, actionCall)(state, "onCreateTask")),
        );
        for (var _i = 0, tasks_1 = tasks; _i < tasks_1.length; _i++) {
            var task = tasks_1[_i];
            var taskButton = null;
            if (loggingState["tasks"].indexOf(task.id) >= 0) {
                taskButton = CardService.newImageButton()
                    .setAltText((0, _t)("Email already logged on the task"))
                    .setIconUrl(UI_ICONS.email_logged)
                    .setOnClickAction((0, actionCall)(state, "onEmailAlreradyLoggedOnTask"));
            } else {
                taskButton = CardService.newImageButton()
                    .setAltText((0, _t)("Log the email on the task"))
                    .setIconUrl(UI_ICONS.email_in_odoo)
                    .setOnClickAction(
                        (0, actionCall)(state, "onLogEmailOnTask", {
                            taskId: task.id,
                        }),
                    );
            }
            tasksSection.addWidget(
                (0, createKeyValueWidget)(
                    task.projectName,
                    (0, truncate)(task.name, 35),
                    null,
                    null,
                    taskButton,
                    odooServerUrl + "/web#id=".concat(task.id, "&model=project.task&view_type=form").concat(cids),
                ),
            );
        }
    } else if (state.canCreatePartner) {
        tasksSection.addWidget(
            CardService.newTextParagraph().setText((0, _t)("Save the contact to create new tasks.")),
        );
    } else {
        tasksSection.addWidget(
            CardService.newTextParagraph().setText((0, _t)("The Contact needs to exist to create Task.")),
        );
    }
    card.addSection(tasksSection);
    return card;
}
