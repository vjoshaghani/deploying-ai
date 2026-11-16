# Ottawa Day Trip Planner

A conversational assistant for adult visitors exploring Ottawa and nearby Gatineau. It recommends attractions, retrieves weather forecasts, and estimates whether a proposed day fits a group’s time and budget.

## Services

1. **Attraction search:** Semantic search over 18 real attractions using persistent Chroma. Optional metadata filters restrict results to indoor, outdoor, or mixed settings.
2. **Weather:** Open-Meteo forecasts for Ottawa, from today through six days ahead. The assistant explains the results in natural language.
3. **Plan calculator:** A function-calling tool calculates admission, meals, transport, total duration, and remaining budget and time.

## Running the application

Use the existing course Python environment.

From the repository root:

```bash
cd 05_src
python -m assignment_chat.app
```

Open the local address printed in the terminal. Docker is not required.

The application needs internet access and the course’s valid `API_GATEWAY_KEY`, supplied through environment variables or the existing `05_src/.env` or `05_src/.secrets` configuration.

`MODEL` optionally selects the chat model; the default is `gpt-4o-mini`. No credentials are included in the submission.

## Project structure

- `app.py`: Gradio interface and session conversation state.
- `main.py`: LangGraph model/tool workflow.
- `prompts.py`: Assistant role and instructions.
- `agent_tools.py`: Model-callable tool definitions.
- `tools_attractions.py`: Attraction retrieval.
- `tools_weather.py`: Weather API integration.
- `tools_budget.py`: Cost and duration calculations.
- `guardrails.py`: Input checks and restricted-topic output checks.
- `db.py`: Persistent Chroma connection and embedding configuration.
- `data/attractions.csv`: Attraction descriptions and numerical planning data.
- `chroma_db/`: Prepared collection and embeddings.
- `project.ipynb`: Dataset preparation and component tests.

## Data and embeddings

The dataset contains real attractions with source links. Prices are fixed demonstration amounts in CAD, treated as including admission taxes and fees. Visit durations are planning estimates. They are not current ticket quotations.

Each attraction becomes one document combining its name, description, and interests. Its stable ID connects retrieval results to the CSV. Metadata includes its name, setting, neighbourhood, and source URL.

Documents were embedded using `text-embedding-3-small` through the course gateway. The saved Chroma collection uses cosine distance.

The prepared database is included. Assessors do not need to generate attraction embeddings or run the notebook before launching the application. Search questions are embedded at runtime.

Gateway credentials are used at runtime but excluded from the embedding function’s saved header configuration.

## Conversation memory and guardrails

Gradio session state retains the full message sequence, including tool calls and results. Clearing the chat clears this state. Conversations are not saved as long-term memory.

System instructions and application checks restrict the required topics and common attempts to reveal or override instructions. Pattern-based checks have limitations, including indirect wording and possible false positives; they are not a guarantee against every bypass.

## Scope and limitations

The planner supports adult groups. It does not book tickets, optimize routes, or verify live opening hours and admission prices.

Meals, transport, travel time, and buffer time are agreed planning allowances. A plan fitting its time budget does not establish ticket availability.

Long conversations are not automatically summarized or truncated.

Weather data is provided by [Open-Meteo](https://open-meteo.com/). Attraction references are included in the CSV and recommendations.