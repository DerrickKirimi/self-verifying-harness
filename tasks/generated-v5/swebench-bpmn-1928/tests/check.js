import {
  bootstrapModeler,
  inject
} from 'test/TestHelper';

import coreModule from 'lib/core';
import modelingModule from 'lib/features/modeling';
import rulesModule from 'lib/features/rules';
import snappingModule from 'lib/features/snapping';
import spaceToolModule from 'lib/features/space-tool';

import {
  createCanvasEvent as canvasEvent
} from 'test/util/MockEvents';

var testModules = [
  coreModule,
  modelingModule,
  rulesModule,
  snappingModule,
  spaceToolModule
];

var xml = '<?xml version="1.0" encoding="UTF-8"?>' +
  '<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" ' +
  'xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" ' +
  'xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" ' +
  'id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">' +
  '  <bpmn:collaboration id="Collaboration_1">' +
  '    <bpmn:participant id="EmptyPool" name="Empty Pool" />' +
  '  </bpmn:collaboration>' +
  '  <bpmndi:BPMNDiagram id="BPMNDiagram_1">' +
  '    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Collaboration_1">' +
  '      <bpmndi:BPMNShape id="EmptyPool_di" bpmnElement="EmptyPool" isHorizontal="true">' +
  '        <dc:Bounds x="100" y="100" width="400" height="60" />' +
  '      </bpmndi:BPMNShape>' +
  '    </bpmndi:BPMNPlane>' +
  '  </bpmndi:BPMNDiagram>' +
  '</bpmn:definitions>';

describe('space tool - empty pool', function() {

  beforeEach(bootstrapModeler(xml, { modules: testModules }));

  it('should not resize empty pool vertically', inject(
    function(dragging, elementRegistry, spaceTool) {

      // given
      var emptyPool = elementRegistry.get('EmptyPool');
      var initialHeight = emptyPool.height;

      // when - activate space tool inside empty pool (y between 100 and 160) and drag down
      spaceTool.activateMakeSpace(canvasEvent({ x: 0, y: 130 }));

      dragging.move(canvasEvent({ x: 0, y: 230 }));

      dragging.end();

      // then
      var shapeGfx = elementRegistry.getGraphics(emptyPool);
      var outline = shapeGfx.querySelector('rect');

      expect(emptyPool.height).to.equal(initialHeight);
      expect(outline.getAttribute('height')).to.equal(String(initialHeight));
    })
  );

});
