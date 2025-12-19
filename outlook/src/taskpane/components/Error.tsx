import { makeStyles } from '@fluentui/react-components'
import React from 'react'

const useStyles = makeStyles({
    container: {
        position: 'absolute',
        zIndex: '999',
        bottom: '0',
        padding: '5px 10px',
        borderRadius: '2px',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        backgroundColor: '#fafafa',
        boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
        minWidth: '200px',
        textAlign: 'center',
    },
    progress: {
        width: '100%',
        backgroundColor: '#e74c3c',
        height: '2px',
        position: 'absolute',
        left: '0',
        bottom: '0',
        animationName: {
            '0%': { width: '100%' },
            '100%': { width: '0%' },
        },
        animationDuration: '2s',
        animationTimingFunction: 'linear',
    },
})

const ErrorContext = React.createContext(null)

const ErrorProvider = ({ children }: { children: React.ReactElement }) => {
    const styles = useStyles()

    const [message, setMessage] = React.useState(null)
    const timeoutRef = React.useRef<NodeJS.Timeout | null>(null)

    const showError = (message: string) => {
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current)
        }
        setMessage(null)
        requestAnimationFrame(() => {
            // restart the animation
            setMessage(message)
        })
        timeoutRef.current = setTimeout(() => {
            setMessage(null)
            timeoutRef.current = null
        }, 2000)
    }

    return (
        <ErrorContext.Provider value={{ showError }}>
            {message && (
                <div className={styles.container}>
                    {message}
                    <div className={styles.progress} />
                </div>
            )}
            {children}
        </ErrorContext.Provider>
    )
}

export { ErrorProvider }
export default ErrorContext
