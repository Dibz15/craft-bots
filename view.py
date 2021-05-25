import tkinter as tk


class GUI(tk.Frame):
    def __init__(self, world,  master=None):
        super().__init__(master)
        self.master = master
        self.world = world
        self.graph = tk.Canvas(self, bg="white", height=350, width=350)
        self.update_graph()
        self.actors = []
        for actor in self.world.actors:
            self.graph.create_oval(actor.node.x * 3 + 22, actor.node.y * 3 + 22, actor.node.x * 3 + 28, actor.node.y * 3 + 28, fill="red")
            self.actors.append((actor, self.graph.find_all()[-1:][0]))
        self.update_actors()
        self.graph.pack()
        self.pack()

    def update_graph(self):
        self.graph.delete("all")
        for edge in self.world.edges:
            x1 = edge.node_a.x * 3 + 25
            y1 = edge.node_a.y * 3 + 25
            x2 = edge.node_b.x * 3 + 25
            y2 = edge.node_b.y * 3 + 25
            self.graph.create_line(x1, y1, x2, y2, fill="blue")
        for node in self.world.nodes:
            x = node.x * 3 + 25
            y = node.y * 3 + 25
            self.graph.create_oval(x - 5, y - 5, x + 5, y + 5, fill="black")

    def update_actors(self):
        for actor in self.actors:
            dx = actor[0].node.x * 3 + 22 - self.graph.coords(actor[1])[0]
            dy = actor[0].node.y * 3 + 22 - self.graph.coords(actor[1])[1]
            self.graph.move(actor[1], dx, dy)
