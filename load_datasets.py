import json



loaders_dict = {}

def getZebraLogicDatasettXL(dataset_name):
    
    from datasets import load_dataset
    sizes = ['6x4', '5x5', '5x6', '6x5', '6x6']
    
    # test set
    ds = load_dataset("allenai/ZebraLogicBench-private", "grid_mode")
    
    puzzles = ds['test']
    puzzle_dict = {}
    for puzzle in puzzles:
        p_id, prob_desc, sol_raw = puzzle['id'], puzzle['puzzle'], puzzle['solution']
        if not any([size in p_id for size in sizes]):
            continue
        gt_string = '\t'.join(sol_raw['header']) + '\n' + '\n'.join(['\t'.join(row) for row in sol_raw['rows']])
        
        puzzle_dict[p_id] = {'problem': prob_desc, 'solution': gt_string}
        
    
    return puzzle_dict

loaders_dict['zlb-xl'] = getZebraLogicDatasettXL
# =============================================================================
# 
# =============================================================================


def getNPE20_dataset(dataset_name):
    
    filename = 'data_' + dataset_name.strip('-20')
    
    with open(f'datasets/nphardeval/{filename}.json', 'r') as f:
        data = json.load(f)
    
    data_dict = {}
    for idx,instance in enumerate(data):
        if idx <80:
            continue
        data_dict[str(idx)] = {'problem': instance[0],
                          'solution': ''}
    
    return data_dict

loaders_dict['edp_p-20'] = getNPE20_dataset
loaders_dict['gcp_d-20'] = getNPE20_dataset
loaders_dict['gcp_hard-20'] = getNPE20_dataset
loaders_dict['ksp-20'] = getNPE20_dataset
loaders_dict['tsp_hard-20'] = getNPE20_dataset
loaders_dict['bsp_p-20'] = getNPE20_dataset
loaders_dict['spp_p-20'] = getNPE20_dataset
loaders_dict['tsp_d-20'] = getNPE20_dataset
loaders_dict['msp_hard-20'] = getNPE20_dataset



# =============================================================================
# 
# =============================================================================


def getPlanbenchMystery(dataset_name):
    
    fname = 'task_1_plan_generation'

    with open(f'datasets/planbench-mystery/{fname}.json', 'r') as f:
        data = json.load(f)
    
    data_dict = {}
    for instance_idx,instance in enumerate(data['instances']):
        prob_id = str(instance['instance_id'])
        #if prob_id not in prob_ids_to_use:
        #    continue
        query = instance['query']
        gt = instance['ground_truth_plan']
        
        idx1 = query.index('[STATEMENT]')
        
        idx2 = query.rindex('[STATEMENT]')
        
        query = query[:idx1]+ query[idx2:]
        if dataset_name in ['pb-t1','pb-t4', 'pb-t5', 'pb-mystery']:
            query = query[:query.index('My plan is as follows:')]
        elif dataset_name in ['pb-t6']:
            query = query[:query.index('After re-planning from the new state')]
        elif dataset_name in ['pb-t7']:
            query = query[:query.index('[RESULTING STATE]')]
            
        #query = query.strip().strip('[PLAN]').strip()
        data_dict[prob_id] = {'problem': query,
                                  'solution': ''        }
        
    return data_dict

loaders_dict['pb-mystery'] = getPlanbenchMystery


# =============================================================================
# 
# =============================================================================

# https://huggingface.co/datasets/microsoft/Eureka-Bench-Logs/tree/main
def getTSP_200(dataset_name):

    with open(r'datasets\TSP\data.json', 'r') as f:
        data_dict = json.load(f)
    
    return data_dict


loaders_dict['tsp-eureka-200'] = getTSP_200

# =============================================================================
# tsp-eureka for baseline
# =============================================================================

def getTSPBaseline_200(dataset_name):

    with open(r'datasets\TSP\data-baseline.json', 'r') as f:
        data_dict = json.load(f)
    
    return data_dict


loaders_dict['tsp-eureka-baseline-200'] = getTSPBaseline_200



# =============================================================================
# 
# =============================================================================


def getZebraGenerated_100(dataset_name):
    
    folder_names = ['zebra-generated-4-50','zebra-generated-6-50','zebra-generated-8-50','zebra-generated-10-50','zebra-generated-12-50']
    
    data_dict = {}
    
    for folder_name in folder_names:
        with open(f'datasets/zebra-generated/{folder_name}.json', 'r') as f:
            data = json.load(f)
        size = folder_name.split('-')[-2]
        for instance_idx,instance in enumerate(data):
            if instance_idx >=20:
                continue
            context, gt = instance
    
            problem_str = context
            
            data_dict[str(instance_idx) + '-' + size ] = {'problem': problem_str,
                                      'solution': gt.__str__()        }
    
    return data_dict

loaders_dict['zebra-generated-100'] = getZebraGenerated_100


# sakana.ai 100 variants
def getSakana100(dataset_name):
    from datasets import load_dataset
    import ast
    import jinja2
    import importlib.util
    import json
    import pandas as pd
    file_path = 'datasets/SudokuBench/sudokuBench_utils.py'
    module_name = 'dataset_llm-asp'
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


    
    overwrite_arrowsome_rules = 'Place the digits from 1 to 6 once each into every Row, Column and Region. All digits on the Arrow are summing to the attached circled cell.'
    # test set
    ds = load_dataset("SakanaAI/Sudoku-Bench", "challenge_100")
    
    puzzles = ds['test']
    puzzle_dict = {}
    for puzzle in puzzles:
        p_id, rules, board, sol_raw = puzzle['title'], puzzle['rules'], puzzle['initial_board'], puzzle['solution']
        rows, cols, visual_elements = puzzle['rows'], puzzle['cols'], puzzle['visual_elements']
        p_id = p_id.replace('?','').replace('.','').replace('\\','')
        initial_board_ascii = module.SudokuBoard.from_ascii(board, rows, cols).to_spaced_ascii(unfilled='.')
        if visual_elements == '[]' or visual_elements == '':
            pretty_visual_elements = None
        else:
            visual_elements = json.loads(visual_elements)
            pretty_visual_elements = module.pretty_print_visual_elements(visual_elements)
        rules = ast.literal_eval(rules)
        if p_id == 'Arrowsome':
            rules = overwrite_arrowsome_rules
        n_rows, n_cols = puzzle['rows'], puzzle['cols']
        if n_rows == 9 and n_cols ==9:
            split_size = 9
        elif n_rows == 6 and n_cols ==6:
            split_size = 6
        elif n_rows == 4 and n_cols ==4:
            split_size = 4
        else:
            breakpoint()
        board_ = board.replace('.','0')
        board_ = [[int(el) for el in board_[i:i+split_size]] for i in range(0,len(board_),split_size)]
        board_str = '\n'.join([row.__str__() for row in board_])
        #gt_string = '\t'.join(sol_raw['header']) + '\n' + '\n'.join(['\t'.join(row) for row in sol_raw['rows']])
        prob_desc = 'Solve the following problem, where 0s are non-given cells.\n' + rules.strip('"') + '\n\nBoard:\n' + board_str + (('\n\nVisual elements:\n'  + puzzle['visual_elements'].__str__()) if len(puzzle['visual_elements'])>2 else '')
        
        
        if  'nikoli' in p_id.lower():
            rule_prompt = module.ONE_SHOT_STANDARD_PROMPT
        else:
            rule_prompt = module.ONE_SHOT_VARIANT_PROMPT
        one_shot_prompt = jinja2.Template(rule_prompt).render(
            rows=rows,
            cols=cols,
            rules=rules,
            pretty_visual_elements=pretty_visual_elements,
            current_board=initial_board_ascii,
            )
        
        
        puzzle_dict[p_id] = {'problem': one_shot_prompt, 'solution': sol_raw}
        
    
    return puzzle_dict



loaders_dict['sakana-100'] = getSakana100



# =============================================================================
# meta prompts
# =============================================================================


spp_p_meta = '''Note: The graph is undirected, so all edges are bidrectional. For example, if there is an edge between a and b, that means there is an edge between b and a.'''

tsp_hard_meta = '''Note: The graph is undirected, so all paths are bidrectional. For example, if there is a path between a and b, that means there is an path between b and a.'''

tsp_hard_meta2 = '''Note: The graph is undirected, so all paths are bidrectional. For example, if there is a path between a and b, that means there is an path between b and a.
IMPORTANT: You may use the minimize statement to find the optimal cost, but you don't need to use sum, because the minimize statement will instruct Clingo to output the optimal cost (and a sum may cause the program to take a long time to terminate).
IMPORTANT: Do NOT track the tour with steps or timesteps as this can much longer to solve, resulting in a timeout. Rather, just model the edges in the tour.'''



tsp_eureka_meta = '''Important: Since optimization may take a long time, use a greedy route to cut down the search space. The actual optimal distance must be less than or equal to a greedy route. Incorporate it in the program. Also, due to the potential size of the problem, be mindful of way it is modeled. Do not use time steps, and try to cut down the search space as much as possible as to not burden the grounder/solver to consider many possible invalid solutions.

For example, the following optimization is efficient:

#minimize { D,U,V : tour_edge_cost(U,V,D) }.
'''

tsp_eureka_meta = '''IMPORTANT: You may use the minimize statement to find the optimal cost, but you don't need to use sum, because the minimize statement will instruct Clingo to output the optimal cost.
IMPORTANT: Do NOT track the tour with steps or timesteps as this can much longer to solve, resulting in a timeout. Rather, just model the edges in the tour.'''

zebra_generated_meta3 = '''IMPORTANT: Atoms with large arity may cause the solver to take a very long time (resulting in a timeout) for larger problems, so do not introduce them unnecessarily.
For example, the following will be problematic, since `solution` has many arguments:
solution(House, Cigarette, Food, Instrument, HouseType, Nationality, Occupation, Music, Fiction) :-
    house(House),
    has(House, cigarette, Cigarette),
    has(House, food, Food),
    has(House, instrument, Instrument),
    has(House, house_type, HouseType),
    has(House, nationality, Nationality),
    has(House, occupation, Occupation),
    has(House, music_genre, Music),
    has(House, fictional_genre, Fiction).
There is no need to use the `solution` atom here, the `has` is sufficient to express the answer for example.
'''


answer_set_meta = '''In the program, include the #show command for atoms which will help for verifying the answer and/or debugging. For example, don't just show the final answer, but show atoms which can be used to check that the parts determining the final answer are also correct.'''

answer_set_meta = '''Operators: `+`, `*`, `**` (power), `/` (integer division), `\` (remainder), `|...|` (absolute value).

In the program, include the #show command for atoms which will help for verifying the answer and/or debugging. For example, don't just show the final answer, but show atoms which can be used to check that the parts determining the final answer are also correct.'''


gcp_d_meta = 'Note: The graph is undirected, so all edges are bidrectional. For example, if there is an edge between a and b, that means there is an edge between b and a.'
meta_prompts_dict = {'gcp_d-20': gcp_d_meta,
                     'tsp_hard-20': tsp_hard_meta2,
                     'tsp_d-20': tsp_hard_meta,
                     'spp_p-20': spp_p_meta,
                     'tsp-eureka': tsp_eureka_meta,
                     'tsp-eureka-200': tsp_eureka_meta,
                     'tsp-eureka-baseline-200': tsp_eureka_meta,
                     'zebra-generated-100': zebra_generated_meta3}

for key in loaders_dict:
    if key not in meta_prompts_dict:
        meta_prompts_dict[key] = ''


# =============================================================================
# formatter 
# =============================================================================


formatter_instructions_dict = {}

nl_instruction_basic= 'Your conversion should be encapsulated completely in 3 backticks, without any extraneous text. It should be in natural language, and precise. If the Clingo output is unsatisfiable, or the program produces an error, the write "UNSAT" or "ERROR" encapsulated in 3 backticks.'
nl_instruction_basic2= 'Your conversion should be encapsulated completely in 3 backticks, without any extraneous text. If the Clingo output is unsatisfiable, or the program produces an error, the write "UNSAT" or "ERROR" encapsulated in 3 backticks.'
extra_prompt = {}

formatter_instructions_dict['edp_p'] = ["Enclose the final minimum number of operations in <final_answer></final_answer> tags, like <final_answer>{'Operations': 'MINIMUM_NUMBER_OF_OPERATIONS'}</final_answer>.", nl_instruction_basic2]
formatter_instructions_dict['edp_p-20'] = formatter_instructions_dict['edp_p']

formatter_instructions_dict['gcp_d'] = ["Enclose the final yes/no answer in <final_answer></final_answer> tags, like <final_answer>{'Feasible': 'YES_OR_NO'}</final_answer>.", nl_instruction_basic2]
formatter_instructions_dict['gcp_d-20'] = formatter_instructions_dict['gcp_d']

formatter_instructions_dict['gcp_hard'] = ["Enclose the final output of all vertex numbers and their associated colors, wrapped by final_answer tag, like <final_answer>{0:'COLOR_1', 1:'COLOR_2', ...}</final_answer>.", nl_instruction_basic2]
formatter_instructions_dict['gcp_hard-20'] = formatter_instructions_dict['gcp_hard'] 

formatter_instructions_dict['ksp'] = ["Enclose the final decision and total value in <final_answer></final_answer> tags, like <final_answer>{'Feasible': 'YES_OR_NO', 'TotalValue': 'TOTAL_VALUE', 'SelectedItemIds': [0, 1]}</final_answer>.", nl_instruction_basic2]
formatter_instructions_dict['ksp-20'] = formatter_instructions_dict['ksp']

formatter_instructions_dict['bsp_p'] = ["Enclose the final position of the target value in <final_answer></final_answer> tags, like <final_answer>{'Position': 'TARGET_POSITION'}</final_answer>.", nl_instruction_basic2]
formatter_instructions_dict['bsp_p-20']  = formatter_instructions_dict['bsp_p'] 

formatter_instructions_dict['spp_p'] = ["Enclose the final path and total distance in <final_answer></final_answer> tags, like <final_answer>{'Path': 'START->...->END', 'TotalDistance': 'INT_TOTAL_DISTANCE'}</final_answer>.", nl_instruction_basic2]
formatter_instructions_dict['spp_p-20'] = formatter_instructions_dict['spp_p']

formatter_instructions_dict['msp_hard'] = ["Your output should contain two parts enclosed by <root></root>. First, your step by step reasoning wraped by <reasoning></reasoning>. Second, the final output of meeting numbers followed by a list of slots, like <final_answer>{0:[1,2], 1:[4], ...}</final_answer>.", nl_instruction_basic2]

formatter_instructions_dict['tsp_d'] = ["Enclose the final yes/no answer in <final_answer></final_answer> tags, like <final_answer>{'Feasible': 'YES_OR_NO'}</final_answer>.", nl_instruction_basic2]
formatter_instructions_dict['tsp_d-20'] = formatter_instructions_dict['tsp_d']

formatter_instructions_dict['tsp_hard'] = ["Enclose the final output of the result path and total distance wrapped by final_answer tag, like <final_answer>{'Path': '0->1->2->...->N->0', 'TotalDistance': 'INT_TOTAL_DISTANCE'}</final_answer>", nl_instruction_basic2]
formatter_instructions_dict['tsp_hard-20'] = formatter_instructions_dict['tsp_hard']



pb_mystery_formatting = '''Enclose the plan in [PLAN] ... [PLAN END], in the following format:
```
[PLAN]    
Attack object a
Feast object b object c
...
Overcome object a object b
[PLAN END]
```
'''

formatter_instructions_dict['pb-mystery'] = [pb_mystery_formatting, nl_instruction_basic2]



bspPrompts = {
    "Output_content": "Please identify the position of the target value in the array. Offer a brief, step-by-step account of your search process. Aim for conciseness in your response.",
    "Output_format": "Your output should be enclosed in <root></root> tags. Include your search process in <reasoning></reasoning> tags and the final position of the target value in <final_answer></final_answer> tags, like <final_answer>{'Position': 'TARGET_POSITION'}</final_answer>.",
}

edpPrompts = {
    "Output_content": "Please provide the minimum number of operations required to transform the first string into the second string. Offer a brief explanation of your methodology. Keep your response concise and focused.",
    "Output_format": "Enclose your output within <root></root> tags. Present your reasoning in <reasoning></reasoning> tags and the final minimum number of operations in <final_answer></final_answer> tags, like <final_answer>{'Operations': 'MINIMUM_NUMBER_OF_OPERATIONS'}</final_answer>.",
}

# NP-complete problems
tsp_dPrompts = {
    "Output_content": "Provide a yes or no answer, with a succinct explanation of your decision process. Focus on clarity and brevity in your response.",
    "Output_format": "Enclose your output in <root></root> tags. Present your reasoning in <reasoning></reasoning> tags and the final yes/no answer in <final_answer></final_answer> tags, like <final_answer>{'Feasible': 'YES_OR_NO'}</final_answer>.",
}

gcp_dPrompts = {
    "Output_content": "Provide a yes or no answer, along with a concise explanation of your reasoning. Keep your explanation focused and brief.",
    "Output_format": "Enclose your output in <root></root> tags. Include your reasoning in <reasoning></reasoning> tags and the final yes/no answer in <final_answer></final_answer> tags, like <final_answer>{'Feasible': 'YES_OR_NO'}</final_answer>.",
}

extra_prompt['ksp'] = {
    "Output_content": "Indicate if an optimal subset exists and its total value. Offer a concise explanation of your selection process. Aim for clarity and brevity in your response.",
    "Output_format": "Enclse your final decision and total value in <final_answer></final_answer> tags, like <final_answer>{'Feasible': 'YES_OR_NO', 'TotalValue': 'TOTAL_VALUE'}</final_answer>.",
}

# NP-hard problems
extra_prompt['tsp_hard'] = {
    "Output_content": "Please list each city in the order they are visited. Provide the total distance of the trip. You should also provide very short step by step reasoning. Do not use multiple lines and try your best to save output tokens.",
    "Output_format": "The final output should have the result path and total distance wrapped by a final_answer tag, like <final_answer>{'Path': '0->1->2->...->N->0', 'TotalDistance': 'INT_TOTAL_DISTANCE'}</final_answer>",
}

extra_prompt['gcp_hard'] = {
    "Output_content":"Please label every vertex, even if it is disconnected from the rest of the graph. Please provide each vertex's color. Do not skip any vertices. You should also provide very short step by step reasoning. Do not use multiple lines and try your best to save output tokens.",
    "Output_format":"Enclose the final output of all vertex numbers and their associated colors, wrapped by final_answer tag, like <final_answer>{0:'COLOR_1', 1:'COLOR_2', ...}</final_answer>.",
}

extra_prompt['msp_hard'] = {
    "Output_content": "Please provide a time slot where all participants can attend the meeting. You should also provide very short step by step reasoning. Do not use multiple lines and try your best to save output tokens.",
    "Output_format": "Enclose the final output of meeting numbers followed by a list of slots, like <final_answer>{0:[1,2], 1:[4], ...}</final_answer>.",
}


for key in loaders_dict:
    if key not in formatter_instructions_dict:
        formatter_instructions_dict[key] = ['', nl_instruction_basic]