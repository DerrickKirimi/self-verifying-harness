Fix the recorded software requirement in /workspace. Edit lib JavaScript source only; preserve existing behavior.

Clearing a task's label via updateLabel should completely remove or unset the `label` property from its DI object (`di.label`), rather than leaving `di.label = null`.

Recording source (reference only): {"sha256": "220daa4e7faf2e8fa18aab3c10ada0642487ab7a9d7d9965bd06e8e036c61758", "source_url": "https://user-images.githubusercontent.com/21984219/164674929-c8e344a5-71d1-4cab-8611-b4cd5ef87a02.gif"}
