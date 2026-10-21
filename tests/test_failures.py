import json
from svh.failures import exception_evidence


def test_nested_provider_status_survives_without_sensitive_error_details():
    class ProviderError(Exception):
        code=503
        response={'headers':{'Authorization':'private-key'}}
        details='private-prompt'
    cause=ProviderError('private-key and private-prompt')
    wrapper=RuntimeError('private request body')
    wrapper.__cause__=cause
    error=ExceptionGroup('private group description',[wrapper,cause])
    result=exception_evidence(error)
    assert result==[{'type':'ExceptionGroup'},{'type':'ProviderError','http_status':503},{'type':'RuntimeError'}]
    assert 'private' not in json.dumps(result)
    cause.__cause__=wrapper
    assert exception_evidence(error)==result


def test_arbitrary_error_codes_are_not_serialized_as_http_evidence():
    for code in ['private-key',True,99,600,None]:
        error=ValueError('private request')
        error.code=code
        assert exception_evidence(error)==[{'type':'ValueError'}]
