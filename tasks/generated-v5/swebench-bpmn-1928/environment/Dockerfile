FROM swebench/sweb.eval.x86_64.bpmn-io_1776_bpmn-js-1928@sha256:b75c9ea8b10388807e0f02841c5671ee76aa1afad4579751c484a674c5ae3f1b
USER root
RUN mkdir -p /workspace && git -C /testbed archive 948c0d73bd9187b6d24ba01f930bd8334898fdb1 | tar -x -C /workspace
RUN rm -rf /testbed/.git && ln -s /testbed/node_modules /workspace/node_modules && mkdir -p /svh-base && cp -R /workspace/lib /svh-base/lib
WORKDIR /workspace
