from dataclasses import dataclass


@dataclass
class Cursor:
    clip: str
    frame: int = 0
    age: int = 0

    def enter(self, target):
        self.clip, self.frame, self.age = target, 0, 0

    def advance(self, clip, speed):
        """返回本拍实际穿越帧和展示帧。尾停留时不重复发出根位移和事件。"""
        self.age += 1
        passed = []
        for _ in range(speed):
            if self.frame == clip['frames']:
                break
            passed.append(self.frame)
            self.frame += 1
            if clip['loop'] and self.frame == clip['frames']:
                self.frame = 0
        return passed, passed[-1] if passed else clip['frames'] - 1
