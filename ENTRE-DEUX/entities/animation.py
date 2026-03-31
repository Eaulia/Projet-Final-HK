# ─────────────────────────────────────────
#  ENTRE-DEUX — Système d'animation
# ─────────────────────────────────────────

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def stop (self, img_index=0):
        self.frame = img_index * self.img_duration
        self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]
