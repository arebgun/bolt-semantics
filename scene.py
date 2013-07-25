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
        
    @staticmethod
    def load_scene(file, normalize=False):
        jtoclass = {
            u'Box': ObjectClass.BOX,
            u'Cylinder': ObjectClass.CYLINDER,
            u'Sphere': ObjectClass.SPHERE,
        }

        jtocolor = {
            u'yellow': Color.YELLOW,
            u'orange': Color.ORANGE,
            u'red': Color.RED,
            u'green': Color.GREEN,
            u'purple': Color.PURPLE,
            u'blue': Color.BLUE,
            u'pink': Color.PINK,
        }

        json_data=open(file)
        data = json.load(json_data)
        json_data.close()

        #pprint(data)

        scene = Scene(3)

        table_spec = data[u'table']
        t_min = Vec2(table_spec[u'aabb'][u'min'][2], table_spec[u'aabb'][u'min'][0])
        t_max = Vec2(table_spec[u'aabb'][u'max'][2], table_spec[u'aabb'][u'max'][0])

        width = t_max.x - t_min.x
        height = t_max.y - t_min.y
        if normalize: norm_factor = width if width >= height else height
        else: norm_factor = 1

        t_min = Vec2(t_min.x / norm_factor, t_min.y / norm_factor)
        t_max = Vec2(t_max.x / norm_factor, t_max.y / norm_factor)

        table = Landmark('table',
                         RectangleRepresentation(rect=BoundingBox([t_min, t_max])),
                         None,
                         ObjectClass.TABLE)

        scene.add_landmark(table)

        object_specs = data[u'objects']
        print 'there are', len(object_specs), 'objects on the table'

        for i,obj_spec in enumerate(object_specs):
            o_min = Vec2(obj_spec[u'aabb'][u'min'][2], obj_spec[u'aabb'][u'min'][0])
            o_max = Vec2(obj_spec[u'aabb'][u'max'][2], obj_spec[u'aabb'][u'max'][0])

            width = o_max.x - o_min.x
            height = o_max.y - o_min.y

            o_min = Vec2(o_min.x / norm_factor, o_min.y / norm_factor)
            o_max = Vec2(o_max.x / norm_factor, o_max.y / norm_factor)

            obj = Landmark('object_%s' % obj_spec[u'name'],
                            RectangleRepresentation(rect=BoundingBox([o_min, o_max]), landmarks_to_get=[]),
                            None,
                            jtoclass[obj_spec[u'type']],
                            jtocolor[obj_spec[u'color-name']])

            obj.representation.alt_representations = []
            scene.add_landmark(obj)

        camera_spec = data[u'cam']
        speaker = Speaker(Vec2(camera_spec[u'loc'][2] / norm_factor, camera_spec[u'loc'][0] / norm_factor))

        # speaker.visualize(scene, obj, Vec2(0,0), None, None, '')
        return scene, speaker
