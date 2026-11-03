# Keera Agents

**Keera Agents** runs AI agents for your organisation. An agent is an
assistant with its own machine, files and memory. People give it work in a
chat, on a board or on a schedule, and it answers where the work came from.

Every model call an agent makes goes through Keera Gateway, with a key in its
owner's name. So the owner's guardrails, budgets, filters and audit log apply.

Open it with **Keera Agents** in the panel's
[account menu](sign-in.md#in-the-browser), and sign in as you do in the panel.

## Create an agent

Open **Agents** and click **New agent**:

| Field                     | What it means                                                                                                                   |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Name**                  | Unique in the organisation. People use it to address the agent in a shared chat.                                                |
| **Instructions**          | What the agent does and how. It reads them before every task.                                                                   |
| **Model**                 | The model or [router](../manage/routers.md) it thinks with.                                                                     |
| **Project**               | The gateway project whose guardrails and budget it uses. Only administrators choose it; otherwise it is the first project.      |
| **Tools**                 | **Memory**, **Files**, **Shell** and **Web**. The [MCP servers](../manage/mcp.md) its key may call come on top.                 |
| **Who may give it work**  | **Only its owner** (the default), **Everyone in the organisation**, or **Only the people listed**.                              |
| **Monthly budget in CHF** | The most its model calls may cost per month. Once spent, the gateway refuses its calls, so its tasks fail until the next month. |

**Machine** sets how isolated it runs (**Standard**, **Isolated** or **VM**),
and its CPU, memory and disk.

You are its owner. What it spends counts as yours. Everyone in the
organisation sees every agent, but only its owner or an administrator can
change, stop or delete it.

## Give it work

| Where          | How                                                                                                                                                               |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A chat**     | Write to it in Microsoft Teams, Google Chat or Slack. In a channel, mention the bot. It answers in the thread.                                                    |
| **Keera Chat** | Pick the agent in the model menu of a new chat, or click **Chat** on the agent's page. See [Keera Chat](chat.md).                                                 |
| **The panel**  | Click **Give a task** on the agent's page.                                                                                                                        |
| **The board**  | Assign a card to it in **To do**. It moves the card to **In progress**, then comments with the result and moves it to **Review**, or to **Backlog** if it failed. |
| **A schedule** | Under **Schedules**, give it the same task at set times, such as every weekday at 08:00, or by a cron expression. The result can go to a chat.                    |
| **A folder**   | A new or changed file in a watched Google Drive or OneDrive folder starts a task.                                                                                 |

When several agents share one bot, start the message with the agent's name,
such as `Scout: …` or `@Scout`.

An agent connected to a GitHub or GitLab repository can code in it. It pushes
branches that start with `keera/` and opens a pull or merge request for a
person to review. It cannot push to any other branch.

Besides its tools, an agent can post updates to its chats, create and move
cards on the board, and comment on issues and pull or merge requests.

An agent does one task at a time. Others wait in line. A task stops after 30
minutes. After 15 minutes without work, the agent sleeps, so the next task
takes a little longer to start.

The **Tasks** tab shows what it did for each task: its messages, the tools it
used and their results. You see the tasks you asked for and the tasks of your
own agents. Administrators see all. Tasks are deleted after 90 days.

## Connect it to a service

An administrator adds a **connector** for each service, under **Connectors**,
such as the organisation's Slack app or GitHub token. Then, on an agent's
**Channels** tab, its owner or an administrator clicks **Add channel**, picks
the connector and a mode:

- **Chat**: it takes messages in a chat.
- **Watch**: each new or changed file in a folder is a task.
- **Files**: it may read and write files in a folder.
- **Repository**: it may code in a repository.

The service's credentials stay in Keera Agents. They never reach the agent's
machine.

## Stop an agent

- **Stop** on the agent's page stops its machine and cancels its tasks. Its
  files and memory are kept. **Start** runs it again.
- **Delete agent**, at the bottom of **Settings**, removes its machine, files,
  memory, channels and schedules, and revokes its key. Its tasks stay.

Its key shows as **Agent <name>**, marked **Keera Agent**, on the gateway's
**API keys** screen. It cannot be rotated. Revoking it makes the agent's model
calls fail, but the agent still takes tasks, so use **Stop** instead.

When its owner is [disabled](../manage/users.md#when-someone-leaves), the
agent's key is revoked at once, and the agent stops within ten minutes. An
administrator can click **Take over** in its **Settings** tab, then **Start**.
It then runs with a key in their name.
