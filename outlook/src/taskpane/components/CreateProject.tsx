import { Button, Input, makeStyles } from '@fluentui/react-components'
import React, { useContext } from 'react'
import { _t } from '../../helpers/translate'
import { Project } from '../../models/project'
import ErrorContext from './Error'
import { hideGlobalLoading, showGlobalLoading } from './GlobalLoading'

export interface CreateProjectProps {
    onCreate: Function
}

const useStyles = makeStyles({
    input: {
        width: '100%',
        marginBottom: '5px',
    },
})

const CreateProject: React.FC<CreateProjectProps> = (
    props: CreateProjectProps
) => {
    const { onCreate } = props
    const showError = useContext(ErrorContext)?.showError
    const styles = useStyles()

    const [projectName, setProjectName] = React.useState('')

    const createProject = async () => {
        if (!projectName.length) {
            showError(_t('The project name is required'))
            return
        }

        showGlobalLoading()
        const project = await Project.createProject(projectName)
        hideGlobalLoading()

        if (!project) {
            showError(_t('Could not create the project'))
            return
        }
        onCreate(project)
    }

    return (
        <div>
            <h4>{_t('Create a Task in a new Project')}</h4>
            <Input
                className={styles.input}
                value={projectName}
                placeholder={_t('Project Name')}
                onChange={(e) => setProjectName(e.target.value)}
            />
            <Button onClick={createProject}>
                {_t('Create Project & Task')}
            </Button>
        </div>
    )
}

export default CreateProject
