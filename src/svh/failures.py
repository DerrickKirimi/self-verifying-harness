"""Minimal private failure evidence without provider request/error payloads."""


def exception_evidence(error):
    pending=[error];seen=set();evidence=[]
    while pending:
        item=pending.pop()
        if id(item) in seen:continue
        seen.add(id(item))
        entry={'type':type(item).__name__}
        code=getattr(item,'code',None)
        if type(code) is int and 100 <= code <= 599:
            entry['http_status']=code
        reply=getattr(item,'ai_message',None)
        if reply is not None:entry['model_reply']=reply.model_dump()
        evidence.append(entry)
        pending.extend(getattr(item,'exceptions',[]))
        if item.__cause__ is not None:pending.append(item.__cause__)
    return evidence
