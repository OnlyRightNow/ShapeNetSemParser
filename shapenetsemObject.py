
class ShapeNetSemObject:
    def __init__(self, full_id, category, wnsynset, wnlemmas, up, front, unit, aligned_dims, name, tags):
        self.tags = tags
        self.name = name
        self.aligned_dims = aligned_dims
        self.unit = unit
        self.front = front
        self.up = up
        self.wnlemmas = wnlemmas
        self.wnsynset = wnsynset
        self.category = category
        self.full_id = full_id
