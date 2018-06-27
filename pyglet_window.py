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



sx = [[      -width/2+offset,    0,             0,
			 width/2,           height/2,      0,
			 width/2-offset,    height/2,      0,
			-width/2,           0,             0,
			 width/2-offset,   -height/2,      0,
			 width/2,          -height/2,      0]]

dx = [[        width/2-offset,    0,             0,
			 -width/2,           height/2,      0,
			 -width/2+offset,    height/2,      0,
			  width/2,           0,             0,
			 -width/2+offset,   -height/2,      0,
			 -width/2,          -height/2,      0]]


up = [[      0*rapp2,   -(-width/2+offset)*rapp1,        0,
			(+height/2)*rapp2,   -(width/2)*rapp1,                0,
			(+height/2)*rapp2,   -(width/2-offset)*rapp1,         0,
					  0*rapp2,   -(-width/2)*rapp1,               0,
			(-height/2)*rapp2,   -(width/2-offset)*rapp1,         0,
			(-height/2)*rapp2,   -(width/2)*rapp1,                0]]

down = [[    0*rapp2,   +(-width/2+offset)*rapp1,        0,
			(+height/2)*rapp2,   +(width/2)*rapp1,                0,
			(+height/2)*rapp2,   +(width/2-offset)*rapp1,         0,
					  0*rapp2,   +(-width/2)*rapp1,               0,
			(-height/2)*rapp2,   +(width/2-offset)*rapp1,         0,
			(-height/2)*rapp2,   +(width/2)*rapp1,                0]]

####COLORS
blue = [0,0,205, 0,0,205, 30,144,255, 0,0,205, 0,0,205, 0,0,205]
red = [139,0,0, 240,128,128, 139,0,0, 139,0,0, 139,0,0, 139,0,0]
white = [255,255,240, 255,255,240, 248,248,255, 255,255,240, 255,255,240, 255,255,240]
green = [34,139,34, 50,205,50, 34,139,34, 34,139,34, 34,139,34, 34,139,34]

def scale_figure(my_figure, scaling):
	new_fig = []
	for item in my_figure:
		half_fig = []
		for coord in item:
			half_fig.append(coord*scaling)
		new_fig.append(half_fig)
	return new_fig


def draw_go_back():
	mini_offset = .05
	back_a = [(+width/2),			 (-height/2)+mini_offset,0]
	back_b = [(+width/2)+mini_offset,(-height/2)+mini_offset,0]
	back_c = [(+width/2)+mini_offset,(+height/2),			   0]
	back_d = [(-width/2),(+height/2), 0]
	back_e = [-(+width/2),			 (-height/2)+mini_offset,0]
	back_f = [-(+width/2)+mini_offset,(-height/2)+mini_offset,0]
	back_g = [-(+width/2)+mini_offset, (+height/2)-mini_offset,0]
	back_h = [(+width/2), (+height/2)-mini_offset,0]


	right_back = [(+width/2),			 (+height/2),			   0,
				  (+width/2)+mini_offset,(+height/2),			   0,
				  (+width/2)+mini_offset,(-height/2)+mini_offset*2,0,
				  (+width/2),			 (-height/2)+mini_offset*2,0]

	left_back = [-(+width/2),			 (+height/2),			 0,
			     -(+width/2)+mini_offset,(+height/2),			 0,
			     -(+width/2)+mini_offset,(-height/2)+mini_offset,0,
			     -(+width/2),			 (-height/2)+mini_offset,0]
	
	up_back = [(-width/2),(+height/2), 0,
			   (+width/2),(+height/2), 0,
			   (+width/2),(+height/2)-mini_offset, 0,
			   (-width/2),(+height/2)-mini_offset, 0,]

	#back_first =  back_a +back_b + back_c +back_h +back_a+ back_h + back_g #+back_d + back_c #+ back_b #+ back_h  # +back_a +back_c + back_h# +back_b 

	#pyglet.graphics.draw(len(back_first)/3, pyglet.gl.GL_POLYGON, ("v3f", (back_first)))
	#pyglet.graphics.draw(len(right_back)/3, pyglet.gl.GL_POLYGON, ("v3f", (right_back)))#vertical dx big
	#pyglet.graphics.draw(4, pyglet.gl.GL_POLYGON, ("v3f", (left_back))) #vertical sx big
	#pyglet.graphics.draw(4, pyglet.gl.GL_POLYGON, ("v3f", (up_back)))
	down_back = down[:]
	down_back = scale_figure(down_back, 0.65)
	down_back = move_arrow(down_back, -0.22, False)
	down_back = move_arrow(down_back, -0.1185, True)
	#back_first =   up_back + left_back  + down_back + left_back
	#pyglet.graphics.draw(len(back_first)/3, pyglet.gl.GL_POLYGON, ("v3f", (back_first)))

	return [up_back] + [left_back] + [right_back] + down_back
	#pyglet.graphics.draw(6, pyglet.gl.GL_POLYGON, ("v3f", (down_back)))



colors = {'blue': blue,
		  'red': red,
		  'white': white,
		  'green': green  }




def update_coordinates(my_indications):
	j = 0
	for key, value in my_indications.iteritems():
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
	i = 0
	for piece in my_arrow:
		single_pos = []
		for coord in piece:
			my_pos = float(coord)
			if i % 3 == flag:
				my_pos = float(my_pos) + float(offset)
				my_pos = float("{0:.2f}".format(my_pos))
			single_pos.append(float(my_pos))
			i += 1
		new_pos.append(single_pos)

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
		vertices = pyglet.graphics.vertex_list(6, ('v3f', pos), ('c3B', [100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220, 100,200,220]))

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

		if 'back' in value[0]:
			if moving%2 == 0:
				my_offset = -20
			else: 
				my_offset = +20

		
		value[2] = move_arrow(value[2], my_offset, horiz)

	return my_indications

def update_moving(my_mov):
	my_mov += 1
	if my_mov == +2:
		my_mov = -2
	return my_mov


arrows = {'sx': sx,
		  'dx': dx,
		  'up': up,
		  'down': down,
		  'back': draw_go_back()
		  }

indications = {'AB:CD:EF:12:34:45': ['sx', 'green']	,
				'AB:C12:EF:12:34:45': ['back', 'blue']			  }
	

class Triangle:


	def __init__(self):
		#pass
		self.indications = update_coordinates(indications)
		

class MyWindow(pyglet.window.Window):
		def __init__(self, *args, **kwargs):
			super(MyWindow, self).__init__(*args, **kwargs)
			glClearColor(0, 0, 0, 0)
			pyglet.clock.schedule_interval(self.update, 10.0/24.0)
			self.set_minimum_size(400,300)
			
			self.triangle = Triangle()
			self.moving = 0

		

			

		def on_draw(self):
			self.clear()
			self.figures = []
			for key, value in self.triangle.indications.iteritems():
				for v in value[2]:
					print v
					print len(v), len(colors[value[1]][:len(v)])
					fig = pyglet.graphics.vertex_list(len(v)/3, ('v3f', v), ('c3B', colors[value[1]][:len(v)]))

					self.figures.append(fig)

			for fig in self.figures:
				fig.draw(pyglet.gl.GL_POLYGON)
			
			#draw_go_back()

			#pyglet.graphics.draw(3, pyglet.gl.GL_POLYGON, ('v3f', (0.2,0.3,0.0, .9,-.2,0, -.5,.4,0)))
			pyglet.gl.glLineWidth(20)

			pyglet.graphics.draw(8, pyglet.gl.GL_LINES, ("v2f", (-1,-1, 1,1, -1,1, 1,-1, 0,1, 0,-1, 1,0, -1,0)))
			pyglet.graphics.draw(8, pyglet.gl.GL_LINES, ("v2f", (-.5,1, -.5,-1, .5,1, .5,-1, -1,+.5, +1,+.5, -1,-.5, +1,-.5)))

			pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ("v2f", ((-width/2),(+height/2), (-width/2),(-height/2)))) #vertical sx
			pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ("v2f", ((+width/2),(+height/2), (+width/2),(-height/2)))) #vertical dx

		
			#horizontal #x*rapp2, y*rapp1
			#pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ("v2f", ((+height/2)*rapp2,(+width/2)*rapp1, (-height/2)*rapp2,(+width/2)*rapp1)))
			#pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ("v2f", ((+height/2)*rapp2,(-width/2)*rapp1, (-height/2)*rapp2,(-width/2)*rapp1)))
			
		def on_resize(self, width, height):
			glViewport(0, 0, width, height)

		def update(self, dt):
			animate_arrow(self.triangle.indications, self.moving)
			self.moving = update_moving(self.moving)
			pass
			
			
			


if __name__ == "__main__":
	window = MyWindow(1024, 668, "test directions", resizable=False)
	pyglet.app.run()