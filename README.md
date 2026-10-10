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
