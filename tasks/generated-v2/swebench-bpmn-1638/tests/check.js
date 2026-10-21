import {
  bootstrapModeler,
  inject
} from 'test/TestHelper';

import modelingModule from 'lib/features/modeling';
import coreModule from 'lib/core';

describe('SvhGeneratedSpec', function() {
  var diagramXML = require('./spec/features/modeling/UpdateLabel.bpmn');

  beforeEach(bootstrapModeler(diagramXML, {
    modules: [
      coreModule,
      modelingModule
    ]
  }));

  it('should remove label property from di when label is cleared', inject(
    function(modeling, elementRegistry) {
      var task_2 = elementRegistry.get('Task_2');
      expect(task_2.di.label).to.exist;

      modeling.updateLabel(task_2, '');

      expect(task_2.di).not.to.have.property('label');
    }
  ));
});
