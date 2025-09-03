import pickle
import os
import openai
import copy
from utils import run_clingo_external, process_clingo_output, get_error_lines, write_intermediate, get_response_check, save_cache, parse_output_no_verifier
from prompts import current_modules_prompt, candidate_feedback_prompt, verifier_feedback_prompt, resource_prompt


from prompts_post_output import prompt_formatter, prompt_evaluator

from prompts import debugger_prompt_resource_v2_2 as debugger_prompt
from prompts import writeActions_no_ver_full_prog as writeActions_no_ver

import argparse
from argparse import RawTextHelpFormatter


parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument('--o', type=str, help='(optional) custom output directory name')
parser.add_argument("--model", type=str, help = '{o4-mini, o1-preview, gpt-4o}', default = 'o4-mini')
parser.add_argument("--task", type=str, help = 'Problem to run.', required=True)
parser.add_argument("--max_updates", type=str, help = 'Maximum number of steps for LLM revision.', default = 8)

parser.add_argument("--num_verifiers", type=str, help = 'Number of verifier LLMs used.', default = 3)
parser.add_argument("--RAG", type=str, help = 'A name to distinguish between RAG implementations', default = '')
parser.add_argument("--timeout", type=int, help = 'Maximum time allowed for a Clingo program to run.', default = 80)
parser.add_argument("--resource", type=str, help = 'A name of text file in the resources directory.', default = '')

args = parser.parse_args()




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


def debugger(action, input_dict, prompt_cache, prompt_cache_RAG, pos, pos_label, num_write, reload = False, num_verifiers = 1, single_update=False, RAG = ''):
    prob_desc = input_dict['prob_desc']
    current_modules = input_dict['current_modules']
    current_output = input_dict['current_output']
    all_verifier_feedback = input_dict['all_verifier_feedback']
    test_case = input_dict['test_case']
    update_counter = -1
    actions_possible = [1,0,0]
    previous_main_outputs, previous_input_prompts = [], []
    while action != 'pass' and actions_possible!=[0,0,1]:
        if input_dict['levels'][-1] > max_updates:
            return 'write', input_dict, prompt_cache, pos, pos_label, num_write
        
        current_modules_filled = current_modules_prompt.replace('<CURRENT MODULES>', '\n' + current_modules)+'\n' if current_modules else ''
        candidate_feedback_filled = candidate_feedback_prompt.replace('<CURRENT OUTPUT>', current_output) +'\n' if current_output else ''
        verifier_feedback_prompt_filled = verifier_feedback_prompt.replace('<FEEDBACK>', all_verifier_feedback) if all_verifier_feedback else ''
        test_case_filled = test_case + '\n' if test_case else ''
        
        possible_actions_str = writeActions_no_ver(actions_possible)
        input_prompt = debugger_prompt.replace('<PROBLEM>', prob_desc).replace('<CURRENT MODULES>', current_modules_filled).replace('<CANDIDATE_FEEDBACK>', candidate_feedback_filled).replace('<VERIFIER_FEEDBACK>', verifier_feedback_prompt_filled).replace('<TEST_CASE>',test_case_filled).replace('<AVAILABLE ACTIONS>', possible_actions_str).replace('<RESOURCE_PROMPT>',RESOURCE_PROMPT)
        
        actions_possible = [1,0,1]
        response, prompt_cache, prompt_cache_RAG = get_response_check(input_prompt, prompt_cache, prompt_cache_RAG, model = model, redo=False, RAG = RAG)
        if not RAG:
            if 'gem' in model:
                output_text = response.text
            elif 'o4-' in model or 'o3-' in model:
                output_text = response.output_text
            elif 'deepseek' in model:
                output_text = response.choices[0].message.content
            
        else:
            if 'gem' not in model:
                output_text =response.output[1].content[0].text ## check
            else:
                output_text = response.text
        
        if output_text in previous_main_outputs:
            redo = True

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
            
        if action =='update':
            if pos[-1]==0:
                pos_label.pop()
                pos_label.append('u')
            pos[-1]+=1


            current_modules = ASP_modules[0]
            input_dict['current_modules'] = current_modules
            ## run clingo
            stdout, stderr, exit_code = run_clingo_external(current_modules, timeout = args.timeout)
            out, err, err_true, error_lines, error_lines_string = processOutputs(stdout, stderr, exit_code, current_modules)
            
            current_output = f'stdout:\n{out}' + (f'\n\nstderr:\n{stderr}' if stderr!='' else '') + (f'\n\nLines where errors occur:\n{error_lines_string}' if error_lines else '')
            input_dict['current_output'] = current_output
            
            input_dict['levels'][-1] +=1
            if single_update:
                return 
            
        else:
            pass
    pos.append(-1)
    pos_label.append('p')
    return 'write', input_dict, prompt_cache, pos, pos_label, num_write


model = args.model

if not args.o:
    args.o= args.task

RAG = args.RAG
assert int(args.num_verifiers) % 2 == 1, print('The number of verifiers must be an odd number.')

if args.resource:
    with open(os.path.join('resources',args.resource),'r', encoding="utf8") as f:
        resource = f.read()
    
    RESOURCE_PROMPT = resource_prompt.replace('<RESOURCE>',resource)
else:
    RESOURCE_PROMPT = ''
    

with open(os.path.join('envs',args.task, 'problem.txt'), 'r') as f:
    prob_desc = f.read()

if not os.path.exists('outputs'+'_'+model):
    os.mkdir('outputs'+'_'+model)

output_dir = os.path.join('outputs'+'_'+model, args.o)

if not os.path.exists(output_dir):
    os.mkdir(output_dir)


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

p_step = 1

write_intermediate([[prob_desc, [0], 'problem', '']], [0], [''], output_dir, num_write=0)

n2l = {i: letter for (i, letter) in zip(range(1,5), ['a','b','c','d','e'])}



input_dict = {'prob_desc': prob_desc, 'current_modules': None, 'current_output': None, 'all_verifier_feedback': None, 'candidate_feedback_filled': None, 'test_case': None,
              'levels': [1]}
pos = [1]

last_action, last_dict, prompt_cache, pos, pos_label, num_write = debugger('none', input_dict, prompt_cache, prompt_cache_RAG, pos=[0], pos_label = [""], num_write = 1, num_verifiers = num_verifiers, RAG = RAG)
last_dict['levels'][-1]+=1



log = [[last_dict['current_modules'], last_dict['levels'], f'ASP_program', ''],
       [last_dict['current_output'], last_dict['levels'], f'ASP_output', '']]

write_intermediate(log, [0], [''], output_dir, num_write)


# format

prompt_formatter_filled = prompt_formatter.replace('<PROB_DESC>',prob_desc).replace('<ANSWER_SET>',last_dict['current_output']).replace('<DOMAIN_SPECIFIC_INSTRUCTIONS>','')

response, prompt_cache, prompt_cache_RAG = get_response_check(prompt_formatter_filled, prompt_cache, prompt_cache_RAG, model = model, redo=False)

formatted_output = response.output_text if 'gem' not in model else response.text
formatted_output = formatted_output.strip('```').strip()

log = [[formatted_output, last_dict['levels'], f'human-readable output', '']]

write_intermediate(log, [0], [''], output_dir, num_write)



