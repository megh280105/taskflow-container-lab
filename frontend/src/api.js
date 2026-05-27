const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
      ...options.headers,
    },
    method: options.method || "GET",
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export async function register(payload) {
  return request("/register", { method: "POST", body: payload });
}

export async function login(payload) {
  return request("/login", { method: "POST", body: payload });
}

export async function listTasks(token) {
  return request("/tasks", { token });
}

export async function createTask(token, payload) {
  return request("/tasks", { method: "POST", token, body: payload });
}

export async function updateTask(token, taskId, payload) {
  return request(`/tasks/${taskId}`, { method: "PATCH", token, body: payload });
}
