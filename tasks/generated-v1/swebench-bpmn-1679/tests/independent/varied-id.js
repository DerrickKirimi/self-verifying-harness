import {
  bootstrapModeler,
  getBpmnJS,
  inject
} from 'test/TestHelper';

import {
  createEvent as globalEvent
} from 'test/util/MockEvents';

import { is } from 'lib/util/ModelUtil';

describe('features/popup-menu - toggle loop characteristics', function() {

  var diagramXML =
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"\n' +
    '                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"\n' +
    '                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"\n' +
    '                  id="Definitions_1"\n' +
    '                  targetNamespace="http://bpmn.io/schema/bpmn">\n' +
    '  <bpmn:process id="Process_1" isExecutable="false">\n' +
    '    <bpmn:task id="Task_outside_recording" name="Task 1" />\n' +
    '  </bpmn:process>\n' +
    '  <bpmndi:BPMNDiagram id="BPMNDiagram_1">\n' +
    '    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">\n' +
    '      <bpmndi:BPMNShape id="Task_outside_recording_di" bpmnElement="Task_outside_recording">\n' +
    '        <dc:Bounds x="150" y="100" width="100" height="80" />\n' +
    '      </bpmndi:BPMNShape>\n' +
    '    </bpmndi:BPMNPlane>\n' +
    '  </bpmndi:BPMNDiagram>\n' +
    '</bpmn:definitions>';

  beforeEach(bootstrapModeler(diagramXML));

  function openPopup(element, offset) {
    offset = offset || 100;

    getBpmnJS().invoke(function(popupMenu) {
      popupMenu.open(element, 'bpmn-replace', {
        x: element.x + offset,
        y: element.y + offset
      });
    });
  }

  function queryEntry(id) {
    var container = getBpmnJS().get('canvas').getContainer();

    return container.querySelector('.djs-popup [data-id="' + id + '"]');
  }

  function triggerAction(id) {
    var entry = queryEntry(id);

    if (!entry) {
      throw new Error('entry "' + id + '" not found in replace menu');
    }

    var popupMenu = getBpmnJS().get('popupMenu');

    return popupMenu.trigger(globalEvent(entry, { x: 0, y: 0 }));
  }

  it('should update loop characteristics to parallel multi-instance after toggling loop', inject(function(elementRegistry, canvas) {

    // given
    var bpmnJS = getBpmnJS();
    var task = elementRegistry.get('Task_outside_recording');

    openPopup(task);
    triggerAction('toggle-loop');

    expect(is(task.businessObject.loopCharacteristics, 'bpmn:StandardLoopCharacteristics')).to.be.true;

    // when
    openPopup(task);
    var parallelEntry = queryEntry('toggle-parallel-mi');
    expect(parallelEntry).to.exist;

    triggerAction('toggle-parallel-mi');

    // then
    var taskGfx = canvas.getGraphics(task);
    expect(taskGfx).to.exist;
    expect(taskGfx.querySelector('[data-marker="parallel"]')).to.exist;

    return bpmnJS.saveXML({ format: true }).then(function(result) {
      expect(result.xml).to.include('<bpmn:multiInstanceLoopCharacteristics');
      expect(result.xml).not.to.include('<bpmn:standardLoopCharacteristics');
      expect(is(task.businessObject.loopCharacteristics, 'bpmn:MultiInstanceLoopCharacteristics')).to.be.true;
      expect(task.businessObject.loopCharacteristics.isSequential).to.be.false;
    });
  }));

  it('should update loop characteristics to sequential multi-instance after toggling loop', inject(function(elementRegistry, canvas) {

    // given
    var bpmnJS = getBpmnJS();
    var task = elementRegistry.get('Task_outside_recording');

    openPopup(task);
    triggerAction('toggle-loop');

    expect(is(task.businessObject.loopCharacteristics, 'bpmn:StandardLoopCharacteristics')).to.be.true;

    // when
    openPopup(task);
    var sequentialEntry = queryEntry('toggle-sequential-mi');
    expect(sequentialEntry).to.exist;

    triggerAction('toggle-sequential-mi');

    // then
    var taskGfx = canvas.getGraphics(task);
    expect(taskGfx).to.exist;
    expect(taskGfx.querySelector('[data-marker="sequential"]')).to.exist;

    return bpmnJS.saveXML({ format: true }).then(function(result) {
      expect(result.xml).to.include('<bpmn:multiInstanceLoopCharacteristics isSequential="true"');
      expect(result.xml).not.to.include('<bpmn:standardLoopCharacteristics');
      expect(is(task.businessObject.loopCharacteristics, 'bpmn:MultiInstanceLoopCharacteristics')).to.be.true;
      expect(task.businessObject.loopCharacteristics.isSequential).to.be.true;
    });
  }));

});
