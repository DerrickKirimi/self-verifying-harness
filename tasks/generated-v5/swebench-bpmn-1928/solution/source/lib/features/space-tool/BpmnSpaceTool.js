import inherits from 'inherits-browser';

import SpaceTool from 'diagram-js/lib/features/space-tool/SpaceTool';

import { is } from '../../util/ModelUtil';
import { isExpanded } from '../../util/DiUtil';

/**
 * @typedef {import('didi').Injector} Injector
 *
 * @typedef {import('../../model/Types').Shape} Shape
 *
 * @typedef {import('diagram-js/lib/util/Types').Axis} Axis
 * @typedef {import('diagram-js/lib/util/Types').Point} Point
 */

/**
 * @param {Injector} injector
 */
export default function BpmnSpaceTool(injector) {
  injector.invoke(SpaceTool, this);
}

BpmnSpaceTool.$inject = [
  'injector'
];

inherits(BpmnSpaceTool, SpaceTool);

/**
 * @param {Shape[]} elements
 * @param {Axis} axis
 * @param {Point} delta
 * @param {number} start
 *
 * @return {Object}
 */
BpmnSpaceTool.prototype.calculateAdjustments = function(elements, axis, delta, start) {
  var adjustments = SpaceTool.prototype.calculateAdjustments.call(this, elements, axis, delta, start);

  // do not resize text annotations or empty pools vertically
  adjustments.resizingShapes = adjustments.resizingShapes.filter(function(shape) {
    if (is(shape, 'bpmn:TextAnnotation')) {
      return false;
    }

    if (axis === 'y' && is(shape, 'bpmn:Participant') && !isExpanded(shape)) {
      return false;
    }

    return true;
  });

  return adjustments;
};