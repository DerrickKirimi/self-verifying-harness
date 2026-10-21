# Bind ordinary task identity before extraction

[CODE] An ordinary run could previously save extraction/checkpoint output and
crash before writing report.json. Reusing that run name with another manifest
would then load the old checkpoint because only report.json bound the inputs.
`bind_task_run` now writes an exclusive input-identity file before model setup or
any paid stage, checks it on resume, and rejects existing unbound artifacts.
The frozen public evaluation path is unchanged.

[RUN] The regression test simulates that exact interrupted-checkpoint state,
permits identical input resumption, rejects a different manifest and rejects a
legacy unbound directory. Full suite: **100 passed**, command
`.venv/bin/python -I -m pytest -q`. The ordinary-run commands now explicitly select
the lighter reviewed model and document resume behavior.
