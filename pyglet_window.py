from pyglet.gl import *
import time


o_x = .0
o_y = .0
z = .0

offset_thick = .05  

offset = .10
height = .75
width = .3
rapp1 = float(1024.0/768.0)
rapp2 = float(768.0/1024.0)



arrow_sx = [-width/2+offset,    0,             0,
             width/2,           height/2,      0,
             width/2-offset,    height/2,      0,
            -width/2,           0,             0,
             width/2-offset,   -height/2,      0,
             width/2,          -height/2,      0]

arrow_dx = [  width/2-offset,    0,             0,
             -width/2,           height/2,      0,
             -width/2+offset,    height/2,      0,
              width/2,           0,             0,
             -width/2+offset,   -height/2,      0,
             -width/2,          -height/2,      0]


arrow_up = [          0*rapp2,   -(-width/2+offset)*rapp1,        0,
            (+height/2)*rapp2,   -(width/2)*rapp1,                0,
            (+height/2)*rapp2,   -(width/2-offset)*rapp1,         0,
                      0*rapp2,   -(-width/2)*rapp1,               0,
            (-height/2)*rapp2,   -(width/2-offset)*rapp1,         0,
            (-height/2)*rapp2,   -(width/2)*rapp1,                0]

arrow_down = [        0*rapp2,   +(-width/2+offset)*rapp1,        0,
            (+height/2)*rapp2,   +(width/2)*rapp1,                0,
            (+height/2)*rapp2,   +(width/2-offset)*rapp1,         0,
                      0*rapp2,   +(-width/2)*rapp1,               0,
            (-height/2)*rapp2,   +(width/2-offset)*rapp1,         0,
            (-height/2)*rapp2,   +(width/2)*rapp1,                0]

arrows = {'sx': arrow_sx,
          'dx': arrow_dx,
          'up': arrow_up,
          'down': arrow_down
          }

def move_arrow(my_arrow, offset):
    new_pos = []


    for coord in range(0,len(my_arrow)):
        my_pos = float(my_arrow[coord])
        if coord % 3 == 0:
            my_pos = my_pos + offset
            my_pos = float("{0:.2f}".format(my_pos))
        new_pos.append(float(my_pos))

    return new_pos

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
    return move_arrow(arrow, + 0.6)
   
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


def create_multi_arrow(pos):
    figures = []
    for i in range(-2,2.5,1.0):
        vertices = pyglet.graphics.vertex_list(6, ('v3f', pos),
                                                       ('c3B', [100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220]))

        figures.append(vertices)

    return figures


class Triangle:


    def __init__(self):
       
       ''' 
        self.fig1 = pyglet.graphics.vertex_list(6, ('v3f', arrow_up),
                                                       ('c3B', [100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220]))


        self.fig2 = pyglet.graphics.vertex_list(6, ('v3f', arrow_down),
                                                       ('c3B', [100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220]))

        self.figures.append(self.fig1)
        self.figures.append(self.fig2)

        '''
        #pos_dx = move_arrow_right(arrow_dx)
        #pos_sx = move_arrow_left(arrow_up)
        #pos_down = move_arrow_down(arrow_dx)
        #pos_up = move_arrow_up(arrow_up)
        #pos_down_sx = move_arrow_left(pos_down)
        #pos_down_dx = move_arrow_right(pos_down)
        #pos_up_sx = move_arrow_left(pos_up)
        #pos_up_dx = move_arrow_right(pos_up)

     
       


        #self.vertices_2 = pyglet.graphics.vertex_list(6, ('v3f', pos_down_dx), 
                                                        # ('c3b', [100,00,220, 100,00,220, 100,00,220, 100,00,220, 100,00,220, 100,200,020]))

        #self.vertices_3 = pyglet.graphics.vertex_list(6, ('v3f', pos_up_sx), 
                                                         #('c3b', [100,00,220, 100,00,220, 100,00,220, 100,00,220, 100,00,220, 100,200,020]))

        #self.vertices_4 = pyglet.graphics.vertex_list(6, ('v3f', pos_up_dx),
                                                         #('c3B', [200,00,220, 0,110,192, 129,0,238, 77,87,81, 1,22,222, 223,12,123]))

        #self.figures.append(self.vertices)
        #self.figures.append(self.vertices_2)
        #self.figures.append(self.vertices_3)
        #self.figures.append(self.vertices_4)


class MyWindow(pyglet.window.Window):
        def __init__(self, *args, **kwargs):
            super(MyWindow, self).__init__(*args, **kwargs)
            self.set_minimum_size(400,300)
            glClearColor(0, 0, 0, 0)
            pyglet.clock.schedule_interval(self.update, 5.0/24.0)
            self.triangle = Triangle()
            self.arrow_dx_new = arrow_dx[:]
            self.moving = 0
            print height/2
            print width/2
            print rapp1, rapp2
           

            

        def on_draw(self):
            self.clear()
            self.figures = []
            self.fig1 = pyglet.graphics.vertex_list(6, ('v3f', self.arrow_dx_new),
                                                       ('c3B', [100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220]))

            self.figures.append(self.fig1)
            for fig in self.figures:
                fig.draw(pyglet.gl.GL_POLYGON)
            



            #pyglet.graphics.draw(8, pyglet.gl.GL_LINES, ("v2f", (-1,-1, 1,1, -1,1, 1,-1, 0,1, 0,-1, 1,0, -1,0)))
            #pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ("v2f", ((-width/2),(+height/2), (-width/2),(-height/2)))) #vertical
            #horizontal #x*rapp2, y*rapp1
            #pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ("v2f", ((+height/2)*rapp2,(+width/2)*rapp1, (-height/2)*rapp2,(+width/2)*rapp1)))
            #pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ("v2f", ((+height/2)*rapp2,(-width/2)*rapp1, (-height/2)*rapp2,(-width/2)*rapp1)))
            
        def on_resize(self, width, height):
            glViewport(0, 0, width, height)

        def update(self, dt):
            self.arrow_dx_new = move_arrow(self.arrow_dx_new, 0.2)
            if self.moving%4 == 0:
                self.arrow_dx_new = arrow_dx[:]
            self.moving += 1



if __name__ == "__main__":
    window = MyWindow(1024, 768, "test directions", resizable=False)
    #window.on_draw()
    pyglet.app.run()