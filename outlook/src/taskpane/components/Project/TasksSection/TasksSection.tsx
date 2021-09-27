import * as React from 'react';
import Partner from '../../../../classes/Partner';
import Project from '../../../../classes/Project';
import Task from '../../../../classes/Task';
import { ContentType, HttpVerb, sendHttpRequest } from '../../../../utils/httpRequest';
import { _t } from '../../../../utils/Translator';
import CollapseSection from '../../CollapseSection/CollapseSection';
import TaskListItem from '../TaskList/TaskListItem';
import api from '../../../api';
import AppContext from '../../AppContext';
import { Callout, DirectionalHint } from 'office-ui-fabric-react';
import SelectProjectDropdown from './SelectProjectDropdown';

type TasksSectionProps = {
    partner: Partner;
};

type TasksSectionState = {
    tasks: Task[];
    isCollapsed: boolean;
    isProjectCalloutOpen: boolean;
};

class TasksSection extends React.Component<TasksSectionProps, TasksSectionState> {
    constructor(props, context) {
        super(props, context);
        const isCollapsed = !props.partner.tasks || !props.partner.tasks.length;
        this.state = {
            tasks: this.props.partner.tasks,
            isCollapsed: isCollapsed,
            isProjectCalloutOpen: false,
        };
    }

    private toggleProjectCallout = () => {
        this.setState({ isProjectCalloutOpen: !this.state.isProjectCalloutOpen });
    };

    private closeProjectCallout = () => {
        this.setState({ isProjectCalloutOpen: false });
    };

    private onProjectSelected = (project: Project): void => {
        this.closeProjectCallout();
        this.createTask(project);
    };

    private createTask = (project: Project) => {
        Office.context.mailbox.item.body.getAsync(Office.CoercionType.Html, async (result) => {
            const message = result.value.split('<div id="x_appendonsend"></div>')[0]; // Remove the history and only log the most recent message.
            const subject = Office.context.mailbox.item.subject;

            const taskValues = {
                partner_id: this.props.partner.id,
                email_body: message,
                email_subject: subject,
                project_id: project.id,
            };

            let response = null;
            try {
                response = await sendHttpRequest(
                    HttpVerb.POST,
                    api.baseURL + api.createTask,
                    ContentType.Json,
                    this.context.getConnectionToken(),
                    taskValues,
                    true,
                ).promise;
            } catch (error) {
                this.context.showHttpErrorMessage(error);
                return;
            }

            const parsed = JSON.parse(response);
            if (parsed['error']) {
                this.context.showTopBarMessage();
                return;
            }
            const cids = this.context.getUserCompaniesString();
            const action = 'project_mail_plugin.project_task_action_form_edit';
            const url = `${api.baseURL}/web#action=${action}&id=${parsed.result.task_id}&model=project.task&view_type=form${cids}`;
            window.open(url);
        });
    };

    private getTasks = () => {
        if (!this.props.partner.isAddedToDatabase()) {
            return <div className="list-text">{_t('Save Contact to create new Tasks.')}</div>;
        } else if (this.state.tasks.length > 0) {
            const tasksContent = this.state.tasks.map((task) => <TaskListItem task={task} key={task.id} />);
            return <div className="section-content">{tasksContent}</div>;
        }

        return <div className="section-content list-text">{_t('No tasks found for this contact.')}</div>;
    };

    render() {
        const title = this.state.tasks ? _t('Tasks (%(count)s)', { count: this.state.tasks.length }) : _t('Tasks');

        return (
            <>
                <CollapseSection
                    className="collapse-task-section"
                    isCollapsed={this.state.isCollapsed}
                    title={title}
                    hasAddButton={this.props.partner.isAddedToDatabase()}
                    onAddButtonClick={this.toggleProjectCallout}>
                    {this.getTasks()}
                </CollapseSection>
                {this.state.isProjectCalloutOpen && (
                    <Callout
                        directionalHint={DirectionalHint.bottomRightEdge}
                        directionalHintFixed={true}
                        onDismiss={() => this.setState({ isProjectCalloutOpen: false })}
                        preventDismissOnScroll={true}
                        setInitialFocus={true}
                        doNotLayer={true}
                        gapSpace={0}
                        role="alertdialog"
                        target=".collapse-task-section .collapse-section-button">
                        <SelectProjectDropdown partner={this.props.partner} onProjectClick={this.onProjectSelected} />
                    </Callout>
                )}
            </>
        );
    }
}

TasksSection.contextType = AppContext;
export default TasksSection;
