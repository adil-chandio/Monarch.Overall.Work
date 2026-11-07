# Raw Full-Screen V4 render trigger

Normal pushes to this V4 workflow, spec, manifest, scripts or this trigger file start the V4 render workflow. Explicit `workflow_dispatch` is also available.

The final audio builder measures the delivered AAC stream and applies bounded level/peak corrections until the unchanged web gates pass. The replacement-source probe workflow is separate. The final V4 manifest uses the verified CC0 originals, with one Wikimedia transcode for the large dove source; no candidate probe assets are used as separate audio layers.

The V3 render workflow and V3 source-reconstruction workflow listen to separate paths; V4 work does not overwrite or re-trigger them.
