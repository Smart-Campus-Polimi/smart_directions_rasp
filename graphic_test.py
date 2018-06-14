import pyglet
# pick an animated gif file you have in the working directory
ag_file = "giphy_1.gif"
animation = pyglet.resource.animation(ag_file)
sprite = pyglet.sprite.Sprite(animation)
# create a window and set it to the image size
win = pyglet.window.Window(800, 500, "smart directions")
# set window background color = r, g, b, alpha
# each value goes from 0.0 to 1.0
green = 0, 0, 0, 0
pyglet.gl.glClearColor(*green)
@win.event
def on_draw():
    win.clear()
    #sprite.draw()
pyglet.app.run()