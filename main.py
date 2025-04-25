from pyvis.network import Network
import json

def format_title(text, max_length=50):
    """Format long text into multiple lines."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        # +1 for the space
        if current_length + len(word) + 1 <= max_length:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)

# Define colors for each category
CATEGORY_COLORS = {
    "Math": "#9b5de5",  # Blue
    "Physics": "#f15bb5",  # Dark Blue
    "Systems": "#fee440",  # Darker Blue
    "Programming": "#00bbf9",  # Darker Orange
    "AI/ML": "#00f5d4",  # Orange
    "External": "#808080"  # Gray
}

# Create network
net = Network(height="900px", width="100%", bgcolor="#ffffff", font_color="black")
net.force_atlas_2based(gravity=-30, spring_length=100)

# Load JSON data
with open('data/school/classes.json', 'r') as f:
    classes = json.load(f)

# Add legend nodes (fixed position at upper left)
x_pos = -1200  # Starting x position for legend
y_pos = -600   # Starting y position for legend
for idx, (category, color) in enumerate(CATEGORY_COLORS.items()):
    legend_node_id = f"legend_{category}"
    net.add_node(
        legend_node_id,
        label=category,
        color=color,
        x=x_pos,
        y=y_pos + idx * 60,  # Stack vertically
        physics=False,  # Disable physics for legend nodes
        size=5,  # Smaller size for legend nodes
        font={'size': 1}
    )

# Create a set of all unique class names (including prerequisites)
all_class_names = set()
for class_info in classes:
    all_class_names.add(class_info['name'])
    all_class_names.update(class_info['prerequisites'])

# First add all nodes, including prerequisites that might not be in the main list
for class_name in all_class_names:
    # Find the class info if it exists in the main list
    class_info = next((c for c in classes if c['name'] == class_name), None)
    
    if class_info:
        # For classes in our main list, use their full info
        category = class_info['category']
        title = format_title(class_info['title'])
        hover_text = f"Name: {class_name}\nCategory: {category}\nWhat:\n{title}"
    else:
        # For prerequisites not in our main list, use default values
        category = "External"
        hover_text = "External Prerequisite"
    
    net.add_node(
        class_name,
        label=class_name,
        title=hover_text,
        category=category,
        color=CATEGORY_COLORS.get(category, "#808080")  # Default to gray for external prerequisites
    )

# Then add all edges
for class_info in classes:
    source = class_info['name']
    for prereq in class_info['prerequisites']:
        net.add_edge(prereq, source, arrows='to')

# Get adjacency list
neighbor_map = net.get_adj_list()

# Update node information with neighbor data and calculate values
for node in net.nodes:
    # Skip legend nodes
    if node["id"].startswith("legend_"):
        continue
        
    neighbors = neighbor_map[node["id"]]
    # Count incoming and outgoing connections
    outcoming_classes = [class_info["name"] for class_info in classes if node["id"] in class_info["prerequisites"]]
    incoming_classes = []
    for class_info in classes:
        if node["id"] == class_info["name"]:
            incoming_classes = class_info["prerequisites"]
            break
    
    # Update node title with neighbor information
    original_title = node["title"]
    node["title"] = f"{original_title}\n\nDependencies:\n"
    for each_class in incoming_classes:
        node["title"] += f"• {each_class}\n"
    
    # Set node value based on total connections (affects node size)
    # node["value"] = 1.1 ** len(neighbors)
    weight = 1.2 if node["category"] in ["Physics", "Math"] else 1.1
    node["value"] = weight ** len(outcoming_classes)

# Generate the HTML file
net.write_html("class_prerequisites.html")
