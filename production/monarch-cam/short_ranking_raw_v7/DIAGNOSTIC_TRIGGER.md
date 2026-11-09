# Temporary V7 audio-window diagnostic trigger

This file only triggers the short-lived `V7 audio-window diagnostic` workflow. It collects the runner's candidate audio/motion measurements and selected-window native audio audit as a GitHub artifact so the V7 render can be debugged without repeating the full 1800-frame render. It is not a deliverable, an acceptance claim, or a change to the V7 short.

Second diagnostic pass prints compact per-window audio measurements into the job log.
