import pickle
import os
import openai
import copy
from core.utils import *
from core.prompts import *
from core.prompts import writeActions_no_ver_full_prog as writeActions_no_ver

from core.prompts_post_output import prompt_formatter, prompt_evaluator

import argparse
from argparse import RawTextHelpFormatter


parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument('--o', type=str, help='(optional) custom output directory name')
parser.add_argument("--model", type=str, help = '{o4-mini, o1-preview, gpt-4o}', default = 'o4-mini')
parser.add_argument("--max_updates", type=str, help = 'Maximum number of steps for LLM revision.', default = 8)

parser.add_argument("--num_verifiers", type=str, help = 'Number of verifier LLMs used.', default = 3)
parser.add_argument("--RAG", type=str, help = 'A name to distinguish between RAG implementations', default = '')

parser.add_argument("--resource", type=str, help = 'A name of text file in the resources directory.', default = '')
parser.add_argument("--limit", type=str, help = 'A number to limit', default = 10e6)

parser.add_argument("--dataset", type=str, help = 'Dataset from {multiNMR-skeptical}.', default='multiNMR-skeptical')
parser.add_argument("--timeout", type=int, help = 'Maximum time allowed for a Clingo program to run.', default = 60)
parser.add_argument("--upper", type=int, help = 'Run in parallel with n workers.', default = None)
parser.add_argument("--lower", type=int, help = 'Run in parallel with n workers.', default = None)


args = parser.parse_args()

if not args.o:
    args.o = args.dataset
assert args.dataset == 'multiNMR-skeptical'


def processOutputs(stdout, stderr, exit_code, current_modules):
    error_lines_string = ''
    if 'TIMEOUT' not in stdout:
        out, err, err_true = process_clingo_output(stdout, stderr)
    else:
        out, err, err_true = stdout, stderr, exit_code
    error_lines = ''
    if err_true:
        error_lines = get_error_lines(current_modules, stderr)
        if error_lines:
            error_lines_string = '\n'.join(error_lines)
    
    return out, err, err_true, error_lines, error_lines_string

def debugger(action, input_dict, prompt_cache, prompt_cache_RAG, token_usage, pos, pos_label, num_write, reload = False, num_verifiers = 1, single_update=False, RAG = ''):
    test_counter = 1 
    # use llm
    prob_desc = input_dict['prob_desc']
    current_modules = input_dict['current_modules']
    current_output = input_dict['current_output']
    current_output1, current_output2 = '', ''
    all_verifier_feedback = input_dict['all_verifier_feedback']
    test_case = input_dict['test_case']
    input_dict_ = copy.deepcopy(input_dict)
    update_counter = -1
    actions_possible = [1,0,0]
    previous_main_outputs, previous_input_prompts = [], []
    while action != 'pass' and actions_possible!=[0,0,1]:
        if input_dict['levels'][-1] > max_updates:
            return 'write', input_dict, prompt_cache, pos, pos_label, num_write, token_usage
        # Get next action
        
        ## use llm
        current_modules_filled = current_modules_prompt.replace('<CURRENT MODULES>', '\n' + current_modules)+'\n' if current_modules else ''
        candidate_feedback_filled = candidate_feedback_prompt_both.replace('<CURRENT OUTPUT1>', current_output1).replace('<CURRENT OUTPUT2>', current_output2) +'\n' if current_output else ''
        verifier_feedback_prompt_filled = verifier_feedback_prompt.replace('<FEEDBACK>', all_verifier_feedback) if all_verifier_feedback else ''
        test_case_filled = test_case + '\n' if test_case else ''
        
        possible_actions_str = writeActions_no_ver(actions_possible)
        input_prompt = debugger_prompt.replace('<PROBLEM>', prob_desc).replace('<CURRENT MODULES>', current_modules_filled).replace('<CANDIDATE_FEEDBACK>', candidate_feedback_filled).replace('<VERIFIER_FEEDBACK>', verifier_feedback_prompt_filled).replace('<TEST_CASE>',test_case_filled).replace('<AVAILABLE ACTIONS>', possible_actions_str).replace('<RESOURCE_PROMPT>',RESOURCE_PROMPT).strip()        
        actions_possible = [1,0,1]
        ## get response
        redo = True
        if input_prompt in previous_input_prompts:
            redo = True
        response, prompt_cache, prompt_cache_RAG = get_response_check(input_prompt, prompt_cache, prompt_cache_RAG, model = model, redo=redo, RAG = RAG)
        
        if not RAG:
            
            if 'gem' in model:
                output_text = response.text
            elif 'o4-' in model or 'o3-' in model:
                output_text = response.output_text
            elif 'deepseek' in model:
                output_text = response.choices[0].message.content
            
        else:
            if 'gem' not in model:
                try:
                        response_message = [resp for resp in response.output if resp.type =='message'][0]
                        output_text =response_message.content[0].text 
                        
                        if 'o4-mini' in model:
                            file_search_response = [resp for resp in response.output if resp.type =='file_search_call']
                            if len(file_search_response) > 0:
                                file_search_str = 'Queries: ' + str(file_search_response[0].queries) + '\n\n' +  ('\n\n' + '-'*50 + '\n\n').join(['Score: ' + str(call.score) + '\n\n' + call.text for call in file_search_response[0].results])
                                log = [[file_search_str, pos, 'file_search', '']]
                            else:
                                log = [['no file search was done', pos, 'file_search_none', '']]
                            write_intermediate(log, pos, pos_label, output_dir, num_write, RAG=RAG)
                        
                except:
                    breakpoint()
            else:
                breakpoint()
                output_text = response.text
        
        if output_text in previous_main_outputs:
            redo = True
        
        if 'gem' in model:
            token_usage['main'].append(response.usage_metadata)
        else:
            token_usage['main'].append(response.usage)

        previous_main_outputs.append(output_text)
        previous_input_prompts.append(input_prompt)
        log = [[input_prompt, input_dict['levels'], 'main', 'input'],
               [output_text, input_dict['levels'], 'main', 'output']]
        
            
        action, ASP_modules = parse_output_no_verifier(output_text)
        log = [[input_prompt, pos, 'main', 'input'],
               [output_text, pos, 'main', 'output']]
        write_intermediate(log, pos, pos_label, output_dir, num_write, RAG=RAG)
        num_write+=1

        # set possible actions
        if action=='update':
            update_counter+=1
            if test_counter==1: 
                pass
            
        if action =='update':
            if pos[-1]==0:
                pos_label.pop()
                pos_label.append('u')
            pos[-1]+=1


            current_modules = ASP_modules[0]
            input_dict['current_modules'] = current_modules
            ## run clingo
            entailment, stdouts, stderrs, exit_codes  = check_entailment(current_modules, timeout = args.timeout, query = 'test_query', strong_negation=True)
            input_dict['entailment'] = entailment
            out1, err1, err_true1, error_lines1, error_lines_string1 = processOutputs(stdouts[0], stderrs[0], exit_codes[0], current_modules[0])
            out2, err2, err_true2, error_lines2, error_lines_string2 = processOutputs(stdouts[1], stderrs[1], exit_codes[1], current_modules[1])
            
            stdout1, stdout2 = stdouts
            stderr1, stderr2 = stderrs            
            
            current_output1 = f'stdout:\n{out1}' + (f'\n\nstderr:\n{stderr1}' if stderr1!='' else '') + (f'\n\nLines where errors occur:\n{error_lines_string1}' if error_lines1 else '')
            current_output2 = f'stdout:\n{out2}' + (f'\n\nstderr:\n{stderr2}' if stderr2!='' else '') + (f'\n\nLines where errors occur:\n{error_lines_string2}' if error_lines2 else '')
            current_output = current_output1 + '\n\n' + current_output2
            input_dict['current_output'] = current_output
            
            input_dict['levels'][-1] +=1
            if single_update:
                return 
        else:
            pass
    pos.append(-1)
    pos_label.append('p')
    return 'write', input_dict, prompt_cache, pos, pos_label, num_write, token_usage


def write_output_dirs(prob_id, dataset_name):
    output_path_base = f'outputs_{model}'
    output_path_lp = os.path.join(output_path_base, dataset_name)
    output_path_lp_problem = os.path.join(output_path_lp, prob_id)
    
    
    inputs_path = os.path.join(output_path_lp_problem, 'problem_description')
    input_prompts_path = os.path.join(output_path_lp_problem, 'pipeline_prompts')
    output_path = os.path.join(output_path_lp_problem, 'pipeline_intermediate_outputs')
    final_bc_path = os.path.join(output_path_lp_problem, 'final_bc_program')
    
    os.makedirs(output_path_base, exist_ok=True)
    os.makedirs(output_path_lp, exist_ok=True)
    os.makedirs(output_path_lp_problem, exist_ok=True)
    
    os.makedirs('temp_bc+', exist_ok=True)

    return inputs_path, input_prompts_path, output_path, output_path_lp_problem, final_bc_path



model = args.model
RAG = args.RAG

assert int(args.num_verifiers) % 2 == 1, print('The number of verifiers must be an odd number.')

if args.resource:
    with open(os.path.join('resources',args.resource),'r', encoding="utf8") as f:
        resource = f.read()
    
    RESOURCE_PROMPT = resource_prompt.replace('<RESOURCE>',resource)
else:
    RESOURCE_PROMPT = ''
    

if not os.path.exists('outputs'+'_'+model):
    os.mkdir('outputs'+'_'+model)

if f'prompt_cache_asp_{model}.pickle' in os.listdir():
    with open(f'prompt_cache_asp_{model}.pickle', 'rb') as handle:
        prompt_cache = pickle.load(handle)
else:
    prompt_cache = dict()

if f'prompt_cache_asp_{model}_RAG_{RAG}.pickle' in os.listdir():
    with open(f'prompt_cache_asp_{model}_RAG_{RAG}.pickle', 'rb') as handle:
        prompt_cache_RAG = pickle.load(handle)
else:
    prompt_cache_RAG = dict()



max_updates = 1 + int(args.max_updates) # +1 since the initial generation doesn't count as a revision
num_verifiers = int(args.num_verifiers)

current_modules = None
current_output = None
all_verifier_feedback = None


from core.load_datasets import loaders_dict, meta_prompts_dict, formatter_instructions_dict


# =============================================================================
# read dataset
# =============================================================================

# should be a dictionary with the problem description and ground truths 
try:
    print('Loading dataset...')
    data = loaders_dict[args.dataset](args.dataset)
    print('Completed.')
except:
    print(f'There was an error while loading {args.dataset}.')
    import sys;sys.exit()

# =============================================================================
# main loop for pipeline + evaluation
# =============================================================================
correct, total = 0, 0
run_once = False
limit = int(args.limit)
token_usages = []
for prob_idx, (prob_id, instance) in enumerate(data.items()):

    if args.upper != None and args.lower != None:
        if prob_idx not in [i for i in range(int(args.lower), int(args.upper))]:
            continue
    else:
        if prob_idx >= limit:
            break

    prob_desc_, gt = instance['problem'], instance['solution']
    
    prob_desc = prob_desc_ + ('\n' + meta_prompts_dict[args.dataset])


    _, _, _, output_dir, _ = write_output_dirs(prob_id.replace('?',''), args.o)
    
    already_evaluated_filename = [filename for filename in os.listdir(output_dir) if 'evaluation_output' in filename]
    if 'stats.txt' in os.listdir(output_dir):
        if not gt:
            continue
        with open(os.path.join(output_dir, already_evaluated_filename[0]), 'r') as f:
            eval_str = f.read()
        
        
        if eval_str.lower()=='correct':
            correct += 1 
        else:
            correct += 0
        total+=1
        print(f'Accuracy: {correct/total} ({correct}/{total})')
        continue
    run_once =  True
    if prob_idx % 12 == 0 and prob_idx !=0:
        if not RAG:
            save_cache(prompt_cache, model)
        else:
            save_cache(prompt_cache_RAG, model, RAG)
    

    p_step = 1
    
    write_intermediate([[prob_desc, [0], 'problem', '']], [0], [''], output_dir, num_write=0)
    
    n2l = {i: letter for (i, letter) in zip(range(1,5), ['a','b','c','d','e'])}
    
    
    input_dict = {'prob_desc': prob_desc, 'current_modules': None, 'current_output': None, 'all_verifier_feedback': None, 'candidate_feedback_filled': None, 'test_case': None,
                  'levels': [1]}
    pos = [1]
    token_usage = {'main': [], 'verifier': [], 'formatter': [], 'evaluator': []}
    last_action, last_dict, prompt_cache, pos, pos_label, num_write, token_usage = debugger('none', input_dict, prompt_cache, prompt_cache_RAG, token_usage, pos=[0], pos_label = [""], num_write = 1, num_verifiers = num_verifiers, RAG = RAG)
    last_dict['levels'][-1]+=1
    
    
    
    log = [[last_dict['current_modules'], last_dict['levels'], f'ASP_program', ''],
           [last_dict['current_output'], last_dict['levels'], f'ASP_output', '']]
    
    write_intermediate(log, [0], [''], output_dir, num_write)
    
    
    # evaluation
    current_correct = 'unknown'
    if gt!='':
        
        if last_dict['entailment'].lower() == gt[0].lower():
            current_correct = 'True'
            correct += 1 
        else:
            current_correct = 'False'
            correct += 0
            print(prob_id)
        total+=1
        print(f'Accuracy: {correct/total} ({correct}/{total})')
        
        evaluation_str = 'CORRECT' if current_correct == 'True' else 'WRONG'
        evaluation_str = evaluation_str.replace('"','').strip()
        
        
        log = [['', last_dict['levels'], f'evaluation', 'input'],
               [evaluation_str, last_dict['levels'], f'evaluation', 'output']]
        
        write_intermediate(log, [0], [''], output_dir, num_write)
        
        
    if True:
        log = [[gt[0], last_dict['levels'], f'ground_truth', '']]
        write_intermediate(log, [0], [''], output_dir, num_write)
    if 'gem' in model:
        write_stats(token_usage, current_correct, output_dir)
    elif 'o4-' in model or 'o3' in model:
        write_stats_openai(token_usage, current_correct, output_dir)
    elif 'deepseek-reasoner' in model:
        write_stats_deepseek(token_usage, current_correct, output_dir)
    elif 'deepseek-chat' in model:
        write_stats_deepseek_chat(token_usage, current_correct, output_dir)
    elif 'deepseek-v3-' in model:
        write_stats_deepseek_v3(token_usage, current_correct, output_dir)

if run_once:
    if not RAG:
        save_cache(prompt_cache, model)
    else:
        save_cache(prompt_cache_RAG, model, RAG)


