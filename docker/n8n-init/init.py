#!/usr/bin/env python3
"""Initialize n8n: setup owner, import workflow, activate workflow."""
import json
import os
import time
import urllib.error
import urllib.request

N8N_URL = os.getenv("N8N_URL", "http://n8n:5678")
OWNER_EMAIL = os.getenv("N8N_OWNER_EMAIL", "admin@example.com")
OWNER_PASSWORD = os.getenv("N8N_OWNER_PASSWORD", "Admin12345!")
OWNER_FIRST = os.getenv("N8N_OWNER_FIRST_NAME", "Admin")
OWNER_LAST = os.getenv("N8N_OWNER_LAST_NAME", "User")
WORKFLOW_PATH = os.getenv("WORKFLOW_PATH", "/workflows/recommendation-pipeline.json")
WORKFLOW_NAME = os.getenv("WORKFLOW_NAME", "Recommendation Pipeline")


def api_request(path, method="GET", data=None, headers=None):
    url = f"{N8N_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
        req.data = payload
    resp = urllib.request.urlopen(req)
    body = resp.read().decode("utf-8")
    return resp, body


def wait_for_n8n(timeout=120):
    print("Waiting for n8n to be ready...")
    for i in range(timeout):
        try:
            api_request("/rest/settings")
            print("n8n is ready.")
            return
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                print("n8n is ready (auth required).")
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("n8n did not become ready in time.")


def setup_owner():
    """Create owner account if none exists."""
    print("Setting up owner account...")
    try:
        # Try the common setup endpoint first
        api_request(
            "/rest/owner/setup",
            method="POST",
            data={
                "email": OWNER_EMAIL,
                "firstName": OWNER_FIRST,
                "lastName": OWNER_LAST,
                "password": OWNER_PASSWORD,
            },
        )
        print("Owner account created.")
        return
    except urllib.error.HTTPError as e:
        if e.code in (400, 401, 403, 409, 500):
            print("Owner may already exist or setup not allowed, proceeding.")
            return
        raise


def login():
    """Login and return auth cookie string."""
    print("Logging in...")
    payload = {"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
    try:
        resp, _ = api_request(
            "/rest/login",
            method="POST",
            data=payload,
        )
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if hasattr(e, "read") else ""
        # newer n8n expects emailOrLdapLoginId
        if "emailOrLdapLoginId" in body or "invalid_type" in body:
            try:
                resp, _ = api_request(
                    "/rest/login",
                    method="POST",
                    data={"emailOrLdapLoginId": OWNER_EMAIL, "password": OWNER_PASSWORD},
                )
            except urllib.error.HTTPError as e2:
                body2 = e2.read().decode("utf-8") if hasattr(e2, "read") else ""
                raise RuntimeError(f"Login failed: {e2.code} {body2}")
        else:
            raise RuntimeError(f"Login failed: {e.code} {body}")

    cookie = resp.headers.get("Set-Cookie", "")
    if not cookie:
        raise RuntimeError("Login succeeded but no Set-Cookie header received.")
    print("Logged in successfully.")
    return cookie


def get_workflows(cookie):
    _, body = api_request("/rest/workflows", headers={"Cookie": cookie})
    data = json.loads(body)
    # n8n response format varies by version
    if isinstance(data, dict) and "data" in data:
        return data["data"]
    return data


def import_workflow(cookie):
    print(f"Importing workflow from {WORKFLOW_PATH}...")
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    # Ensure name matches
    workflow["name"] = WORKFLOW_NAME

    # Check if workflow already exists
    workflows = get_workflows(cookie)
    for wf in workflows:
        if wf.get("name") == WORKFLOW_NAME:
            print(f"Workflow already exists with ID {wf['id']}.")
            return wf["id"]

    try:
        _, body = api_request(
            "/rest/workflows",
            method="POST",
            data=workflow,
            headers={"Cookie": cookie},
        )
        result = json.loads(body)
        wf_id = result.get("id") or result.get("data", {}).get("id")
        print(f"Workflow imported with ID {wf_id}.")
        return wf_id
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Failed to import workflow: {e.code}")


def activate_workflow(cookie, workflow_id):
    print(f"Activating workflow {workflow_id}...")
    # Fetch versionId required by newer n8n APIs
    _, body = api_request(f"/rest/workflows/{workflow_id}", headers={"Cookie": cookie})
    data = json.loads(body)
    wf = data.get("data", data)
    version_id = wf.get("versionId") or data.get("versionId")
    if not version_id:
        raise RuntimeError("Could not determine workflow versionId")

    if wf.get("active"):
        print("Workflow is already active.")
        return

    try:
        api_request(
            f"/rest/workflows/{workflow_id}/activate",
            method="POST",
            data={"versionId": version_id},
            headers={"Cookie": cookie},
        )
        print("Workflow activated.")
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("Workflow is already active (409).")
            return
        raise


def main():
    wait_for_n8n()
    setup_owner()
    cookie = login()
    wf_id = import_workflow(cookie)
    activate_workflow(cookie, wf_id)
    print("n8n initialization complete.")


if __name__ == "__main__":
    main()
