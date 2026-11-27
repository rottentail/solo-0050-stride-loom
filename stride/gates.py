"""解释每条候选边，以及唯一胜者消费的输入。"""


def choose(edges, age, events, buffer):
    labels = {event['tag'] for event in events}
    winner, consumed = None, None
    assessed = []
    for edge in edges:
        press = buffer.find(edge['command'])
        missing = []
        if press is None:
            missing.append('command')
        if age < edge['age']:
            missing.append('age')
        if edge['mark'] is not None and edge['mark'] not in labels:
            missing.append('mark')
        if missing:
            verdict = 'blocked'
        elif winner is not None:
            verdict = 'deferred'
        else:
            winner, consumed, verdict = edge, press, 'chosen'
        assessed.append(dict(id=edge['id'], verdict=verdict, missing=missing,
                             press=press.id if press is not None else None))
    if consumed is not None:
        buffer.consume(consumed)
    return winner, assessed, consumed.id if consumed is not None else None
