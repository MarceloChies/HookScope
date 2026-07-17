import {type SubmitEvent, useEffect, useState} from 'react'
import './App.css'
import hookscopelogo from './assets/hookscopelogo.png'

type Endpoint = {
  id: string
  name: string
  token: string
  destination_url: string | null
  created_at: string
  contract_baseline: Record<string,unknown> | null
  duplicate_detection_enabled: boolean
}

const API_URL = 'http://127.0.0.1:8000'

function App(){
  const [endpoints, setEndpoints] = useState<Endpoint[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isCreateFormOpen, setIsCreateFormOpen] = useState(false)
  const [endpointName, setEndpointName] = useState('')
  const [destinationUrl, setDestinationUrl] = useState('')
  const [duplicateDetectionEnabled, setDuplicateDetectionEnabled] = useState(false)
  const [isCreating, setIsCreating] = useState(false)



  useEffect(() =>{
    async function loadEndpoints(){
      try {
        const response = await fetch(`${API_URL}/endpoints`)

        if(!response.ok){
          throw new Error('Could not load endpoints.')
        }
      const data: Endpoint[] = await response.json()
      setEndpoints(data)
      } catch(error){
        setErrorMessage(
          error instanceof Error ? error.message : 'An unknown error occurred.',
        )
      }finally{
        setIsLoading(false)
      }
    }

    void loadEndpoints()
  },[])

async function createEndpoint(event: SubmitEvent<HTMLFormElement>) {
  event.preventDefault()
  setIsCreating(true)
  setErrorMessage(null)

  try {
    const response = await fetch(`${API_URL}/endpoints`,{
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: endpointName,
        destination_url: destinationUrl || null,
        duplicate_detection_enabled: duplicateDetectionEnabled
      }),
    })

    if(!response.ok){
      throw new Error('Could not create endpoint.')
    }

    const createEndpoint: Endpoint = await response.json()

    setEndpoints((currentEndpoints) => [
      createEndpoint,
      ...currentEndpoints,
    ])

    setEndpointName('')
    setDestinationUrl('')
    setDuplicateDetectionEnabled(false)
    setIsCreateFormOpen(false)
  } catch (error) {
    setErrorMessage(
      error instanceof Error ? error.message : 'An unknown error occurred.',
    )
  } finally {
    setIsCreating(false)
  }
}

 return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <img className="brand-logo" src={hookscopelogo} alt="" />
          <span>HookScope</span>
        </a>

        <span className="environment">Local development</span>
      </header>

      <section className="page-heading">
        <div>
          <p className="eyebrow">Webhook endpoints</p>
          <h1>Monitor incoming events.</h1>
          <p className="subtitle">
            Inspect payloads, delivery attempts, contract changes, and duplicates.
          </p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={() => setIsCreateFormOpen(true)}
        >
          Create endpoint
        </button>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Your endpoints</h2>
            <p>{endpoints.length} configured</p>
          </div>
        </div>

        {isLoading && <p className="state-message">Loading endpoints…</p>}

        {errorMessage && (
          <p className="state-message error-message">{errorMessage}</p>
        )}

        {!isLoading && !errorMessage && endpoints.length === 0 && (
          <p className="state-message">
            No endpoints yet. Create one from the FastAPI docs for now.
          </p>
        )}

        {!isLoading && !errorMessage && endpoints.length > 0 && (
          <div className="endpoint-list">
            {endpoints.map((endpoint) => (
              <article className="endpoint-card" key={endpoint.id}>
                <div>
                  <h3>{endpoint.name}</h3>
                  <p className="destination-url">
                    {endpoint.destination_url ?? 'Inspection only — no forwarding'}
                  </p>
                </div>

                <div className="endpoint-meta">
                  <span>
                    Contract Watch:{' '}
                    {endpoint.contract_baseline ? 'enabled' : 'disabled'}
                  </span>

                  <span>
                    Duplicate detection:{' '}
                    {endpoint.duplicate_detection_enabled ? 'enabled' : 'disabled'}
                  </span>
                </div>

                <code className="webhook-url">
                  {API_URL}/hooks/{endpoint.token}
                </code>
              </article>
            ))}
          </div>
        )}
      </section>
      {isCreateFormOpen && (
        <section className="panel create-panel">
          <form className="create-form" onSubmit={createEndpoint}>
            <div className="form-field">
              <label htmlFor="endpoint-name">Endpoint name</label>
              <input
                id="endpoint-name"
                value={endpointName}
                onChange={(event) => setEndpointName(event.target.value)}
                placeholder="Stripe production"
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="destination-url">Forward to URL (optional)</label>
              <input
                id="destination-url"
                type="url"
                value={destinationUrl}
                onChange={(event) => setDestinationUrl(event.target.value)}
                placeholder="https://your-app.com/webhooks"
              />
            </div>

            <label className="checkbox-field">
              <input
                type="checkbox"
                checked={duplicateDetectionEnabled}
                onChange={(event) =>
                  setDuplicateDetectionEnabled(event.target.checked)
                }
              />
              Enable duplicate detection
            </label>

            <div className="form-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setIsCreateFormOpen(false)}
              >
                Cancel
              </button>

              <button type="submit" className="primary-button" disabled={isCreating}>
                {isCreating ? 'Creating...' : 'Create endpoint'}
              </button>
            </div>
          </form>
        </section>
      )}
    </main>
  )
}

export default App