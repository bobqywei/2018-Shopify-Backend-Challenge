"""
Shopify Backend Intern Coding Challenge 2018
Written by: Bob Wei (Python 3.6.0)

Note: the following code works for both challenges simply by changing the id query parameter in the API variable
Also, since it was not specified, depth is defined as the distance from the root node (i.e. root node has depth 0)
"""

import requests
import json
import math

API_ENDPOINT = "https://backend-challenge-summer-2018.herokuapp.com/challenges.json?id=2&page="


# calculates number of pages to scrape and fills list with nodes from api endpoint
def fill_nodes(node_list, api):
	response = requests.get(api + "1").json()["pagination"]
	num_pages = int(math.ceil(response["total"] / response["per_page"]))

	for number in range(1, num_pages + 1):
		node_list += requests.get(api + str(number)).json()["menus"]


# searches through all children: looks for invalid menus and determines max depth of menu
def search_children(parent_id, root, depth):
	current_node_depth = depth

	for child_id in nodes[parent_id - 1]["child_ids"]:

		# validates that the child_id is an actual node id, otherwise, the menu is marked as invalid
		if child_id < 0 or child_id > len(nodes):
			root["valid"] = False
			root["children"].add(child_id)
			continue

		# checks if the child has the same id as any of its parents
		# a unique id indicates that the child is not a previous node
		if not child_id == root["root_id"] and child_id not in root["children"]:

			# add operation must be done here due to the above if statement and the recursive call below
			root["children"].add(child_id)

			# Covers two separate Edge Cases:
			# 1. if the menu has a child that is a root node of another menu, then the menu is invalid
			# 2. if a child has an incorrect parent_id value, then the menu is invalid
			if "parent_id" not in nodes[child_id - 1].keys() or not nodes[child_id - 1]["parent_id"] == parent_id:
				root["valid"] = False

			# the depth of the entire sub-branch is determined recursively and the max is taken
			depth = max(depth, search_children(child_id, root, current_node_depth + 1))

		# a matching id indicates a cyclic (invalid) menu
		else:
			root["valid"] = False
			root["children"].add(child_id)

	# returns the depth of the current node's longest sub-branch
	return depth


# fills the output dictionary
def create_output(out_dict):
	# iterates through only the root nodes
	# node is a root if it does not contain a parent id
	for node in nodes:
		if "parent_id" not in node.keys():

			# creates new root node and determines children and depth of longest branch
			# a set is used for storing the children ids since it provides constant time searching
			new_root = {"root_id": node["id"], "children": set(), "valid": True, "depth": None}
			new_root["depth"] = search_children(node["id"], new_root, 0)

			# checks validity and fills the output dictionary
			if new_root["depth"] > 4 or not new_root["valid"]:
				out_dict["invalid_menus"].append({"root_id": new_root["root_id"], "children": sorted(list(new_root["children"]))})
			else:
				out_dict["valid_menus"].append({"root_id": new_root["root_id"], "children": sorted(list(new_root["children"]))})


# outputs final json data to a json file
def output_to_file(data, filename):
	with open(filename, 'w') as out_file:
		json.dump(data, out_file)


if __name__ == '__main__':
	nodes = []  # list for storing every menu node
	output = {"valid_menus": [], "invalid_menus": []}  # dictionary for final output

	fill_nodes(nodes, API_ENDPOINT)
	create_output(output)

	print(json.dumps(output, indent=2))  # prints output to console
	output_to_file(output, "output.json")  # save output to json file
