FROM swebench/sweb.eval.x86_64.bpmn-io_1776_bpmn-js-1679@sha256:b9e7aeef61162391296294a52b21d21643b1c1b919184bb50002d77cca56e28c
USER root
RUN mkdir -p /workspace && git -C /testbed archive 6eb9aceb843a43ff6ae6d6d640d22ae84c508315 | tar -x -C /workspace
RUN rm -rf /testbed/.git && ln -s /testbed/node_modules /workspace/node_modules && mkdir -p /svh-base && cp -R /workspace/lib /svh-base/lib
WORKDIR /workspace
