"""
Genetic algorithm to select sentences
"""
import numpy as np
import random


# Fitness function for Exact Selection of k sentences
def calculate_proportions(selected_sentences, sentences):
    proportion = np.sum(selected_sentences, 0) / np.sum(sentences)
    total_red = np.sum(selected_sentences * sentences[:, 0])
    total_black = np.sum(selected_sentences * sentences[:, 1])
    total_white = np.sum(selected_sentences * sentences[:, 2])
    total_balls = total_red + total_black + total_white
    proportions = np.array([total_red / total_balls, total_black / total_balls, total_white / total_balls])
    print(proportion,proportions)
    assert((proportion-proportions).sum()==0)
    return proportions

def fitness_exact_selection(solution, sentences, target_ratios, k):
    # Check how many sentences are selected
    num_selected = np.sum(solution)
    
    # Penalize solutions that don't select exactly `k` sentences
    penalty = abs(num_selected - k)
    
    # Calculate the proportions
    proportions = calculate_proportions(solution, sentences)
    
    # Calculate Mean Squared Error (MSE) between proportions and target ratios
    mse = np.mean((proportions - target_ratios) ** 2)
    
    # Combine MSE with the penalty
    return mse + penalty * 10  # Penalty weight can be adjusted

# Initialize population
def initialize_population(pop_size, num_sentences, k):
    population = []
    for _ in range(pop_size):
        solution = np.zeros(num_sentences)
        selected_indices = random.sample(range(num_sentences), k)
        solution[selected_indices] = 1
        population.append(solution)
    return np.array(population)

# Tournament selection
def tournament_selection(population, sentences, target_ratios, k, tournament_size=3):
    selected = random.sample(range(len(population)), tournament_size)
    fitness_values = [fitness_exact_selection(population[i], sentences, target_ratios, k) for i in selected]
    winner = selected[np.argmin(fitness_values)]
    return population[winner]

# Crossover (one-point crossover)
def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
    return child

# Mutation (randomly flip a sentence selection)
def mutate(child, mutation_rate=0.1):
    for i in range(len(child)):
        if random.random() < mutation_rate:
            child[i] = 1 - child[i]  # Flip the selection
    return child

# Genetic Algorithm with Exact Selection
def genetic_algorithm_exact_selection(sentences, target_ratios, k, pop_size=100, generations=500, mutation_rate=0.1):
    num_sentences = len(sentences)
    num_entities = sentences.shape[1]
    population = initialize_population(pop_size, num_sentences, k)
    print(len(population))
    for gen in range(generations):
        new_population = []
        
        # Selection, Crossover, and Mutation
        for _ in range(pop_size):
            parent1 = tournament_selection(population, sentences, target_ratios, k)
            parent2 = tournament_selection(population, sentences, target_ratios, k)
            child = crossover(parent1, parent2)
            child = mutate(child, mutation_rate)
            new_population.append(child)
        
        population = np.array(new_population)
        print(len(population))
        # Evaluate best solution
        best_solution = None
        best_fit_score = 1000
        cur_solution = min(population, key=lambda s: fitness_exact_selection(s, sentences, target_ratios, k))
        best_fitness = fitness_exact_selection(cur_solution, sentences, target_ratios, k)
        print(f"Generation {gen}, Best Fitness: {best_fitness}")
        if best_fitness < best_fit_score:
            best_fit_score = best_fitness
            best_solution = cur_solution
        # If solution is sufficiently close to the target, stop early
        if best_fitness < 1e-6:
            print("Converged!")
            break
    
    return best_solution

if __name__ == '__main__':
    # Target ratios among entities
    target_ratios = np.array([2/10, 3/10, 5/10])

    # Example Sentences: [Entity1, Entity2, Entity3]
    sentences = np.array([
        [4, 6, 10],  # Sentence 1: 4 E1, 6 E2, 10 E3
        [2, 4, 6],   # Sentence 2: 2 E1, 4 E2, 6 E3
        [6, 9, 15],  # Sentence 3: 6 E1, 9 E2, 15 E3
        [5, 3, 7],   # Sentence 4: 5 E1, 3 E2, 7 E3
        [1, 2, 4],   # Sentence 5: 1 E1, 2 E2, 4 E3
    ])

    # Run the Genetic Algorithm with Exact Selection of k Sentences
    k = 3  # Number of sentences to select
    best_solution = genetic_algorithm_exact_selection(sentences, target_ratios, k)

    # Output the best selected sentences
    selected_sentences = np.where(best_solution == 1)[0]
    print(f"Selected sentences: {selected_sentences}")