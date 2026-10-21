# Export ordinary verified runs

[CODE] The exporter now accepts `--task-manifest` to package an ordinary run
without loading the frozen benchmark corpus, row or gold test patch. It checks
the run's exact manifest identity, requires the same actual generated fail/pass
and native evidence as other exports, reads the source license inside Docker,
and exports the model's retained source/check bytes. Real Harbor integrity remains
a separate mandatory command; packaging is not a passed trial.

[CODE] `--only` selects public cases so a repeated experiment on the same claim
need not create duplicate training tasks. Empty/unverified selections fail
explicitly, and a missing Harbor bundle points the user to complete export first.
The guide gives exact artifact/review locations plus ordinary export/replay steps.
Existing frozen task bundles were not edited.

[RUN] `.venv/bin/python -I -m pytest tests/test_harbor_export.py -q`: **2 passed**.
The route test uses a controlled normal manifest and fails immediately if
benchmark loading is attempted; it verifies no native gold patch is passed and
that failed repairs cannot be reported as exported. The existing packaging
integrity test continues to reject changed model source bytes and absent native
verification. This is route/unit coverage, not a new ordinary model-quality score.

[RUN] Actual public export with `--only swebench-bpmn-1638` completed from the
new v2 model-generated repair. Its Harbor trials are tracked separately. The
canonical earlier1679 task stays frozen rather than duplicating that same claim
for the v2 repeat.
