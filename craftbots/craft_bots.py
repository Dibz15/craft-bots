from craftbots.world import World
from api.agent_api import AgentAPI
from agents.blank_agent import BlankAgent
import craftbots.view as view
import threading
import random as r
import math
import time

PADDING = 25
NODE_SIZE = 20

simulation_stop = None
sim_stopped = False
gui_updating = False
root = None
world = World()
start_time = time.time()


def default_scenario(modifiers, world_gen_modifiers):
    global world
    for _ in range(modifiers["NUM_OF_ACTORS"]):
        actor = world.add_actor(world.nodes[r.randint(0, world.nodes.__len__() - 1)])
        for _ in range(world_gen_modifiers["ACTOR_NUM_OF_RED_RESOURCES"]):
            world.add_resource(actor, 0)
        for _ in range(world_gen_modifiers["ACTOR_NUM_OF_BLUE_RESOURCES"]):
            world.add_resource(actor, 1)
        for _ in range(world_gen_modifiers["ACTOR_NUM_OF_ORANGE_RESOURCES"]):
            world.add_resource(actor, 2)
        for _ in range(world_gen_modifiers["ACTOR_NUM_OF_BLACK_RESOURCES"]):
            world.add_resource(actor, 3)
        for _ in range(world_gen_modifiers["ACTOR_NUM_OF_GREEN_RESOURCES"]):
            world.add_resource(actor, 4)
        
    for _ in range(world_gen_modifiers["NUM_OF_RED_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 0)
    for _ in range(world_gen_modifiers["NUM_OF_RED_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 0)
    for _ in range(world_gen_modifiers["NUM_OF_RED_SITES"]):
        world.add_site(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 0)
    for _ in range(world_gen_modifiers["NUM_OF_RED_BUILDINGS"]):
        world.add_building(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 0)
        
    for _ in range(world_gen_modifiers["NUM_OF_BLUE_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 1)
    for _ in range(world_gen_modifiers["NUM_OF_BLUE_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 1)
    for _ in range(world_gen_modifiers["NUM_OF_BLUE_SITES"]):
        world.add_site(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 1)
    for _ in range(world_gen_modifiers["NUM_OF_BLUE_BUILDINGS"]):
        world.add_building(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 1)
        
    for _ in range(world_gen_modifiers["NUM_OF_ORANGE_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 2)
    for _ in range(world_gen_modifiers["NUM_OF_ORANGE_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 2)
    for _ in range(world_gen_modifiers["NUM_OF_ORANGE_SITES"]):
        world.add_site(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 2)
    for _ in range(world_gen_modifiers["NUM_OF_ORANGE_BUILDINGS"]):
        world.add_building(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 2)
        
    for _ in range(world_gen_modifiers["NUM_OF_BLACK_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 3)
    for _ in range(world_gen_modifiers["NUM_OF_BLACK_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 3)
    for _ in range(world_gen_modifiers["NUM_OF_BLACK_SITES"]):
        world.add_site(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 3)
    for _ in range(world_gen_modifiers["NUM_OF_BLACK_BUILDINGS"]):
        world.add_building(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 3)
        
    for _ in range(world_gen_modifiers["NUM_OF_GREEN_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 4)
    for _ in range(world_gen_modifiers["NUM_OF_GREEN_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 4)
    for _ in range(world_gen_modifiers["NUM_OF_GREEN_SITES"]):
        world.add_site(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 4)
    for _ in range(world_gen_modifiers["NUM_OF_GREEN_BUILDINGS"]):
        world.add_building(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 4)


def start_simulation(agent_class=BlankAgent, use_gui=True, scenario=default_scenario):
    sim_thread = threading.Thread(target=prep_simulation, args=(agent_class, use_gui, scenario), daemon=True)
    sim_thread.start()
    while not sim_stopped:
        time.sleep(1)
    return world.total_score


def prep_simulation(agent_class, use_gui, scenario):
    global world
    world_gen_modifiers = get_world_gen_modifiers()
    modifiers = get_modifiers()
    rules = get_rules()
    world = World(modifiers, world_gen_modifiers, rules)
    scenario(modifiers, world_gen_modifiers)

    if rules["LIMITED_COMMUNICATIONS"]:
        agents = []
        for actor in world.get_all_actors():
            new_agent = agent_class()
            new_agent.api = AgentAPI(world, [actor.id])
            new_agent.world_info = new_agent.api.get_world_info()
            agents.append(new_agent)
    else:
        agents = [agent_class()]
        actor_ids = []
        for actor in world.get_all_actors():
            actor_ids.append(actor.id)
        agents[0].api = AgentAPI(world, actor_ids)
        agents[0].world_info = agents[0].api.get_world_info()

    if rules["RT_OR_LOCK_STEP"] == 0:
        global simulation_stop
        simulation_stop = call_repeatedly(1 / rules["TICK_HZ"], refresh_world, agents)

        if use_gui:
            gui = init_gui()
            refresh_gui(gui, rules["TICK_HZ"])
            gui.mainloop()

    else:
        if use_gui:
            gui = init_gui()
            sim_thread = threading.Thread(target=lock_step_sim, args=(agents, gui.update_model))
            sim_thread.start()
            gui.mainloop()
        else:
            sim_thread = threading.Thread(target=lock_step_sim, args=(agents, None))
            sim_thread.start()


def lock_step_sim(agents, update_model):
    global world
    while not sim_stopped:
        for agent in agents:
            agent.world_info = agent.api.get_world_info()
            agent.get_next_commands()

        world.run_tick()

        for agent in agents:
            agent.api.num_of_current_commands = 0

        if world.rules["TIME_LENGTH_TYPE"] == 0:
            if time.time() - world.rules["SIM_LENGTH"] >= start_time:
                return on_close()
        else:
            if world.tick >= world.rules["SIM_LENGTH"] * world.rules["TICK_HZ"]:
                return on_close()

        if update_model is not None:
            update_model()


def refresh_gui(gui, tick_hz):

    def refresh_gui_wrapper():
        if not sim_stopped:
            global gui_updating
            gui_updating = True
            gui.update_model()
            gui_updating = False
            refresh_gui(gui, tick_hz)

    gui.after(math.ceil(1000 / tick_hz), refresh_gui_wrapper)


def refresh_world(agents):
    global world
    for agent in agents:
        if not agent.thinking:
            agent.thinking = True
            agent.world_info = agent.api.get_world_info()
            agent_thread = threading.Thread(target=agent.get_next_commands)
            agent_thread.start()
    world.run_tick()
    for agent in agents:
        agent.api.num_of_current_commands = 0
    if world.rules["TIME_LENGTH_TYPE"] == 0:
        if time.time() - world.rules["SIM_LENGTH"] >= start_time:
            return on_close()
    else:
        if world.tick >= world.rules["SIM_LENGTH"] * world.rules["TICK_HZ"]:
            return on_close()


def call_repeatedly(interval, func, *args):
    stopped = threading.Event()

    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            func(*args)
    threading.Thread(target=loop, daemon=True).start()
    return stopped.set


def init_gui():
    global root, world
    root = view.tk.Tk()

    width = world.world_gen_modifiers["WIDTH"]
    height = world.world_gen_modifiers["HEIGHT"]
    root.title("CraftBots")
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.geometry(str(width + PADDING * 2) + "x" + str(height + PADDING * 2))
    return view.GUI(world, width=width, height=height, padding=PADDING, node_size=NODE_SIZE, master=root)


def on_close():
    global world
    print("Simulation time up")
    global sim_stopped, simulation_stop
    if simulation_stop is not None:
        simulation_stop()
    sim_stopped = True
    if root is not None:
        try:
            root.destroy()
        except:
            return on_close()
    return world.total_score


def get_world_gen_modifiers():
    return read_ini_file("craftbots/initialisation_files/world_gen_modifiers",
                         "craftbots/initialisation_files/default_world_gen_modifiers")


def get_modifiers():
    return read_ini_file("craftbots/initialisation_files/modifiers", "craftbots/initialisation_files/default_modifiers")
    
    
def get_rules():
    return read_ini_file("craftbots/initialisation_files/rules", "craftbots/initialisation_files/default_rules")


def read_ini_file(path, default_path):
    default_file = open(default_path, "r")
    parameters = {}
    for line in default_file:
        data = line.strip("\n").split(" ")
        if data[0] != '' and data[0][0] != "#":
            try:
                parameters[data[0]] = int(data[2])
                continue
            except ValueError:
                try:
                    parameters[data[0]] = float(data[2])
                    continue
                except ValueError:
                    temp = []
                    for value in data[2].split(","):
                        temp.append(int(value))
                    parameters[data[0]] = temp
    default_file.close()
    try:
        file = open(path, "r")
        for line in file:
            data = line.strip("\n").split(" ")
            if data[0] != '' and data[0][0] != "#":
                try:
                    parameters[data[0]] = int(data[2])
                    continue
                except ValueError:
                    try:
                        parameters[data[0]] = float(data[2])
                        continue
                    except ValueError:
                        temp = []
                        for value in data[2].split(","):
                            temp.append(int(value))
                        parameters[data[0]] = temp
        file.close()
    except FileNotFoundError:
        pass
    return parameters
