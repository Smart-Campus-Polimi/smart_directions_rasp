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



sx = [      -width/2+offset,    0,             0,
			 width/2,           height/2,      0,
			 width/2-offset,    height/2,      0,
			-width/2,           0,             0,
			 width/2-offset,   -height/2,      0,
			 width/2,          -height/2,      0]

dx = [        width/2-offset,    0,             0,
			 -width/2,           height/2,      0,
			 -width/2+offset,    height/2,      0,
			  width/2,           0,             0,
			 -width/2+offset,   -height/2,      0,
			 -width/2,          -height/2,      0]


up = [      0*rapp2,   -(-width/2+offset)*rapp1,        0,
			(+height/2)*rapp2,   -(width/2)*rapp1,                0,
			(+height/2)*rapp2,   -(width/2-offset)*rapp1,         0,
					  0*rapp2,   -(-width/2)*rapp1,               0,
			(-height/2)*rapp2,   -(width/2-offset)*rapp1,         0,
			(-height/2)*rapp2,   -(width/2)*rapp1,                0]

down = [    0*rapp2,   +(-width/2+offset)*rapp1,        0,
			(+height/2)*rapp2,   +(width/2)*rapp1,                0,
			(+height/2)*rapp2,   +(width/2-offset)*rapp1,         0,
					  0*rapp2,   +(-width/2)*rapp1,               0,
			(-height/2)*rapp2,   +(width/2-offset)*rapp1,         0,
			(-height/2)*rapp2,   +(width/2)*rapp1,                0]

####COLORS
blue = [0,0,205, 0,0,205, 30,144,255, 0,0,205, 0,0,205, 0,0,205]
red = [139,0,0, 240,128,128, 139,0,0, 139,0,0, 139,0,0, 139,0,0]
white = [255,255,240, 255,255,240, 248,248,255, 255,255,240, 255,255,240, 255,255,240]
green = [34,139,34, 50,205,50, 34,139,34, 34,139,34, 34,139,34, 34,139,34]

colors = {'blue': blue,
		  'red': red,
		  'white': white,
		  'green': green  }

arrows = {'sx': sx,
		  'dx': dx,
		  'up': up,
		  'down': down
		  }

indications = {'AB:CD:EF:12:34:45': ['up', 'green'],
			   'AB:12:EF:12:34:45': ['up', 'blue'],
			   'AB:CD:43:12:34:45': ['up', 'red'],
			   'AB:CD:HH:12:34:45': ['up', 'white']
			  }

def update_coordinates(my_indications):
	j = 0
	for key, value in my_indications.iteritems():
		print key
		if len(my_indications) == 1:
			my_indications[key].append(arrows[value[0]])

		if len(my_indications) == 2:
			if j == 0:
				my_indications[key].append(move_arrow_right(arrows[value[0]]))
			if j == 1:
				my_indications[key].append(move_arrow_left(arrows[value[0]]))

		if len(my_indications) == 3:
			if j == 0:
				my_indications[key].append(move_arrow_up(move_arrow_right(arrows[value[0]])))
			if j == 1:
				my_indications[key].append(move_arrow_up(move_arrow_left(arrows[value[0]])))
			if j == 2:
				my_indications[key].append(move_arrow_down(arrows[value[0]]))

		if len(my_indications) == 4:
			if j == 0:
				my_indications[key].append(move_arrow_up(move_arrow_right(arrows[value[0]])))
			if j == 1:
				my_indications[key].append(move_arrow_up(move_arrow_left(arrows[value[0]])))
			if j == 2:
				my_indications[key].append(move_arrow_down(move_arrow_right(arrows[value[0]])))
			if j == 3:
				my_indications[key].append(move_arrow_down(move_arrow_left(arrows[value[0]])))

		j += 1

	return my_indications

def move_arrow(my_arrow, offset, horiz):
	new_pos = []

	if horiz:
		flag = 0
	else:
		flag = 1

	for coord in range(0,len(my_arrow)):
		my_pos = float(my_arrow[coord])
		if coord % 3 == flag:
			my_pos = float(my_pos) + float(offset)
			my_pos = float("{0:.2f}".format(my_pos))
			print offset, my_pos
		new_pos.append(float(my_pos))

	return new_pos

def move_arrow_horiz(my_arrow, offset):
	return move_arrow(my_arrow, offset, horiz=True)

def move_arrow_vertic(my_arrow, offset):
	return move_arrow(my_arrow, offset, horiz=False)

def move_arrow_left(arrow):
	return move_arrow_horiz(arrow, -.6)

def move_arrow_right(arrow):
	return move_arrow_horiz(arrow, +.6)
   
def move_arrow_down(arrow):
	return move_arrow_vertic(arrow, -.6)

def move_arrow_up(arrow):
	return move_arrow_vertic(arrow, +.6)


def create_multi_arrow(pos):
	figures = []
	for i in range(-2,2.5,1.0):
		vertices = pyglet.graphics.vertex_list(6, ('v3f', pos),
													   ('c3B', [100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220]))

		figures.append(vertices)

	return figures

def animate_arrow(my_indications, moving):
	
	for key, value in my_indications.iteritems():
		if 'up' in value[0]:
			horiz = False
			my_offset = +.2
			if moving == 1:
				my_offset = -.6
		if 'down' in value[0]:
			horiz = False
			my_offset = -.2
			if moving == 1:
				my_offset = +.6
		if 'sx' in value[0]:
			horiz = True
			my_offset = -.2
			if moving == 1:
				my_offset = +.6
		if 'dx' in value[0]:
			my_offset = .2
			if moving == 1:
				my_offset = -.6
			horiz = True

		value[2] = move_arrow(value[2], my_offset, horiz)

	return my_indications

def update_moving(my_mov):
	my_mov += 1
	if my_mov == +2:
		my_mov = -2
	return my_mov

class Triangle:


	def __init__(self):


		self.indications = update_coordinates(indications)
		print self.indications
		


class MyWindow(pyglet.window.Window):
		def __init__(self, *args, **kwargs):
			super(MyWindow, self).__init__(*args, **kwargs)
			glClearColor(0, 0, 0, 0)
			pyglet.clock.schedule_interval(self.update, 10.0/24.0)
			self.set_minimum_size(400,300)
			
			self.triangle = Triangle()
			self.moving = 0

			print height/2
			print width/2
			print rapp1, rapp2
		   

			

		def on_draw(self):
			self.clear()
			self.figures = []
			for key, value in self.triangle.indications.iteritems():
				fig = pyglet.graphics.vertex_list(6, ('v3f', value[2]),
		                                               ('c3B', colors[value[1]]))

				self.figures.append(fig)

			for fig in self.figures:
				fig.draw(pyglet.gl.GL_POLYGON)
			
			#pyglet.graphics.draw(8, pyglet.gl.GL_LINES, ("v2f", (-1,-1, 1,1, -1,1, 1,-1, 0,1, 0,-1, 1,0, -1,0)))
			#pyglet.graphics.draw(8, pyglet.gl.GL_LINES, ("v2f", (-.5,1, -.5,-1, .5,1, .5,-1, -1,+.5, +1,+.5, -1,-.5, +1,-.5)))

			#pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ("v2f", ((-width/2),(+height/2), (-width/2),(-height/2)))) #vertical
			#horizontal #x*rapp2, y*rapp1
			#pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ("v2f", ((+height/2)*rapp2,(+width/2)*rapp1, (-height/2)*rapp2,(+width/2)*rapp1)))
			#pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ("v2f", ((+height/2)*rapp2,(-width/2)*rapp1, (-height/2)*rapp2,(-width/2)*rapp1)))
			
		def on_resize(self, width, height):
			glViewport(0, 0, width, height)

		def update(self, dt):
			animate_arrow(self.triangle.indications, self.moving)
			self.moving = update_moving(self.moving)

			
			
			


if __name__ == "__main__":
	window = MyWindow(1024, 668, "test directions", resizable=False)
	pyglet.app.run()