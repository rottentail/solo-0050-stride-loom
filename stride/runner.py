from .clock import Cursor
from .compile import compile_graph
from .gates import choose
from .inputs import Buffer, schedule
from .motion import traverse
from .pose import project, sample


def run(doc, scene):
    graph = compile_graph(doc)
    cursor = Cursor(graph.start)
    commands = Buffer(graph.ttl)
    arrivals = schedule(scene)
    world = 0
    rows = []
    for tick in range(scene['ticks']):
        expired = commands.begin(tick, arrivals[tick])
        clip = graph.clips[cursor.clip]
        passed, frame = cursor.advance(clip, scene['speed'])
        delta, events = traverse(graph, clip, passed, scene['mirror'])
        world += delta
        winner, probes, consumed = choose(graph.edges.get(cursor.clip, ()), cursor.age,
                                          events, commands)
        rows.append(dict(tick=tick, clip=cursor.clip, age=cursor.age, frame=frame, crossed=passed,
                         delta=delta, world=world, events=events, gates=probes, expired=expired,
                         arrived=[press.id for press in arrivals[tick]], pending=commands.snapshot(),
                         consumed=consumed, edge=winner['id'] if winner else None,
                         target=winner['target'] if winner else None,
                         pose=project(graph.rig, sample(clip, frame), scene['mirror'])))
        if winner:
            cursor.enter(winner['target'])
    return dict(scene=scene['id'], rows=rows, end=dict(clip=cursor.clip, world=world,
                                                      pending=commands.snapshot()))
