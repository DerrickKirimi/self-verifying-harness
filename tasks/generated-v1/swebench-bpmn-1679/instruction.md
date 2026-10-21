Fix the recorded software requirement in /workspace. Edit lib JavaScript source only; preserve existing behavior.

When toggling from standard loop characteristics to parallel or sequential multi-instance via the replace popup menu, the task's loopCharacteristics businessObject must become an instance of bpmn:MultiInstanceLoopCharacteristics and serialize to <bpmn:multiInstanceLoopCharacteristics /> in the exported XML.

Recording source (reference only): {"sha256": "be1925039dea24dd160978f40e52df53caa2f30eadb4826b74de192d952a4bd3", "source_url": "https://user-images.githubusercontent.com/61787903/172374025-61f23e34-b199-4e67-bddd-ec7a3aafdb92.gif"}
