from planar import BoundingBox


class Scene(object):
    def __init__(self, num_dim):
        self.num_dim = num_dim
        self.landmarks = {}

    def __repr__(self):
        return 'Scene(' + str(self.num_dim) + ', ' + str(self.landmarks) + ')'

    def add_landmark(self, lmk):
        self.landmarks[lmk.name] = lmk

    def get_child_scenes(self, trajector):
        scenes = []

        for lmk1 in self.landmarks.values():
            if lmk1.representation.contains(trajector.representation):
                sc = Scene(lmk1.representation.num_dim)

                for lmk2 in self.landmarks.values():
                    if lmk1.representation.contains(lmk2.representation): sc.add_landmark(lmk2)

                scenes.append(sc)
        return scenes

    def get_bounding_box(self):
        return BoundingBox.from_shapes([lmk.representation.get_geometry() for lmk in self.landmarks.values()])

    def fetch_landmark(self, uuid):
        result = None
        for landmark in self.landmarks.values():
            result = landmark.fetch_landmark(uuid)
            if result:
                break
        return result
