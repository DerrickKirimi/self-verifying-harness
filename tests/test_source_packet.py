from svh.source_packet import root_spec_references


def test_base_spec_imports_are_relocated_without_changing_assertions_or_source():
    content="import { inject } from '../../../../TestHelper';\nimport core from '../../../../../lib/core';\nvar xml = require('./planes.bpmn');\nexpect(actual).to.equal(expected);"
    original={'path':'/workspace/test/spec/features/modeling/behavior/PlanesSpec.js','first_line':1,'content':content,'truncated':False}
    packet=[original,{'path':'/workspace/lib/handler.js','content':"import foo from './foo';"}]
    result=root_spec_references(packet)
    assert "from 'test/TestHelper'" in result[0]['content']
    assert "from 'lib/core'" in result[0]['content']
    assert "require('test/spec/features/modeling/behavior/planes.bpmn')" in result[0]['content']
    assert result[0]['content'].endswith('expect(actual).to.equal(expected);')
    assert original['content']==content and result[1]==packet[1]
    assert len(result[0]['original_excerpt_sha256'])==64
    assert result[0]['import_mapping']['./planes.bpmn'].endswith('/planes.bpmn')


def test_reference_mapping_does_not_relocate_external_or_escaping_imports():
    content="import ext from 'min-dom';\nrequire('../../../../../../../../outside');\nrequire('test/fixture.bpmn');"
    result=root_spec_references([{'path':'/workspace/test/spec/features/TestSpec.js','content':content}])
    assert result[0]['content']==content and 'import_mapping' not in result[0]
