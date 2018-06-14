from pyglet.gl import *
import time

class Triangle:
	def __init__(self):
		self.vertices = pyglet.graphics.vertex_list(3, ('v3f', [-0.5,-0.5,0.0, 0.5,-0.5,0.0, 0.0,0.5,0.0]),
														('c3B', [100,200,220, 200,110,192, 129,200,238]))

class MyWindow(pyglet.window.Window):
		def __init__(self, *args, **kwargs):
			super(MyWindow, self).__init__(*args, **kwargs)
			self.set_minimum_size(400,300)
			glClearColor(0, 0, 0, 0)

			self.triangle = Triangle()

		def on_draw(self):
			self.clear()

			self.triangle.vertices.draw(GL_TRIANGLES)

		def on_resize(self, width, height):
			glViewport(0, 0, width, height)


if __name__ == "__main__":
	window = MyWindow(1280, 720, "test directions", resizable=False)
	#window.on_draw()
	pyglet.app.run()