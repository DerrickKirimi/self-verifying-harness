FROM swebench/sweb.eval.x86_64.bpmn-io_1776_bpmn-js-1640@sha256:310ae5ed5cc26302e732efbf7669327410489cca6072a3faf37b38af6e5e0b21
USER root
RUN mkdir -p /workspace && git -C /testbed archive b708a4d7afa57c5944bda777c15c5b7971c3f4c9 | tar -x -C /workspace
RUN rm -rf /testbed/.git && ln -s /testbed/node_modules /workspace/node_modules && mkdir -p /svh-base && cp -R /workspace/lib /svh-base/lib
WORKDIR /workspace
