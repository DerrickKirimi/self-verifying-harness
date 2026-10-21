import {
  bootstrapModeler,
  getBpmnJS,
  inject
} from 'test/TestHelper';

import {
  createEvent as globalEvent
} from 'test/util/MockEvents';

import coreModule from 'lib/core';
import modelingModule from 'lib/features/modeling';
import replaceMenuProviderModule from 'lib/features/popup-menu';

import {
  query as domQuery,
  classes as domClasses
} from 'min-dom';

describe('features/popup-menu - ReplaceMenuProvider multi-instance', function() {

  var diagramXML =
    '<?xml version="1.0" encoding="UTF-8"?>' +
    '<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" ' +
    '                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" ' +
    '                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" ' +
    '                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' +
    '                  id="Definitions_1" ' +
    '                  targetNamespace="http://bpmn.io/schema/bpmn">' +
    '  <bpmn:process id="Process_1" isExecutable="false">' +
    '    <bpmn:subProcess id="SubProcess_1">' +
    '      <bpmn:multiInstanceLoopCharacteristics>' +
    '        <bpmn:loopCardinality xsi:type="bpmn:tFormalExpression">1</bpmn:loopCardinality>' +
    '        <bpmn:completionCondition xsi:type="bpmn:tFormalExpression">${foo}</bpmn:completionCondition>' +
    '      </bpmn:multiInstanceLoopCharacteristics>' +
    '    </bpmn:subProcess>' +
    '  </bpmn:process>' +
    '  <bpmndi:BPMNDiagram id="BPMNDiagram_1">' +
    '    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">' +
    '      <bpmndi:BPMNShape id="SubProcess_1_di" bpmnElement="SubProcess_1" isExpanded="true">' +
    '        <dc:Bounds x="150" y="100" width="350" height="200" />' +
    '      </bpmndi:BPMNShape>' +
    '    </bpmndi:BPMNPlane>' +
    '  </bpmndi:BPMNDiagram>' +
    '</bpmn:definitions>';

  var testModules = [
    coreModule,
    modelingModule,
    replaceMenuProviderModule
  ];

  beforeEach(bootstrapModeler(diagramXML, { modules: testModules }));

  function openPopup(element) {
    getBpmnJS().invoke(function(popupMenu) {
      popupMenu.open(element, 'bpmn-replace', {
        x: element.x + 100,
        y: element.y + 100
      });
    });
  }

  function queryEntry(id) {
    var container = getBpmnJS().get('canvas').getContainer();
    return domQuery('.djs-popup [data-id="' + id + '"]', container);
  }

  function triggerAction(id) {
    var entry = queryEntry(id);
    if (!entry) {
      throw new Error('entry "' + id + '" not found in replace menu');
    }
    var popupMenu = getBpmnJS().get('popupMenu');
    return popupMenu.trigger(globalEvent(entry, { x: 0, y: 0 }));
  }

  it('should retain multi-instance properties when changing between parallel and sequential', inject(
    function(elementRegistry) {

      // given
      var subProcess = elementRegistry.get('SubProcess_1');
      var subProcessGfx = elementRegistry.getGraphics(subProcess);

      // verify initial state: parallel multi-instance with loopCardinality and completionCondition
      expect(domQuery('[data-marker="parallel"]', subProcessGfx)).to.exist;
      expect(domQuery('[data-marker="sequential"]', subProcessGfx)).not.to.exist;

      var initialLoopCharacteristics = subProcess.businessObject.loopCharacteristics;
      expect(initialLoopCharacteristics).to.exist;
      expect(initialLoopCharacteristics.isSequential).to.be.false;
      expect(initialLoopCharacteristics.loopCardinality).to.exist;
      expect(initialLoopCharacteristics.loopCardinality.body).to.equal('1');
      expect(initialLoopCharacteristics.completionCondition).to.exist;
      expect(initialLoopCharacteristics.completionCondition.body).to.equal('${foo}');

      // when: switch from parallel to sequential multi-instance
      openPopup(subProcess);
      triggerAction('toggle-sequential-mi');

      // then: visual marker updates to sequential
      subProcessGfx = elementRegistry.getGraphics(subProcess);
      expect(domQuery('[data-marker="sequential"]', subProcessGfx)).to.exist;
      expect(domQuery('[data-marker="parallel"]', subProcessGfx)).not.to.exist;

      // then: multi-instance properties must be preserved
      var updatedLoopCharacteristics = subProcess.businessObject.loopCharacteristics;
      expect(updatedLoopCharacteristics).to.exist;
      expect(updatedLoopCharacteristics.isSequential).to.be.true;
      expect(updatedLoopCharacteristics.loopCardinality, 'loopCardinality should be preserved').to.exist;
      expect(updatedLoopCharacteristics.loopCardinality.body).to.equal('1');
      expect(updatedLoopCharacteristics.completionCondition, 'completionCondition should be preserved').to.exist;
      expect(updatedLoopCharacteristics.completionCondition.body).to.equal('${foo}');
    }
  ));

});
