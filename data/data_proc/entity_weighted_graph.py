import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.io_utils import jdump, jload
import itertools
import random
from tqdm import tqdm
import json
from utils.io_utils import jload, jdump
from tasks.quality import QuALITY
from tasks.judge_zh import Judge
from utils.io_utils import set_openai_key
from data.entigraph import generate_entities, generate_entity_specific_questions, generate_k_entity_relations, generate_two_entity_relations

class Graph:
    def __init__(self):
        """Initialize an empty graph."""
        self.nodes = set()
        self.edges = {}

    def add_node(self, node):
        """Add a node to the graph."""
        self.nodes.add(node)
        if node not in self.edges:
            self.edges[node] = []

    def add_edge(self, node1, node2, weight):
        """
        Add a weighted edge to the graph.
        Args:
            node1: Starting node.
            node2: Ending node.
            weight: Weight of the edge.
        """
        if node1 not in self.nodes or node2 not in self.nodes:
            raise ValueError("Both nodes must exist in the graph!")
        self.edges[node1].append((node2, weight))
        self.edges[node2].append((node1, weight))  # Undirected edge

    def remove_edges_below_threshold(self, threshold):
        """
        Remove edges with weights below the given threshold.
        Args:
            threshold: The weight threshold.
        """
        for node in self.nodes:
            self.edges[node] = [(neighbor, weight) for neighbor, weight in self.edges[node] if weight >= threshold]

        # Remove dangling edges (reverse connections in an undirected graph)
        for node in self.nodes:
            for neighbor, _ in list(self.edges[node]):
                self.edges[neighbor] = [(n, w) for n, w in self.edges[neighbor] if n != node or w >= threshold]

    def update_edge_weight_by_common_neighbor(self):
        for node in self.nodes:
            neighbors = set(n[0] for n in self.edges[node])
            for i, info in enumerate(self.edges[node]):
                neighbor, weight = info
                cur_neigh = set(n[0] for n in self.edges[neighbor])
                common_elements = neighbors & cur_neigh
                merged_set = neighbors | cur_neigh
                weight = weight*0.5 + len(common_elements) / len(merged_set) * 0.5
                self.edges[node][i] = (neighbor, weight)

    def get_neighbor_combinations(self, k):
        """
        Get all combinations of k-neighbors (connected nodes) in the graph.
        Args:
            k: The size of the neighbor combination (pair, triplet, quadruple, etc.)
        Returns:
            A list of tuples, where each tuple is a set of k nodes.
        """
        neighbor_combinations = set()

        # Iterate over each node and its neighbors
        for node in self.edges:
            neighbors = [neighbor for neighbor, _ in self.edges[node]]
            
            # Get combinations of neighbors of size k
            if len(neighbors) >= k-1:
                for combination in itertools.combinations(neighbors, k - 1):  # k-1 because node is included
                    combination_set = tuple(sorted([node] + list(combination)))  # Sort to ensure uniqueness
                    neighbor_combinations.add(combination_set)

        return list(neighbor_combinations)

    def find_subgraphs(self):
        """
        Find all connected components (subgraphs).
        Returns:
            A list of subgraphs, where each subgraph is a set of nodes.
        """
        visited = set()
        subgraphs = []

        def dfs(node, component):
            """Depth-First Search to explore connected components."""
            visited.add(node)
            component.add(node)
            for neighbor, _ in self.edges[node]:
                if neighbor not in visited:
                    dfs(neighbor, component)

        for node in self.nodes:
            if node not in visited:
                component = set()
                dfs(node, component)
                subgraphs.append(component)

        return subgraphs
    
    def display(self):
        """Display the graph's adjacency list with weights."""
        print("Graph Structure:")
        for node, neighbors in self.edges.items():
            connections = ", ".join([f"{neighbor} (weight: {weight})" for neighbor, weight in neighbors])
            print(f"{node} -> {connections}")

    def get_neighbors(self, node):
        """Get all neighbors of a given node."""
        if node not in self.nodes:
            raise ValueError("Node does not exist in the graph!")
        return self.edges[node]

# create a weighted graph
class EntiGraphs:
    def __init__(self, path, lang = 'zh'):
        self.graphs = []
        self.edge_weight_path = path
        self.lang = lang
        self.names = []
    
    def get_graph_by_file(self, filepath, lang):
        with open(filepath, 'r') as f:
            edge_data = jload(f)
        title = filepath.split('/')[-1].split(' ')[0]
        nodes = edge_data[0]
        edge_data = edge_data[2:]
        graph = Graph()
        for node in nodes:
            graph.add_node(node)
        if lang == 'zh':
            sep = ['与','之间的因果关系']
        pair_list = []
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                pair = (nodes[i], nodes[j])
                pair_list.append(pair)
        for edge, es in zip(edge_data,pair_list):
            entity1, entity2 = es
            relation = edge.split(sep[1])[0]
            # if entity1 not in relation or entity2 not in relation:
                # print(relation)
                # print(f'Error: fail to add edge {entity1}, {entity2}')
            pattern = r"分数:\s*\d+\.\d+"
            match = re.search(pattern, edge)
            weight = match.group() if match else None
            if weight:
                graph.add_edge(entity1,entity2,float(weight[4:]))
        return graph
        
    def create_entigraphs(self):
        # List all files and directories in the folder
        all_items = os.listdir(self.edge_weight_path)
        # Filter out directories, keep only files
        files = [f for f in all_items if os.path.isfile(os.path.join(self.edge_weight_path, f))]
        for f in files:
            path = os.path.join(self.edge_weight_path, f)
            graph = self.get_graph_by_file(path, self.lang)
            # graph.update_edge_weight_by_common_neighbor()
            self.graphs.append(graph)
            self.names.append(f)

def load_groups_from_file(group_path):
    group_res = []
    with open(group_path, 'r') as f:
        lines = f.readlines()
    prefix = 'Entities: '
    for line in lines:
        if (prefix in line):
            g = line[len(prefix)+1:-2].split(', ')
            g = [e[1:-1] for e in g]
            group_res.append(g)
    return group_res

def get_entity_groups(article_path, data_path, lang, threshold, num_per_group, k):
    """
    datapath: 'data/dataset/raw/judge_edge_entigraph_deepseek-chat'
    lang: zh en
    k: k neighbors
    """
    
    egs = EntiGraphs(data_path,lang)
    egs.create_entigraphs()
    # get article id
    article_name = article_path.split('/')[-1]
    for i,n in enumerate(egs.names):
        if article_name in n:
            article_id = i
            break
    egs.graphs[article_id].remove_edges_below_threshold(threshold)
    group_res = []
    neighbor_ks = egs.graphs[article_id].get_neighbor_combinations(2)
    group_res.append(neighbor_ks)
    for i in range(3, k+1):
        print(f"Number of {i}-tuple: {num_per_group}")
        neighbor_ks = egs.graphs[article_id].get_neighbor_combinations(i)
        indices = [i for i in range(len(neighbor_ks))]
        random.seed(0)
        if num_per_group > len(neighbor_ks):
            num_per_group = len(neighbor_ks)
            print(f"Number of tuples are not sufficient, change to #{num_per_group}...")

        indices = sorted(random.sample(indices, k=num_per_group))
        selected_neighbor_ks = [neighbor_ks[i] for i in indices]
        group_res.append(selected_neighbor_ks)
    return group_res

def generate_pairwise_entity_relation_strength(document_index: str, model_name: str, task_type: str, encryption: bool, output_path=None):
    random.seed(42)
    set_openai_key()
    if task_type == 'quality':
        task = QuALITY('cur')
    elif task_type == 'judge':
        task = Judge()
    print(len(task.documents))
    document = task.documents[document_index]
    
    print(f"Generating the entity relation strength for {document_index} article {document.uid}")
    if output_path is None:
        output_path = f'data/dataset/raw/{task_type}_weighted_edge_entigraph_{model_name}-v2/{k}/{document.uid}.json'
    else:
        output_path = f'{output_path}/{document.uid}.json'
    if os.path.exists(output_path):
        output = jload(output_path)
    else:
        print("The path does not exist.")
        return
    
    if task_type == 'quality':
        content = document.content
    elif task_type == 'judge':
        content = document.text
    
    if isinstance(output[0], list) and len(output[0])>0:
        entities = output[0]
        if encryption:
            pii_entities=document.get_pii_entities_by_decryption(entities)
            content, encrypted_entity = document.get_encrypted_content(['person','loc'],pii_entities=pii_entities)
    else:
        print("Error, no entities..")
    
    print('Generating Entity Strength...')
    pair_list = []
    # iterate over pairs of entities and generate relations
    for i in range(len(entities)):
        for j in range(i+1, len(entities)):
            pair = (entities[i], entities[j])
            pair_list.append(pair)
    print(f"len of pair list {len(pair_list)}")
    for entity1, entity2 in tqdm(pair_list):
        # if _pair_already_generated(entity1, entity2, output):
        #     continue
        response = generate_two_entity_relations(
            content, entity1, entity2,
            task.openai_system_generate_two_entity_connection_score,
            model_name)
        if response:
            output.append(response)
        jdump(output, output_path) # default encoding: UTF-8

def generate_synthetic_data_for_document(document_index: str, model_name: str, task_type: str, encryption: bool, k: int, num_sentence_per_group: int, continual: bool, output_path=None, score_data_path=None, lang='zh'):
    random.seed(42)
    set_openai_key()
    if task_type == 'quality':
        task = QuALITY('cur')
    elif task_type == 'judge':
        task = Judge()
    print(len(task.documents))
    document = task.documents[document_index]
    
    print(f"Generating synthetic data for {document_index} article {document.uid}")
    if output_path is None:
        output_path = f'data/dataset/raw/{task_type}_weighted_edge_entigraph_{model_name}-v2/{k}/{document.uid}.json'
    else:
        output_path = f'{output_path}/{document.uid}.json'
    
    if os.path.exists(output_path):
        output = jload(output_path)
    else:
        output = [[]]

    content = document.content

    # first check if entities are already generated
    if isinstance(output[0], list) and len(output[0])>0:
        entities = output[0]
        print(f"Load entities... {len(entities)}")
        if encryption:
            pii_entities=document.get_pii_entities_by_decryption(entities)
            content, encrypted_entity = document.get_encrypted_content(['person','loc'],pii_entities=pii_entities)
    else:
        print("Error, no entities..")
        return

    # get entity groups
    threshold = 0.5
    if score_data_path is None:
        score_data_path = 'data/dataset/raw/judge_edge_score_entigraph_deepseek-chat/encrypted'
    groups = get_entity_groups(output_path, score_data_path, lang, threshold, num_sentence_per_group, k)
    for g in groups:
        print(len(g))
    if continual:
        # load groups
        group_path = f"outputs/error_out/edge_{k}/output{document_index}.txt"
        groups = load_groups_from_file(group_path)
        count = 0 
        jdump(groups,f'group{document_index}.json')
        for entities in tqdm(groups):
            count = count+1
            response = generate_k_entity_relations(
                content, entities,
                task.openai_system_generate_k_entity_relations,
                model_name,lang=lang)
            if response:
                output.append(response)
            jdump(output, output_path) # default encoding: UTF-8
        print(f"Number of tuple is {count}...")
    else:
        groups = groups[1:]
    
        for gi in range(len(groups)):
            print(f"Generating {gi+3} of entities content...")
            count = 0 
            for entities in tqdm(groups[gi]):
                count = count+1
                response = generate_k_entity_relations(
                    content, entities,
                    task.openai_system_generate_k_entity_relations,
                    model_name,lang=lang)
                if response:
                    output.append(response)
                jdump(output, output_path) # default encoding: UTF-8
            print(f"Number of {gi+3} tuple is {count}...")

# ===================================
# keep total number of tuples around 22K
# ===================================
if __name__ == "__main__":
    model_name = "deepseek-chat"
    task_type = "judge"
    encryption = False
    lang = 'zh'
    document_index = int(sys.argv[1])
    task = int(sys.argv[2])# 1 - strength score; 2 - generation
    if (len(sys.argv)>3):
        k = int(sys.argv[3])
    num_list = [2000, 2000, 1000, 1000, 1000, 2000, 2500]
    score_path = "data/dataset/raw/judge_edge_score_entigraph_deepseek-chat/encrypted"
    output_path = f"data/dataset/raw/judge_weighted_encrypt_edge_entigraph_deepseek-chat/{k}"
    if task == 1:
        generate_pairwise_entity_relation_strength(document_index, model_name, task_type, encryption, output_path=score_path)
    elif task == 2:
        num_sentences_per_group = num_list[document_index] // (k-2)
        generate_synthetic_data_for_document(document_index, model_name, task_type, encryption, k, num_sentences_per_group,continual=False,
                                            output_path=output_path, score_data_path=score_path, lang=lang)