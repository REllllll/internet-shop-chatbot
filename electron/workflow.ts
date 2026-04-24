export interface EnsureWorkflowResult {
  imported: boolean
  message: string
}

interface N8nWorkflowSummary {
  id: string
  name: string
}

const WORKFLOW_NAME = 'Recommendation Pipeline'

async function parseJsonResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`n8n returned HTTP ${response.status}`)
  }
  return response.json() as Promise<T>
}

export async function ensureDefaultWorkflow(
  n8nBaseUrl: string,
  workflowJson: string,
  fetchImpl: typeof fetch = fetch
): Promise<EnsureWorkflowResult> {
  const listResponse = await fetchImpl(`${n8nBaseUrl}/rest/workflows`)
  const listPayload = await parseJsonResponse<{ data?: N8nWorkflowSummary[] }>(listResponse)
  const workflows = Array.isArray(listPayload.data) ? listPayload.data : []

  if (workflows.some((workflow) => workflow.name === WORKFLOW_NAME)) {
    return { imported: false, message: 'Default workflow already exists.' }
  }

  await importWorkflow(n8nBaseUrl, workflowJson, fetchImpl)
  return { imported: true, message: 'Default workflow imported.' }
}

export async function restoreDefaultWorkflow(
  n8nBaseUrl: string,
  workflowJson: string,
  fetchImpl: typeof fetch = fetch
): Promise<{ ok: boolean; message: string }> {
  await importWorkflow(n8nBaseUrl, workflowJson, fetchImpl)
  return { ok: true, message: 'Default workflow restored.' }
}

async function importWorkflow(n8nBaseUrl: string, workflowJson: string, fetchImpl: typeof fetch): Promise<void> {
  const workflow = JSON.parse(workflowJson)
  const response = await fetchImpl(`${n8nBaseUrl}/rest/workflows/import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ workflow }),
  })
  await parseJsonResponse(response)
}
