import math


def sample(clip, frame):
    left = clip['keys'][0]
    for right in clip['keys'][1:]:
        if frame < right['at']:
            fraction = (frame - left['at']) / (right['at'] - left['at'])
            return [a + (b - a) * fraction for a, b in zip(left['angles'], right['angles'])]
        left = right
    return left['angles']


def project(rig, angles, mirror):
    transforms, points = {}, []
    for joint, local in zip(rig, angles):
        parent_x, parent_y, parent_angle = transforms.get(joint['parent'], (0, 0, 0))
        radians = math.radians(parent_angle)
        dx, dy = joint['dx'], joint['dy']
        x = parent_x + dx * math.cos(radians) - dy * math.sin(radians)
        y = parent_y + dx * math.sin(radians) + dy * math.cos(radians)
        angle = parent_angle + local
        transforms[joint['id']] = x, y, angle
        points.append(dict(id=joint['id'], parent=joint['parent'],
                           x=round((-x if mirror else x) * 1000), y=round(y * 1000)))
    return points
