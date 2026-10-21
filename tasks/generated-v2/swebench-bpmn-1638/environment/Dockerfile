FROM swebench/sweb.eval.x86_64.bpmn-io_1776_bpmn-js-1638@sha256:d548fd8261111fdb43dc1204e0535708f1c234197be628e6a98df49e1c8eb25c
USER root
RUN mkdir -p /workspace && git -C /testbed archive 574a674381d6449b509396b6d17c4ca94674ea1c | tar -x -C /workspace
RUN rm -rf /testbed/.git && ln -s /testbed/node_modules /workspace/node_modules && mkdir -p /svh-base && cp -R /workspace/lib /svh-base/lib
WORKDIR /workspace
