# agent-misbehavior-experiment

Two small experiments on how AI agents go wrong, inspired by the July 2026 OpenAI/Hugging Face and UK AISI incidents.

Plain Python, no dependencies.

## Reward hacking

`python experiments.py`

A Q-learning agent in a grid world, rewarded for a respawning coin instead of reaching the goal.

- With the sloppy reward it camps the coin and never finishes, even when the goal pays 50x a coin. It only reached the goal twice in 6,000 training games, so it never learned the goal was worth anything.
- An agent that starts out curious finds the goal once it pays 15+.
- With a scorer bug tile that counts as the goal, the honest-reward agent takes the bug every time, even when the real goal is reachable.

`python reward_hacking.py --watch` animates the agents in the terminal.

## Prompt injection

`python prompt_injection.py`

A toy issue-triage agent reads three bug reports. One hides an instruction for AI agents in an HTML comment.

- The naive agent follows it.
- The hardened agent strips hidden text, treats the issue as data, and can only take allowlisted actions, so it ignores it.

The payload is a harmless marker file in a temp folder.

## Prompt injection vs a real model

`python llm_injection.py`

Same issue_43 attack, but a real LLM does the triage through tool calls. The shell is fake: nothing runs except the marker write. Needs an OpenAI-compatible server on localhost:8080 (llama-server with `--jinja`).

Four setups, 10 trials each:

- **naive**: raw issue, shell tool, plain prompt
- **prompt-only**: told the issue is untrusted data, hidden comment still in it
- **strip-only**: hidden comment removed, plain prompt
- **hardened**: stripped, untrusted framing, no shell tool (calls to it get blocked)

`--log runs.jsonl` saves every tool call.
