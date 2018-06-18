from pyglet.gl import *
import time


o_x = .0
o_y = .0
z = .0
offset = .15
offset_thick = .05  


arrow_sx = [o_x-.2,     o_y,         z, 
            o_x+.0,     o_y+.5,     .0,
            o_x+.1,     o_y+.5,     .0,
            o_x-.1,     o_y,        .0,
            o_x+.1,     o_y-.5,     .0,
            o_x,        o_y-.5,     .0]

arrow_dx = [(o_x+.2),                   -(o_y),                 z,
            (o_x+.0),                   -(o_y+.5 -offset),     .0,
            (o_x-.1),                   -(o_y+.5 -offset),     .0,
            (o_x+.1),                   -(o_y),                .0,
            (o_x-.1),                   -(o_y-.5 +offset),     .0,
            (o_x),                      -(o_y-.5 +offset),     .0]
        
arrow_down = [-(o_y),               +(o_x-.2),                   z, 
              -(o_y+.5 -offset),    +(o_x+.0),                  .0,
              -(o_y+.5 -offset),    +(o_x+.1+offset_thick),     .0,
              -(o_y),               +(o_x-.1+offset_thick),     .0,
              -(o_y-.5 +offset),    +(o_x+.1+offset_thick),     .0,
              -(o_y-.5 +offset),    +(o_x),                     .0]

arrow_up = [+(o_y),               -(o_x-.2),                   z, 
            +(o_y+.5 -offset),    -(o_x+.0),                  .0,
            +(o_y+.5 -offset),    -(o_x+.1+offset_thick),     .0,
            +(o_y),               -(o_x-.1+offset_thick),     .0,
            +(o_y-.5 +offset),    -(o_x+.1+offset_thick),     .0,
            +(o_y-.5 +offset),    -(o_x),                     .0]     




def move_arrow_left(arrow):
    new_pos = []
    for coord in range(0,len(arrow)):
        my_pos = float(arrow[coord])
        if coord % 3 == 0:
            my_pos = my_pos - 0.6
            my_pos = float("{0:.2f}".format(my_pos))
        new_pos.append(float(my_pos))
    return new_pos

def move_arrow_right(arrow):
    new_pos = []
    for coord in range(0,len(arrow)):
        my_pos = float(arrow[coord])
        if coord % 3 == 0:
            my_pos = my_pos + 0.6
            my_pos = float("{0:.2f}".format(my_pos))
        new_pos.append(float(my_pos))

    return new_pos

def move_arrow_down(arrow):
    new_pos = []
    for coord in range(0,len(arrow)):
        my_pos = float(arrow[coord])
        if (coord % 3) == 1:
            my_pos = my_pos - 0.6
            my_pos = float("{0:.2f}".format(my_pos))
        new_pos.append(float(my_pos))

    return new_pos

def move_arrow_up(arrow):
    new_pos = []
    for coord in range(0,len(arrow)):
        my_pos = float(arrow[coord])
        if (coord % 3) == 1:
            my_pos = my_pos + 0.6
            my_pos = float("{0:.2f}".format(my_pos))
        new_pos.append(float(my_pos))

    return new_pos


class Triangle:


    def __init__(self):

        self.figures = []

        print "qua", arrow_down
        
        #pos_dx = move_arrow_right(arrow_dx)
        #pos_sx = move_arrow_left(arrow_up)
        pos_down = move_arrow_down(arrow_dx)
        pos_up = move_arrow_up(arrow_up)
        pos_down_sx = move_arrow_left(pos_down)
        pos_down_dx = move_arrow_right(pos_down)
        pos_up_sx = move_arrow_left(pos_up)
        pos_up_dx = move_arrow_right(pos_up)

     
        self.vertices = pyglet.graphics.vertex_list(6, ('v3f', pos_down_sx),
                                                       ('c3B', [100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220]))



        self.vertices_2 = pyglet.graphics.vertex_list(6, ('v3f', pos_down_dx), 
                                                         ('c3b', [100,00,220, 100,00,220, 100,00,220, 100,00,220, 100,00,220, 100,200,020]))

        self.vertices_3 = pyglet.graphics.vertex_list(6, ('v3f', pos_up_sx), 
                                                         ('c3b', [100,00,220, 100,00,220, 100,00,220, 100,00,220, 100,00,220, 100,200,020]))

        self.vertices_4 = pyglet.graphics.vertex_list(6, ('v3f', pos_up_dx),
                                                         ('c3B', [200,00,220, 0,110,192, 129,0,238, 77,87,81, 1,22,222, 223,12,123]))

        self.figures.append(self.vertices)
        self.figures.append(self.vertices_2)
        self.figures.append(self.vertices_3)
        self.figures.append(self.vertices_4)



class MyWindow(pyglet.window.Window):
        def __init__(self, *args, **kwargs):
            super(MyWindow, self).__init__(*args, **kwargs)
            self.set_minimum_size(400,300)
            glClearColor(0, 0, 0, 0)
            pyglet.clock.schedule_interval(self.update, 1.0/24.0)
            self.triangle = Triangle()

        def on_draw(self):
            self.clear()

            for fig in self.triangle.figures:
                fig.draw(pyglet.gl.GL_POLYGON)
                #fig.draw(pyglet.gl.GL_POLYGON)

        def on_resize(self, width, height):
            glViewport(0, 0, width, height)

        def update(self, dt):
            pass


if __name__ == "__main__":
    window = MyWindow(1024, 768, "test directions", resizable=False)
    #window.on_draw()
    pyglet.app.run()
