# Raw Full-Screen V4 render trigger

Normal pushes to this V4 workflow, spec, manifest, scripts or this trigger file start the V4 render workflow. Explicit `workflow_dispatch` is also available.

The V3 render workflow and V3 source-reconstruction workflow listen to separate paths; V4 work does not overwrite or re-trigger them.
