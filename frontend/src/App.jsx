import { useEffect, useState } from "react";

import { createTask, listTasks, login, register, updateTask } from "./api";

const emptyAuth = { email: "", password: "" };
const emptyTask = { title: "", description: "", dueAt: "" };

function taskPayload(form) {
  return {
    title: form.title,
    description: form.description || null,
    due_at: form.dueAt ? new Date(form.dueAt).toISOString() : null,
  };
}

export default function App() {
  const [mode, setMode] = useState("login");
  const [authForm, setAuthForm] = useState(emptyAuth);
  const [taskForm, setTaskForm] = useState(emptyTask);
  const [token, setToken] = useState(() => localStorage.getItem("taskflow-token") || "");
  const [userEmail, setUserEmail] = useState(() => localStorage.getItem("taskflow-email") || "");
  const [tasks, setTasks] = useState([]);
  const [loadingTasks, setLoadingTasks] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setTasks([]);
      return;
    }

    setLoadingTasks(true);
    setError("");
    listTasks(token)
      .then(setTasks)
      .catch((err) => {
        setError(err.message);
        if (err.message.toLowerCase().includes("authentication")) {
          handleLogout();
        }
      })
      .finally(() => setLoadingTasks(false));
  }, [token]);

  function persistSession(nextToken, nextEmail) {
    setToken(nextToken);
    setUserEmail(nextEmail);
    localStorage.setItem("taskflow-token", nextToken);
    localStorage.setItem("taskflow-email", nextEmail);
  }

  function handleLogout() {
    setToken("");
    setUserEmail("");
    localStorage.removeItem("taskflow-token");
    localStorage.removeItem("taskflow-email");
  }

  async function handleAuthSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setMessage("");

    try {
      if (mode === "register") {
        await register(authForm);
        setMode("login");
        setMessage("Account created. Sign in to continue.");
      } else {
        const result = await login(authForm);
        persistSession(result.access_token, result.user.email);
        setMessage("Signed in.");
      }
      setAuthForm(emptyAuth);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleTaskSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setMessage("");

    try {
      const created = await createTask(token, taskPayload(taskForm));
      setTasks((current) => [created, ...current]);
      setTaskForm(emptyTask);
      setMessage("Task created. If you added a due date, a reminder job was queued.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleToggleTask(task) {
    try {
      const updated = await updateTask(token, task.id, { completed: !task.completed });
      setTasks((current) => current.map((item) => (item.id === task.id ? updated : item)));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Docker • Compose • Kubernetes • Helm</p>
          <h1>TaskFlow</h1>
          <p className="hero-copy">
            A small multi-service app for learning container workflows with a real API, queue, and
            background worker.
          </p>
        </div>
        <div className="status-card">
          <span className="status-label">Stack</span>
          <strong>FastAPI + React + Postgres + Redis</strong>
          <span className="status-label">Session</span>
          <strong>{token ? userEmail : "Signed out"}</strong>
        </div>
      </header>

      {(error || message) && (
        <div className={`banner ${error ? "banner-error" : "banner-success"}`}>
          {error || message}
        </div>
      )}

      <main className="layout">
        <section className="panel">
          <div className="panel-heading">
            <h2>{token ? "Account" : mode === "login" ? "Sign in" : "Create account"}</h2>
            {!token && (
              <button
                className="ghost-button"
                type="button"
                onClick={() => {
                  setMode((current) => (current === "login" ? "register" : "login"));
                  setMessage("");
                  setError("");
                }}
              >
                {mode === "login" ? "Need an account?" : "Already registered?"}
              </button>
            )}
          </div>

          {token ? (
            <div className="account-card">
              <p>Signed in as <strong>{userEmail}</strong></p>
              <button className="secondary-button" type="button" onClick={handleLogout}>
                Log out
              </button>
            </div>
          ) : (
            <form className="stack" onSubmit={handleAuthSubmit}>
              <label>
                <span>Email</span>
                <input
                  required
                  type="email"
                  value={authForm.email}
                  onChange={(event) => setAuthForm({ ...authForm, email: event.target.value })}
                />
              </label>
              <label>
                <span>Password</span>
                <input
                  required
                  minLength={8}
                  type="password"
                  value={authForm.password}
                  onChange={(event) => setAuthForm({ ...authForm, password: event.target.value })}
                />
              </label>
              <button className="primary-button" disabled={submitting} type="submit">
                {submitting ? "Working..." : mode === "login" ? "Sign in" : "Register"}
              </button>
            </form>
          )}
        </section>

        <section className="panel">
          <div className="panel-heading">
            <h2>Create task</h2>
            <span className="chip">{token ? "Authenticated" : "Login required"}</span>
          </div>
          <form className="stack" onSubmit={handleTaskSubmit}>
            <label>
              <span>Title</span>
              <input
                required
                disabled={!token}
                value={taskForm.title}
                onChange={(event) => setTaskForm({ ...taskForm, title: event.target.value })}
              />
            </label>
            <label>
              <span>Description</span>
              <textarea
                disabled={!token}
                rows="4"
                value={taskForm.description}
                onChange={(event) => setTaskForm({ ...taskForm, description: event.target.value })}
              />
            </label>
            <label>
              <span>Reminder due date</span>
              <input
                disabled={!token}
                type="datetime-local"
                value={taskForm.dueAt}
                onChange={(event) => setTaskForm({ ...taskForm, dueAt: event.target.value })}
              />
            </label>
            <button className="primary-button" disabled={!token || submitting} type="submit">
              {submitting ? "Saving..." : "Create task"}
            </button>
          </form>
        </section>
      </main>

      <section className="panel task-panel">
        <div className="panel-heading">
          <h2>Your tasks</h2>
          <span className="chip">{loadingTasks ? "Refreshing" : `${tasks.length} loaded`}</span>
        </div>
        {!token ? (
          <p className="empty-state">Sign in to load tasks from the API.</p>
        ) : loadingTasks ? (
          <p className="empty-state">Loading tasks...</p>
        ) : tasks.length === 0 ? (
          <p className="empty-state">No tasks yet. Create one to test the backend and queue.</p>
        ) : (
          <div className="task-grid">
            {tasks.map((task) => (
              <article className={`task-card ${task.completed ? "task-complete" : ""}`} key={task.id}>
                <div className="task-card-top">
                  <div>
                    <h3>{task.title}</h3>
                    <p>{task.description || "No description provided."}</p>
                  </div>
                  <button className="ghost-button" type="button" onClick={() => handleToggleTask(task)}>
                    {task.completed ? "Mark active" : "Mark done"}
                  </button>
                </div>
                <dl>
                  <div>
                    <dt>Due</dt>
                    <dd>{task.due_at ? new Date(task.due_at).toLocaleString() : "No reminder set"}</dd>
                  </div>
                  <div>
                    <dt>Reminder</dt>
                    <dd>
                      {task.reminder_sent_at
                        ? `Processed ${new Date(task.reminder_sent_at).toLocaleString()}`
                        : "Pending / not sent"}
                    </dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
