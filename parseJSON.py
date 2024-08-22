import json
from pyvis.network import Network
import networkx as nx
import os

# Function to read and parse the JSON file
def read_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

# Define a function to map course codes to colors
def get_color(course_code):
    color_mapping = {
        "MATH": "blue",
        "PHGN": "green",
        "CSCI": "purple",
        "CHGN": "orange",
        # Add more mappings as needed
    }
    prefix = course_code[:4]
    return color_mapping.get(prefix, "gray")  # Default color if prefix not found

# Function to create the network using pyvis and NetworkX graph
def create_network_and_graph(data):
    net = Network(directed=True, height='750px', width='100%', bgcolor='#222222', font_color='white')
    net.toggle_physics(True)
    G = nx.DiGraph()

    # Add nodes and edges
    course_dict = {}

    # First pass to add all nodes
    for course in data:
        course_code = course['courseCode']
        course_title = course['courseTitle']
        course_credits = course['courseCredits']
        label = f"{course_code}"
        color = get_color(course_code)
        course_dict[course_code] = course
        net.add_node(course_code, label=label, color=color, size=15)
        G.add_node(course_code, title=course_title, credits=course_credits)

    # Second pass to add edges
    for course in data:
        course_code = course['courseCode']
        prereqs = course.get('coursePrereqs', [])
        coreqs = course.get('courseCoreqs', [])

        for prereq in prereqs:
            if prereq in course_dict:
                net.add_edge(prereq, course_code, width=2)
                G.add_edge(prereq, course_code)
            else:
                # Add a placeholder node for prerequisites not in the file
                net.add_node(prereq, label=prereq, color='red', size=15)
                net.add_edge(prereq, course_code, width=2)
                G.add_node(prereq, title="Unknown Course", credits=0)
                G.add_edge(prereq, course_code)

        for coreq in coreqs:
            if coreq in course_dict:
                net.add_edge(coreq, course_code, width=2, dashes=True)
                G.add_edge(coreq, course_code)
            else:
                # Add a placeholder node for corequisites not in the file
                net.add_node(coreq, label=coreq, color='red', size=15)
                net.add_edge(coreq, course_code, width=2, dashes=True)
                G.add_node(coreq, title="Unknown Course", credits=0)
                G.add_edge(coreq, course_code)

    return net, G

# Load the JSON data
data = read_json('coursesMINES.json')

# Create the network and graph
net, G = create_network_and_graph(data)

# Save and visualize the network
output_file_network = 'courses_network.html'
net.write_html(output_file_network)  # Use write_html instead of show

# Save the graph in GraphML format
output_file_graph = 'courses_graph.graphml'
nx.write_graphml(G, output_file_graph)

# Ensure the HTML and GraphML files are saved and notify the user
if os.path.exists(output_file_network):
    print(f"Network visualization saved to {output_file_network}")
else:
    print("There was an error saving the network visualization.")

if os.path.exists(output_file_graph):
    print(f"Graph saved to {output_file_graph}")
else:
    print("There was an error saving the graph.")