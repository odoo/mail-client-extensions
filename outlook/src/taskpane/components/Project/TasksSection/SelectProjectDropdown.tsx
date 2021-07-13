import {Spinner, SpinnerSize, TextField} from "office-ui-fabric-react";
import * as React from "react";
import Partner from "../../../../classes/Partner";
import Project from "../../../../classes/Project";
import {ContentType, HttpVerb, sendHttpRequest} from "../../../../utils/httpRequest";
import {OdooTheme} from "../../../../utils/Themes";
import {_t} from "../../../../utils/Translator";
import api from "../../../api";
import "./SelectProjectDropdown.css";
import AppContext from '../../AppContext';

type ProjectDialogProps = {
    partner: Partner;
    onProjectClick: (project: Project) => void;
}

type ProjectDialogState = {
    query: string;
    isLoading: boolean;
    projects: Project[];
}

class SelectProjectDropdown extends React.Component<ProjectDialogProps, ProjectDialogState> {

    constructor(props, context) {
        super(props, context);
        this.state = {query: "", isLoading: false, projects: []};
    }

    private projectsRequest;

    private onQueryChanged = (event) => {
        let query = event.target.value;
        this.setState({query: query});
        this.cancelProjectsRequest();
        if (query.length > 0) {
            this.getProjectsRequest(query);
        } else {
            this.setState({isLoading: false, projects: []});
        }
    }

    private cancelProjectsRequest = () => {
        if (this.projectsRequest)
            this.projectsRequest.cancel();
    };

    private getProjectsRequest = (searchTerm: string) => {

        if (searchTerm.length > 0) {
            this.setState({isLoading: true});

            this.projectsRequest = sendHttpRequest(HttpVerb.POST,
                api.baseURL + api.searchProject, ContentType.Json,
                this.context.getConnectionToken(), {search_term: searchTerm}, true);

            this.context.addRequestCanceller(this.projectsRequest.cancel);

            this.projectsRequest.promise.then(response => {
                const parsed = JSON.parse(response);
                let projects = []
                if (parsed.result.length > 0)
                    projects = parsed.result.map(project_json => Project.fromJson(project_json));
                this.setState({projects: projects, isLoading: false});
            }).catch((error) => {
                if (error) {
                    this.setState({isLoading: false, projects: []});
                    this.context.showHttpErrorMessage(error);
                }
            });
        }

    }

    private createProject = () => {

        const createProjectRequest = sendHttpRequest(HttpVerb.POST,
            api.baseURL + api.createProject, ContentType.Json,
            this.context.getConnectionToken(), {name: this.state.query}, true);

        this.setState({isLoading: true});

        createProjectRequest.promise.then((response) => {
            const parsed = JSON.parse(response);
            const createdProject = Project.fromJson(parsed.result);
            this.props.onProjectClick(createdProject);
        }).catch((error) => {
            if (error) {
                this.setState({isLoading: false, projects: []});
                this.context.showHttpErrorMessage(error);
                this.setState({isLoading: false});
            }
        });
    }

    render() {

        let searchBar = (
            <div className="project-search-bar">
                <TextField className="input-search" placeholder={_t('Search Projects...')}
                           onChange={this.onQueryChanged} value={this.state.query} autoComplete="off"
                           onFocus={(e) => e.target.select()}
                />
            </div>
        );

        let projects = null;
        if (this.state.isLoading) {
            projects = (
                <Spinner theme={OdooTheme}
                         size={SpinnerSize.large}
                         className="project-result-spinner"/>
            );
        } else {
            let createProjectDiv = (
                <div className="create-project-text" onClick={() => {
                    this.createProject()
                }}>
                    {_t("Create %(name)s", {name: this.state.query})}
                </div>
            );
            if (this.state.projects.length > 0) {
                if (this.state.projects.filter(project =>
                    project.name.toUpperCase() === this.state.query.toUpperCase()).length > 0) {
                    createProjectDiv = null;
                }

                let projectsList = this.state.projects.map(project => {
                    return (
                        <div key={project.id} className="project-search-result-text"
                             onClick={() => this.props.onProjectClick(project)}>
                            {project.name}
                        </div>
                    )
                })
                projects = (
                    <div>
                        {projectsList}
                        {createProjectDiv}
                    </div>);
            } else {
                if (this.state.query.length > 0) {
                    projects = (
                        <div>
                            {createProjectDiv}
                        </div>
                    );
                }
            }
        }

        return (
            <>
                <div className="project-result-container">
                    <div>
                        {_t("Pick a Project to create a Task")}
                    </div>
                    {searchBar}
                    <div style={{flex: "1"}}>
                        {projects}
                    </div>
                </div>
            </>
        )

    }

}

SelectProjectDropdown.contextType = AppContext;
export default SelectProjectDropdown;
