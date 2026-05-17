import re
import random
from collections import defaultdict
import itertools
import json 



# =============================================================================
# Set number of puzzles to generate, and the number of houses
# =============================================================================
num_puzzles = 10
n_of_houses = 4

to_nl = {'House Colors' : ['the person in the ', ' house'],
         'Nationalities': ['the ', ' person'],
         'Pets': ['the person with the ', ''],
         'Favorite Drink': ['the person whose favorite drink is ', ''],
         'Cigarette Brands': ['the person who smokes ',''],
         'Occupations': ['the ', ''],
         'Music Genre': ['the person whose favorite music genre is ', ''],
         'Favorite Food': ['the person whose favorite food is ', ''],
         'House Types': ['the person in the ', ''],
         'Clothing Item': ['the person who wears the ', ''],
         'Fictional Genre': ['the person whose favorite fictional genre is ', ''],
         'Instrument': ['the person who plays the ', ''], # 12
         'Sport': ['the person who competes in ', ''],
         'Lucky Number': ['the person whose lucky number is ', ''],
         'Fantasy Creature': ['the person whose favorite fantasy creature is ', ''],
         'Travel Destination': ['the person whose travel destination is ', '']
         }

zebra_puzzle_data = {
    "House Colors": [
        "Red", "Green", "Blue", "Yellow", "White", "Black", "Purple", "Orange", "Pink", "Grey",
        "Brown", "Beige", "Teal", "Cyan", "Navy", "Maroon", "Gold", "Silver", "Lime", "Turquoise"
    ],
    "Nationalities": [
        "American", "British", "Canadian", "French", "German", "Italian", "Spanish", "Russian",
        "Japanese", "Chinese", "Indian", "Brazilian", "Mexican", "Australian", "Swedish", "Dutch",
        "South African", "Norwegian", "Irish", "Egyptian"
    ],
    "Pets": [
        "Dog", "Cat", "Fish", "Bird", "Horse", "Rabbit", "Hamster", "Snake", "Turtle", "Lizard",
        "Ferret", "Parrot", "Guinea pig", "Frog", "Goat", "Pig", "Monkey", "Chinchilla", "Hedgehog", "Peacock"
    ],
    "Favorite Drink": [
        "Tea", "Coffee", "Milk", "Water", "Orange juice", "Soda", "Lemonade", "Beer", "Wine", "Smoothie",
        "Cola", "Apple juice", "Energy drink", "Hot chocolate", "Iced tea", "Sparkling water",
        "Cranberry juice", "Coconut water", "Kombucha", "Grape juice"
    ],
    "Cigarette Brands": [
        "Pall Mall", "Dunhill", "Blend", "Blue Master", "Prince", "Camel", "Marlboro", "Lucky Strike",
        "Winston", "Chesterfield", "Newport", "Parliament", "L&M", "Kool", "Rothmans", "Benson & Hedges",
        "Davidoff", "Salem", "Gauloises", "Viceroy"
    ],
    "Occupations": [
        "Teacher", "Doctor", "Engineer", "Artist", "Musician", "Chef", "Farmer", "Mechanic", "Scientist",
        "Policeman", "Writer", "Pilot", "Lawyer", "Astronaut", "Architect", "Plumber", "Librarian",
        "Actor", "Firefighter", "Magician"
    ],
    "Music Genre": [
        "Rock", "Jazz", "Classical", "Pop", "Hip Hop", "EDM", "Reggae", "Country", "Blues", "Metal",
        "R&B", "Folk", "Punk", "Funk", "Opera", "Indie", "Gospel", "Ska", "Techno", "Soul"
    ],
    "Favorite Food": [
        "Pizza", "Sushi", "Pasta", "Burger", "Salad", "Tacos", "Steak", "Ramen", "Dumplings", "Fried rice",
        "Pancakes", "Sandwich", "Lasagna", "Burrito", "Kebab", "Falafel", "Roast chicken", "Noodles",
        "BBQ ribs", "Curry"
    ],
    "House Types": [
        "Bungalow", "Villa", "Apartment", "Cabin", "Cottage", "Duplex", "Mansion", "Farmhouse", "Studio",
        "Loft", "Townhouse", "Treehouse", "Igloo", "Mobile home", "Tent", "Chalet", "Castle", "Houseboat",
        "Yurt", "Skyscraper"
    ],
    "Clothing Item": [
        "Hat", "Jacket", "Scarf", "Boots", "Glasses", "Watch", "Tie", "Gloves", "Belt", "Hoodie",
        "Dress", "Coat", "Sneakers", "Vest", "T-shirt", "Jeans", "Shorts", "Blazer", "Skirt", "Sandals"
    ],
    "Fictional Genre": [
        "Fantasy", "Sci-Fi", "Mystery", "Thriller", "Romance", "Horror", "Drama", "Comedy", "Adventure", "Historical fiction",
        "Dystopian", "Fairy tale", "Urban fantasy", "Magical realism", "Cyberpunk", "Steampunk", "Supernatural",
        "Crime", "Satire", "War"
    ],
    "Instrument": [
        "Guitar", "Piano", "Violin", "Drums", "Flute", "Saxophone", "Trumpet", "Cello",
        "Clarinet", "Harp", "Banjo", "Ukulele", "Accordion", "Bass guitar", "Oboe",
        "Trombone", "Tuba", "Mandolin", "Harmonica", "Xylophone"
    ],
    "Sport": [
        "Soccer", "Basketball", "Baseball", "Tennis", "Golf", "Volleyball", "Cricket",
        "Hockey", "Table tennis", "Swimming", "Boxing", "Wrestling", "Rugby", "Badminton",
        "Archery", "Fencing", "Skateboarding", "Surfing", "Gymnastics", "Track and field"
    ],
    "Lucky Number": [
        '1', '3', '5', '7', '8', '9', '11', '13', '17', '18', '21', '23', '27', '28', '33', '36', '42', '49', '64', '77'
    ],
    "Fantasy Creature": [
        "Dragon", "Unicorn", "Phoenix", "Mermaid", "Griffin", "Elf", "Dwarf", "Troll", "Goblin", "Vampire",
        "Werewolf", "Centaur", "Fairy", "Pegasus", "Gnome", "Giant", "Witch", "Zombie", "Ghost", "Chimera"
    ],
    "Travel Destination": [
        "Paris", "Tokyo", "New York", "Rome", "London", "Sydney", "Dubai", "Bangkok", "Cape Town", "Rio de Janeiro",
        "Cairo", "Moscow", "Athens", "Toronto", "Beijing", "Los Angeles", "Prague", "Bali", "Amsterdam", "Istanbul"
    ]
}


idx2cat = {1: 'House Colors',
 2: 'Nationalities',
 3: 'Pets',
 4: 'Favorite Drink',
 5: 'Cigarette Brands',
 6: 'Occupations',
 7: 'Music Genre',
 8: 'Favorite Food',
 9: 'House Types',
 10: 'Clothing Item',
 11: 'Fictional Genre',
 12: 'Instrument',
 13: 'Sport',
 14: 'Lucky Number',
 15: 'Fantasy Creature',
 16: 'Travel Destination',
 }

li = list(idx2cat.items())
random.shuffle(li)
idx2cat = dict(li)

import time
import subprocess

def shuffleZebraDict(zebraDict, idx2cat):
    
    shuffled_values = list(idx2cat.values())
    random.shuffle(shuffled_values)

    for key, new_value in zip(idx2cat.keys(), shuffled_values):
        idx2cat[key] = new_value
    
    for key, value_list in zebraDict.items():
        random.shuffle(value_list)
    return

def remove_random_elements_from_list_(input_list, num_elements_to_remove):

  if not isinstance(input_list, list):
    return "Error: Input must be a list."
  if not isinstance(num_elements_to_remove, int):
    return "Error: Number of elements to remove must be an integer."
  if num_elements_to_remove < 0:
    return "Error: Number of elements to remove cannot be negative."

  list_length = len(input_list)

  if num_elements_to_remove == 0:
    return input_list[:]  # Return a copy of the original list

  if num_elements_to_remove >= list_length:
    return [], input_list[:]  # All elements are removed, return an empty list

  # Create a copy of the list to work with, preserving the original
  list_copy = input_list[:]
  
  # Select indices to remove
  # random.sample ensures that each index is chosen at most once
  indices_to_remove = sorted(random.sample(range(list_length), num_elements_to_remove), reverse=True)
  
  elements_to_remove = [input_list[i] for i in indices_to_remove]
  # Remove elements at the selected indices
  # Iterating in reverse order of indices prevents issues with changing list size
  for index in indices_to_remove:
    list_copy.pop(index)
    
  return list_copy, elements_to_remove


def remove_random_elements_with_min_per_type(
    input_list,
    type_list,
    num_elements_to_remove,
    min_elements_per_type
):
    
    indices = random.sample(range(len(input_list)), len(input_list))  # Get a shuffled list of indices

    input_list = [input_list[i] for i in indices]  
    type_list = [type_list[i] for i in indices]  
    
    # 1. Input Validations
    if not isinstance(input_list, list):
        return "Error: input_list must be a list."
    if not isinstance(type_list, list):
        return "Error: type_list must be a list."
    if len(input_list) != len(type_list):
        return "Error: input_list and type_list must have the same length."
    if not isinstance(num_elements_to_remove, int):
        return "Error: num_elements_to_remove must be an integer."
    if num_elements_to_remove < 0:
        return "Error: num_elements_to_remove cannot be negative."
    if not isinstance(min_elements_per_type, int):
        return "Error: min_elements_per_type must be an integer."
    if min_elements_per_type < 0:
        return "Error: min_elements_per_type cannot be negative."

    list_length = len(input_list)
    if list_length == 0:
        return [], [] # Consistent with original for empty input

    # Handle num_elements_to_remove == 0 (similar to original)
    if num_elements_to_remove == 0:
        return input_list[:], [] # Return a copy of the original list and empty removed list

    # 2. Determine must_keep_indices: indices of elements that must not be removed
    #    to satisfy min_elements_per_type for each type.
    must_keep_indices = set()
    indices_by_type = defaultdict(list)
    for i, current_type in enumerate(type_list):
        indices_by_type[current_type].append(i)

    for current_type, all_indices_of_type in indices_by_type.items():
        # all_indices_of_type are already sorted by original position due to enumerate
        count_of_type = len(all_indices_of_type)
        # Determine how many elements of this type must be guaranteed to remain.
        # It's the minimum of how many exist and the required minimum.
        num_to_guarantee_for_type = min(count_of_type, min_elements_per_type)
        
        # The first num_to_guarantee_for_type elements of this type (by original order) are kept
        must_keep_indices.update(all_indices_of_type[:num_to_guarantee_for_type])

    # 3. Identify potential_removable_indices: indices of elements that are candidates for removal.
    #    These are all indices NOT in must_keep_indices.
    all_original_indices = set(range(list_length))
    # Convert to list for random.sample
    potential_removable_indices = list(all_original_indices - must_keep_indices)

    # 4. Determine num_actually_to_remove:
    #    We want to remove num_elements_to_remove, but capped by how many are actually available for removal.
    num_actually_to_remove = min(num_elements_to_remove, len(potential_removable_indices))

    # 5. Select indices_to_be_removed:
    #    Randomly sample from the potential_removable_indices.
    #    random.sample chooses unique elements without replacement.
    indices_to_be_removed_set = set(random.sample(potential_removable_indices, num_actually_to_remove))

    # 6. Construct the final_kept_list and elements_removed_output list
    final_kept_list = []
    final_types_list = []
    # For elements_removed_output, to be consistent with the style of the original function's
    # internal processing (where indices to remove were sorted in reverse),
    # we sort our `indices_to_be_removed_set` in descending order of index.
    sorted_indices_actually_removed_desc = sorted(list(indices_to_be_removed_set), reverse=True)
    elements_removed_output = [input_list[i] for i in sorted_indices_actually_removed_desc]
    types_removed_output = [type_list[i] for i in sorted_indices_actually_removed_desc]

    # Construct the final_kept_list by iterating through the original list indices
    # and including elements whose indices were not chosen for removal.
    # This preserves the relative order of kept elements.
    for i in range(list_length):
        if i not in indices_to_be_removed_set:
            final_kept_list.append(input_list[i])
            final_types_list.append(type_list[i])
            
    return final_kept_list, final_types_list, elements_removed_output, types_removed_output

def run_clingo_external(program_str, num_models=1, timeout = 60):
    try:
        # Run Clingo with input from stdin (-), return num_models models
        result = subprocess.run(
            ["clingo", "-", str(num_models), '--opt-mode=optN', '-t 12'],
            input=program_str.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout = timeout
        )
        return result.stdout.decode("utf-8"), result.stderr.decode("unicode_escape"), result.returncode
    except subprocess.TimeoutExpired as exc:
        print(exc)
        return f"TIMEOUT: exceeded {timeout} seconds.", '', ''

import itertools

def generate_asp_clues_from_assignment(assignment):
    """
    Generates ASP clue rules based on a given assignment and returns them as a list.

    Args:
        assignment (list of list of int): Represents items for each category for each house.
                                          assignment[cat_idx][house_idx] = item_value
    Returns:
        list of str: A list of strings, where each string is an ASP comment or rule.
                     Returns None if the input assignment is invalid.
    """
    asp_rules = []
    rule_types = []
    if not assignment or not isinstance(assignment, list) or \
       not assignment[0] or not isinstance(assignment[0], list):
        print("% Error: Assignment must be a non-empty list of lists.")
        return None # Indicate error

    num_categories = len(assignment)
    num_houses = len(assignment[0])

    if not all(len(row) == num_houses for row in assignment):
        print("% Error: All categories must have the same number of house assignments.")
        return None # Indicate error

    #asp_rules.append(f"% Automatically generated ASP clues for an assignment with {num_categories} categories and {num_houses} houses.")
    #asp_rules.append("% The predicate 'has_attribute(House, Category, Item)' is assumed.")

    all_attribute_instances = []
    for c_idx in range(num_categories):
        for h_idx in range(num_houses):
            item_val = assignment[c_idx][h_idx]
            all_attribute_instances.append({
                "cat_py": c_idx,
                "item_py": item_val,
                "house_py": h_idx,
                "cat_asp": c_idx + 1,
                "item_asp": item_val + 1,
                "house_asp": h_idx + 1
            })

    # --- 1. FOUNDAT Clues ---
    # Description: Item ITEM_A (of category CAT_A) is in House HOUSE_X.
    # NEW ASP Template: :- not has_attribute(H_var, %%CAT_A%%, %%ITEM_A%%), H_var = %%HOUSE_X%%.
    #asp_rules.append("\n% --- FOUNDAT Clues ---")
    for attr_inst in all_attribute_instances:
        cat_a = attr_inst['cat_asp']
        item_a = attr_inst['item_asp']
        house_x = attr_inst['house_asp'] # This is the specific house for the item
        
        clue_desc = f"Item {item_a} (of Cat {cat_a}) is in House {house_x}"
        # Updated rule line according to the new template:
        rule = f":- not has_attribute(H_var, {cat_a}, {item_a}), H_var = {house_x}."
        #asp_rules.append(f"% Clue: {clue_desc}")
        asp_rules.append(rule)
        rule_types.append('foundAt')
    # --- 2. SAMEHOUSE Clues (Symmetric) ---
    # ASP Template: :- has_attribute(H1, %%CAT_A%%, %%ITEM_A%%), has_attribute(H2, %%CAT_B%%, %%ITEM_B%%), H1 != H2.
    #asp_rules.append("\n% --- SAMEHOUSE Clues ---")
    for attr_a, attr_b in itertools.combinations(all_attribute_instances, 2):
        if attr_a['cat_py'] == attr_b['cat_py'] and attr_a['item_py'] == attr_b['item_py']:
            continue
        if attr_a["house_py"] == attr_b["house_py"]:
            clue_desc = (f"Item {attr_a['item_asp']} (Cat {attr_a['cat_asp']}) and "
                         f"Item {attr_b['item_asp']} (Cat {attr_b['cat_asp']}) "
                         f"are in the same house (House {attr_a['house_asp']})")
            rule = (f":- has_attribute(H1, {attr_a['cat_asp']}, {attr_a['item_asp']}), "
                    f"has_attribute(H2, {attr_b['cat_asp']}, {attr_b['item_asp']}), H1 != H2.")
            #asp_rules.append(f"% Clue: {clue_desc}")
            asp_rules.append(rule)
            rule_types.append('sameHouse')

    # --- 3. NOTAT Clues (Symmetric) ---
    # ASP Template: :- has_attribute(H, %%CAT_A%%, %%ITEM_A%%), has_attribute(H, %%CAT_B%%, %%ITEM_B%%).
    #asp_rules.append("\n% --- NOTAT (Not At Same House) Clues ---")
    for attr_a, attr_b in itertools.combinations(all_attribute_instances, 2):
        if attr_a['cat_py'] == attr_b['cat_py'] and attr_a['item_py'] == attr_b['item_py']:
            continue
        if attr_a["house_py"] != attr_b["house_py"]:
            clue_desc = (f"Item {attr_a['item_asp']} (Cat {attr_a['cat_asp']}) (in H{attr_a['house_asp']}) and "
                         f"Item {attr_b['item_asp']} (Cat {attr_b['cat_asp']}) (in H{attr_b['house_asp']}) "
                         f"are NOT in the same house.")
            rule = (f":- has_attribute(H, {attr_a['cat_asp']}, {attr_a['item_asp']}), "
                    f"has_attribute(H, {attr_b['cat_asp']}, {attr_b['item_asp']}).")
            #asp_rules.append(f"% Clue: {clue_desc}")
            asp_rules.append(rule)
            rule_types.append('notAt')
    # --- 4. DIRECTLEFT/RIGHT Clues (Asymmetric) ---
    # DIRECTLEFT Template: :- has_attribute(HA, %%CAT_A%%, %%ITEM_A%%), has_attribute(HB, %%CAT_B%%, %%ITEM_B%%), HA != HB - 1.
    # DIRECTRIGHT Template: :- has_attribute(HA, %%CAT_A%%, %%ITEM_A%%), has_attribute(HB, %%CAT_B%%, %%ITEM_B%%), HA != HB + 1.
    #asp_rules.append("\n% --- DIRECTLEFT/RIGHT Clues ---")
    for attr_a, attr_b in itertools.permutations(all_attribute_instances, 2):
        if attr_a['cat_py'] == attr_b['cat_py'] and attr_a['item_py'] == attr_b['item_py']:
            continue
        if attr_a["house_py"] == attr_b["house_py"] - 1: # A is left of B
            clue_desc = (f"House with Item {attr_a['item_asp']} (Cat {attr_a['cat_asp']}) (H{attr_a['house_asp']}) "
                         f"is directly left of house with Item {attr_b['item_asp']} (Cat {attr_b['cat_asp']}) (H{attr_b['house_asp']}).")
            rule = (f":- has_attribute(HA, {attr_a['cat_asp']}, {attr_a['item_asp']}), "
                    f"has_attribute(HB, {attr_b['cat_asp']}, {attr_b['item_asp']}), HA != HB - 1.")
            #asp_rules.append(f"% Clue: {clue_desc}")
            asp_rules.append(rule)
            rule_types.append('directlr')
        if attr_a["house_py"] == attr_b["house_py"] + 1: # A is right of B
            clue_desc = (f"House with Item {attr_a['item_asp']} (Cat {attr_a['cat_asp']}) (H{attr_a['house_asp']}) "
                         f"is directly right of house with Item {attr_b['item_asp']} (Cat {attr_b['cat_asp']}) (H{attr_b['house_asp']}).")
            rule = (f":- has_attribute(HA, {attr_a['cat_asp']}, {attr_a['item_asp']}), "
                    f"has_attribute(HB, {attr_b['cat_asp']}, {attr_b['item_asp']}), HA != HB + 1.")
            #asp_rules.append(f"% Clue: {clue_desc}")
            asp_rules.append(rule)
            rule_types.append('directlr')

    # --- 5. SIDEBYSIDE Clues (Symmetric) ---
    # ASP Template: :- has_attribute(HA, %%CAT_A%%, %%ITEM_A%%), has_attribute(HB, %%CAT_B%%, %%ITEM_B%%), HA != HB - 1, HA != HB + 1.
    #asp_rules.append("\n% --- SIDEBYSIDE Clues ---")
    for attr_a, attr_b in itertools.combinations(all_attribute_instances, 2):
        if attr_a['cat_py'] == attr_b['cat_py'] and attr_a['item_py'] == attr_b['item_py']:
            continue
        if abs(attr_a["house_py"] - attr_b["house_py"]) == 1:
            clue_desc = (f"Houses of Item {attr_a['item_asp']} (Cat {attr_a['cat_asp']}) (H{attr_a['house_asp']}) and "
                         f"Item {attr_b['item_asp']} (Cat {attr_b['cat_asp']}) (H{attr_b['house_asp']}) are side-by-side.")
            rule = (f":- has_attribute(HA, {attr_a['cat_asp']}, {attr_a['item_asp']}), "
                    f"has_attribute(HB, {attr_b['cat_asp']}, {attr_b['item_asp']}), "
                    f"HA != HB - 1, HA != HB + 1.")
            #asp_rules.append(f"% Clue: {clue_desc}")
            asp_rules.append(rule)
            rule_types.append('sideBySide')

    # --- 6. LEFT/RIGHTOF (Somewhere) Clues (Asymmetric) ---
    # LEFT OF Template: :- has_attribute(HA, %%CAT_A%%, %%ITEM_A%%), has_attribute(HB, %%CAT_B%%, %%ITEM_B%%), HA >= HB.
    # RIGHT OF Template: :- has_attribute(HA, %%CAT_A%%, %%ITEM_A%%), has_attribute(HB, %%CAT_B%%, %%ITEM_B%%), HA <= HB.
    #asp_rules.append("\n% --- LEFT/RIGHTOF (Somewhere) Clues ---")
    for attr_a, attr_b in itertools.permutations(all_attribute_instances, 2):
        if attr_a['cat_py'] == attr_b['cat_py'] and attr_a['item_py'] == attr_b['item_py']:
            continue
        if attr_a["house_py"] < attr_b["house_py"]: # A is left of B
            clue_desc = (f"House with Item {attr_a['item_asp']} (Cat {attr_a['cat_asp']}) (H{attr_a['house_asp']}) "
                         f"is somewhere left of house with Item {attr_b['item_asp']} (Cat {attr_b['cat_asp']}) (H{attr_b['house_asp']}).")
            rule = (f":- has_attribute(HA, {attr_a['cat_asp']}, {attr_a['item_asp']}), "
                    f"has_attribute(HB, {attr_b['cat_asp']}, {attr_b['item_asp']}), HA >= HB.")
            #asp_rules.append(f"% Clue: {clue_desc}")
            asp_rules.append(rule)
            rule_types.append('lrOf')
        if attr_a["house_py"] > attr_b["house_py"]: # A is right of B
            clue_desc = (f"House with Item {attr_a['item_asp']} (Cat {attr_a['cat_asp']}) (H{attr_a['house_asp']}) "
                         f"is somewhere right of house with Item {attr_b['item_asp']} (Cat {attr_b['cat_asp']}) (H{attr_b['house_asp']}).")
            rule = (f":- has_attribute(HA, {attr_a['cat_asp']}, {attr_a['item_asp']}), "
                    f"has_attribute(HB, {attr_b['cat_asp']}, {attr_b['item_asp']}), HA <= HB.")
            #asp_rules.append(f"% Clue: {clue_desc}")
            asp_rules.append(rule)
            rule_types.append('lrOf')

    # --- 7. N_BETWEEN Clues (Symmetric) ---
    # ONE HOUSE BETWEEN Template: :- has_attribute(HA, %%CAT_A%%, %%ITEM_A%%), has_attribute(HB, %%CAT_B%%, %%ITEM_B%%), HA != HB - 2, HA != HB + 2.
    #asp_rules.append("\n% --- ONE HOUSE BETWEEN Clues ---")
    for attr_a, attr_b in itertools.combinations(all_attribute_instances, 2):
        if attr_a['cat_py'] == attr_b['cat_py'] and attr_a['item_py'] == attr_b['item_py']:
            continue
        if abs(attr_a["house_py"] - attr_b["house_py"]) == 2: # One house between
            clue_desc = (f"One house between Item {attr_a['item_asp']} (Cat {attr_a['cat_asp']}) (H{attr_a['house_asp']}) and "
                         f"Item {attr_b['item_asp']} (Cat {attr_b['cat_asp']}) (H{attr_b['house_asp']}).")
            rule = (f":- has_attribute(HA, {attr_a['cat_asp']}, {attr_a['item_asp']}), "
                    f"has_attribute(HB, {attr_b['cat_asp']}, {attr_b['item_asp']}), "
                    f"HA != HB - 2, HA != HB + 2.")
            #asp_rules.append(f"% Clue: {clue_desc}")
            asp_rules.append(rule)
            rule_types.append('1_between')

    # TWO HOUSES BETWEEN Template: :- has_attribute(HA, %%CAT_A%%, %%ITEM_A%%), has_attribute(HB, %%CAT_B%%, %%ITEM_B%%), HA != HB - 3, HA != HB + 3.
    #asp_rules.append("\n% --- TWO HOUSES BETWEEN Clues ---")
    for attr_a, attr_b in itertools.combinations(all_attribute_instances, 2):
        if attr_a['cat_py'] == attr_b['cat_py'] and attr_a['item_py'] == attr_b['item_py']:
            continue
        if abs(attr_a["house_py"] - attr_b["house_py"]) == 3: # Two houses between
            clue_desc = (f"Two houses between Item {attr_a['item_asp']} (Cat {attr_a['cat_asp']}) (H{attr_a['house_asp']}) and "
                         f"Item {attr_b['item_asp']} (Cat {attr_b['cat_asp']}) (H{attr_b['house_asp']}).")
            rule = (f":- has_attribute(HA, {attr_a['cat_asp']}, {attr_a['item_asp']}), "
                    f"has_attribute(HB, {attr_b['cat_asp']}, {attr_b['item_asp']}), "
                    f"HA != HB - 3, HA != HB + 3.")
            #asp_rules.append(f"% Clue: {clue_desc}")
            asp_rules.append(rule)
            rule_types.append('2_between')
            
    return asp_rules, rule_types

def extract_has_attribute_args(line_str):
    pattern = re.compile(r"has_attribute\(([^)]+)\)")
    all_extracted_args = []
    for match in pattern.finditer(line_str):
        args_string = match.group(1)
        current_call_args = [arg.strip() for arg in args_string.split(',')]
        all_extracted_args.append(current_call_args)
        
    return all_extracted_args

rule_type_names = ['foundAt',
 'sameHouse',
 'notAt',
 'directlr',
 'sideBySide',
 'lrOf',
 '1_between',
 '2_between']


min_to_keep_per_size = {3: 1,
                        4: 1,
                        5: 2,
                        6: 4,
                        7: 2,
                        8: 10,
                        9: 5,
                        10: 15,
                        11: 18,
                        12: 5,
                        14: 10,
                        16: 20}


data_list = []

for i in range(num_puzzles):

    shuffleZebraDict(zebra_puzzle_data, idx2cat)
    program_basic = '''% --- Configuration ---
    % Define the number of houses (and items per category for unique assignment)
    #const n_houses = <N_OF_HOUSES>. % Change this value to scale the problem (e.g., 3, 4, 6)
    
    % Define the basic entities in the problem.
    
    % Houses are numbered from 1 to n_houses.
    house(1..n_houses). % Generates house(1), ..., house(n_houses).
    
    % --- Generic Category and Item Definitions ---
    % Syntax: category(category_name).
    %         item(numeric_identifier, category_name).
    
    
    category(1..n_houses).
    item(1..n_houses).
    
    item(C,I) :- category(C), item(I).
    
    
    1 { has_attribute(H, C, I) : item(I, C) } 1 :- house(H), category(C).
    1 { has_attribute(H, C, I) : house(H) } 1 :- item(I, C), category(C).'''.replace('<N_OF_HOUSES>',str(n_of_houses))
    
    start_time = time.time()
    
    
    n_of_categories = n_of_houses
    category_assignments = []
    for cat in range(n_of_categories):
        assignment = [i for i in range(n_of_categories)]
        random.shuffle(assignment)
        category_assignments.append(assignment)
    
    # generate solution string
    categories_solution = {i+1: [] for i in range(n_of_houses)}
    for cat_idx,category in enumerate(category_assignments):
        for house_idx,house_num in enumerate(category):
            categories_solution[house_idx+1].append(category_assignments[cat_idx][house_idx])
    
    solution_lines = []
    for key,items in categories_solution.items():
        solution_line = f'House {key}: ' + ', '.join([zebra_puzzle_data[idx2cat[i+1]][item] for i, item in enumerate(items)])
        solution_lines.append(solution_line)
    
    
    
    clingo_calls = 0
    max_tries = 6
    tries = 0
    generated_rules, rule_types = generate_asp_clues_from_assignment(category_assignments)
    rule_type_counts = {rule_type_name: rule_types.count(rule_type_name) for rule_type_name in rule_type_names}
    rule_type_probabilities = {rule_type_name: 1/(rule_type_counts[rule_type_name]*len(rule_type_names)) for rule_type_name in rule_type_names}
    
    
    candidate_rules = generated_rules[:]
    candidate_rule_types = rule_types[:]
    n_to_cut = len(candidate_rules) //2
    while n_to_cut>1:
        
        
        candidate_remaining, candidate_remaining_rule_types, candidate_removed, candidate_type_removed = remove_random_elements_with_min_per_type(candidate_rules, candidate_rule_types, n_to_cut, min_to_keep_per_size[n_of_houses])
        
        candidate_rule_type_counts = {rule_type_name: candidate_remaining_rule_types.count(rule_type_name) for rule_type_name in rule_type_names}
        if len(candidate_removed)==0:
            break
        
        # solve
        program = program_basic + '\n\n\n\n' + '\n'.join(candidate_remaining)
        stdout, stderr, _ = run_clingo_external(program, 2)
        clingo_calls+=1
        if 'Answer: 2' in stdout:
            unique = False
        else:
            if 'Answer: 1' in stdout and 'SATISFIABLE' in stdout:
                unique = True
            else:
                breakpoint()
        if unique:
            candidate_rules= candidate_remaining
            candidate_rule_types = candidate_remaining_rule_types
            if n_to_cut >= (0.9)*len(candidate_rules):
                n_to_cut//=2
            tries = 0
        elif tries < max_tries-1:
            tries+=1
            continue # resample rules to remove
        else:
            n_to_cut = n_to_cut //2 # the number to cut is halfed
            tries = 0
            
    rules_to_check = candidate_rules[:]
    rules_to_check_type = candidate_rule_types[:]
    for rule,rule_type in zip(rules_to_check, rules_to_check_type):
        
        
        rule_type_counts = {rule_type_name: candidate_rule_types.count(rule_type_name) for rule_type_name in rule_type_names}
        
        idx_to_remove = candidate_rules.index(rule)
        del candidate_rules[idx_to_remove]
        del candidate_rule_types[idx_to_remove]
    
        program = program_basic + '\n\n\n\n' + '\n'.join(candidate_rules)
        stdout, stderr, _ = run_clingo_external(program, 2)
        clingo_calls+=1
        if 'Answer: 2' in stdout:
            unique = False
        else:
            if 'Answer: 1' in stdout and 'SATISFIABLE' in stdout:
                unique = True
            else:
                breakpoint()
    
        if unique: #don't add rule back
            continue
        else: # add rule back
            candidate_rules.append(rule)
            candidate_rule_types.append(rule_type)
    
    program = program_basic + '\n\n\n\n' + '\n'.join(candidate_rules)
    end_time = time.time()
    print(f'Total time to generate puzzle: {end_time-start_time}')
    print(f'{clingo_calls} clingo calls used to create puzzle.')
    print(f'# of clues: {len(candidate_rule_types)}')
    print(rule_type_counts)
    clues = []

    for rule,rule_type in zip(candidate_rules, candidate_rule_types):
        
        if rule_type == '1_between': # 1 between
            a1, a2 = extract_has_attribute_args(rule)
            
            cat_a1 = idx2cat[int(a1[1])]
            cat_a2 = idx2cat[int(a2[1])]
            
            choice_a1 = zebra_puzzle_data[cat_a1][int(a1[2])-1]
            choice_a2 = zebra_puzzle_data[cat_a2][int(a2[2])-1]
            
            sentence = 'There is one house in between ' + to_nl[cat_a1][0] + choice_a1.lower() + (to_nl[cat_a1][1] if to_nl[cat_a1][0] else '') + ' and ' + to_nl[cat_a2][0] + choice_a2.lower() + to_nl[cat_a2][1] + '.'
        elif rule_type == '2_between': # 1 between
            a1, a2 = extract_has_attribute_args(rule)
            
            cat_a1 = idx2cat[int(a1[1])]
            cat_a2 = idx2cat[int(a2[1])]
            
            choice_a1 = zebra_puzzle_data[cat_a1][int(a1[2])-1]
            choice_a2 = zebra_puzzle_data[cat_a2][int(a2[2])-1]
            
            sentence = 'There are two houses in between ' + to_nl[cat_a1][0] + choice_a1.lower() + (to_nl[cat_a1][1] if to_nl[cat_a1][0] else '') + ' and ' + to_nl[cat_a2][0] + choice_a2.lower() + to_nl[cat_a2][1] + '.'
        elif rule_type == 'lrOf' and '>=' in rule: # lrOf two cases
            a1, a2 = extract_has_attribute_args(rule)
            
            cat_a1 = idx2cat[int(a1[1])]
            cat_a2 = idx2cat[int(a2[1])]
            
            choice_a1 = zebra_puzzle_data[cat_a1][int(a1[2])-1]
            choice_a2 = zebra_puzzle_data[cat_a2][int(a2[2])-1]
            
            sentence = to_nl[cat_a1][0] + choice_a1.lower() + (to_nl[cat_a1][1] if to_nl[cat_a1][0] else '') + ' is somewhere to the left of ' + to_nl[cat_a2][0] + choice_a2.lower() + to_nl[cat_a2][1] + '.'
        elif rule_type == 'lrOf' and '<=' in rule: # lrOf two cases
            a1, a2 = extract_has_attribute_args(rule)
            
            cat_a1 = idx2cat[int(a1[1])]
            cat_a2 = idx2cat[int(a2[1])]
            
            choice_a1 = zebra_puzzle_data[cat_a1][int(a1[2])-1]
            choice_a2 = zebra_puzzle_data[cat_a2][int(a2[2])-1]
            
            sentence = to_nl[cat_a1][0] + choice_a1.lower() + (to_nl[cat_a1][1] if to_nl[cat_a1][0] else '') + ' is somewhere to the right of ' + to_nl[cat_a2][0] + choice_a2.lower() + to_nl[cat_a2][1] + '.'
        elif rule_type == 'directlr' and '- 1.' in rule: # directlr two cases
            a1, a2 = extract_has_attribute_args(rule)
            
            cat_a1 = idx2cat[int(a1[1])]
            cat_a2 = idx2cat[int(a2[1])]
            
            choice_a1 = zebra_puzzle_data[cat_a1][int(a1[2])-1]
            choice_a2 = zebra_puzzle_data[cat_a2][int(a2[2])-1]
            
            sentence = to_nl[cat_a1][0] + choice_a1.lower() + (to_nl[cat_a1][1] if to_nl[cat_a1][0] else '') + ' is directly to left of ' + to_nl[cat_a2][0] + choice_a2.lower() + to_nl[cat_a2][1] + '.'
        elif rule_type == 'directlr' and '+ 1.' in rule: # directlr two cases
            a1, a2 = extract_has_attribute_args(rule)
            
            cat_a1 = idx2cat[int(a1[1])]
            cat_a2 = idx2cat[int(a2[1])]
            
            choice_a1 = zebra_puzzle_data[cat_a1][int(a1[2])-1]
            choice_a2 = zebra_puzzle_data[cat_a2][int(a2[2])-1]
            
            sentence = to_nl[cat_a1][0] + choice_a1.lower() + (to_nl[cat_a1][1] if to_nl[cat_a1][0] else '') + ' is directly to right of ' + to_nl[cat_a2][0] + choice_a2.lower() + to_nl[cat_a2][1] + '.'
        elif rule_type == 'foundAt': # lrOf two cases
            a1 = extract_has_attribute_args(rule)[0]
            house_num = rule.split('=')[-1].replace('.','').strip()
            cat_a1 = idx2cat[int(a1[1])]
            
            choice_a1 = zebra_puzzle_data[cat_a1][int(a1[2])-1]
            
            sentence = to_nl[cat_a1][0] + choice_a1.lower() + (to_nl[cat_a1][1] if to_nl[cat_a1][0] else '') + ' is in house number ' + house_num + '.'
        elif rule_type == 'sideBySide': # directlr two cases
            a1, a2 = extract_has_attribute_args(rule)
            
            cat_a1 = idx2cat[int(a1[1])]
            cat_a2 = idx2cat[int(a2[1])]
            
            choice_a1 = zebra_puzzle_data[cat_a1][int(a1[2])-1]
            choice_a2 = zebra_puzzle_data[cat_a2][int(a2[2])-1]
            
            sentence = to_nl[cat_a1][0] + choice_a1.lower() + (to_nl[cat_a1][1] if to_nl[cat_a1][0] else '') + ' is adjacent to ' + to_nl[cat_a2][0] + choice_a2.lower() + to_nl[cat_a2][1] + '.'
        elif rule_type == 'notAt': # directlr two cases
            a1, a2 = extract_has_attribute_args(rule)
            
            cat_a1 = idx2cat[int(a1[1])]
            cat_a2 = idx2cat[int(a2[1])]
            
            choice_a1 = zebra_puzzle_data[cat_a1][int(a1[2])-1]
            choice_a2 = zebra_puzzle_data[cat_a2][int(a2[2])-1]
            
            sentence = to_nl[cat_a1][0] + choice_a1.lower() + (to_nl[cat_a1][1] if to_nl[cat_a1][0] else '') + ' is not ' + to_nl[cat_a2][0] + choice_a2.lower() + to_nl[cat_a2][1] + '.'
        elif rule_type == 'sameHouse': # directlr two cases
            a1, a2 = extract_has_attribute_args(rule)
            
            cat_a1 = idx2cat[int(a1[1])]
            cat_a2 = idx2cat[int(a2[1])]
            
            choice_a1 = zebra_puzzle_data[cat_a1][int(a1[2])-1]
            choice_a2 = zebra_puzzle_data[cat_a2][int(a2[2])-1]
            
            sentence = to_nl[cat_a1][0] + choice_a1.lower() + (to_nl[cat_a1][1] if to_nl[cat_a1][0] else '') + ' and ' + to_nl[cat_a2][0] + choice_a2.lower() + to_nl[cat_a2][1] + ' are the same person' + '.'
        else:
            breakpoint()
        
        sentence = sentence.capitalize()
        
        clues.append(sentence)
    
    clues_str = '\n'.join(clues)
    
    category_lines = []
    for num_house in range(n_of_houses):
        cat = idx2cat[num_house+1]
        items = ', '.join(zebra_puzzle_data[cat][:n_of_houses]).lower()
        
        category_line = cat.lower() + ': ' + items
        
        category_lines.append(category_line)
    
    category_items_str = '\n'.join(category_lines)
    description = '''There are <NUM_HOUSES> houses, numbered 1 to <NUM_HOUSES> from left to right, as seen from across the street. Each house is occupied by a different person. Each house has a unique attribute for each of the following characteristics:
<CAT-ITEMS>
    
Clues:
<CLUES>

Find an assignment which satisfies all constraints in the problem. After finding the solution only present it without extra text.'''.replace('<NUM_HOUSES>', str(n_of_houses)).replace('<CAT-ITEMS>',category_items_str).replace('<CLUES>', clues_str)

    data_list.append([description, solution_lines])



with open("zebra-generated-16-50_3.json", "w", encoding='utf-8') as file:
    json.dump(data_list, file)


