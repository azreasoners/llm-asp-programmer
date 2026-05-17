import pickle
import os
import copy

from utils import *
from prompts import *

from prompts_post_output import prompt_formatter, prompt_evaluator

import argparse
from argparse import RawTextHelpFormatter

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
    # use llm
    prob_desc = input_dict['prob_desc']
    current_modules = input_dict['current_modules']
    current_output = input_dict['current_output']
    all_verifier_feedback = input_dict['all_verifier_feedback']
    test_case = input_dict['test_case']
    input_dict_ = copy.deepcopy(input_dict)
    update_counter = -1
    actions_possible = [1,0,0]
    previous_main_outputs, previous_input_prompts = [], []

    while action != 'pass' and actions_possible!=[0,0,1]:
        if input_dict['levels'][-1] > max_updates:
            return 'write', input_dict, prompt_cache, pos, pos_label, num_write, token_usage
        
        current_modules_filled = current_modules_prompt.replace('<CURRENT MODULES>', '\n' + current_modules)+'\n' if current_modules else ''
        candidate_feedback_filled = candidate_feedback_prompt.replace('<CURRENT OUTPUT>', current_output) +'\n' if current_output else ''
        verifier_feedback_prompt_filled = verifier_feedback_prompt.replace('<FEEDBACK>', all_verifier_feedback) if all_verifier_feedback else ''
        test_case_filled = test_case + '\n' if test_case else ''
        
        
        possible_actions_str = writeActions_no_ver(actions_possible)
        input_prompt = debugger_prompt.replace('<PROBLEM>', prob_desc).replace('<CURRENT MODULES>', current_modules_filled).replace('<CANDIDATE_FEEDBACK>', candidate_feedback_filled).replace('<VERIFIER_FEEDBACK>', verifier_feedback_prompt_filled).replace('<TEST_CASE>',test_case_filled).replace('<AVAILABLE ACTIONS>', possible_actions_str).replace('<RESOURCE_PROMPT>',RESOURCE_PROMPT).strip()        
        actions_possible = [1,0,1]
        
        ## get response
        redo = False
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
                output_text =response.output[1].content[0].text
            else:
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

    return inputs_path, input_prompts_path, output_path, output_path_lp_problem, final_bc_path


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('--o', type=str, help='(optional) custom output directory name')
    parser.add_argument("--model", type=str, help = '{o4-mini, o1-preview, gpt-4o}', default = 'o4-mini')
    parser.add_argument("--max_updates", type=str, help = 'Maximum number of steps for LLM revision.', default = 10)
    parser.add_argument("--num_verifiers", type=str, help = 'Number of verifier LLMs used.', default = 3)
    parser.add_argument("--RAG", type=str, help = 'A name to distinguish between RAG implementations', default = '')
    parser.add_argument("--resource", type=str, help = 'A name of text file in the resources directory.', default = '')
    parser.add_argument("--limit", type=str, help = 'A number to limit', default = 10e6)
    parser.add_argument("--dataset", type=str, help = 'Dataset from {zebra, sakana-100, etc.}.', required=True)
    parser.add_argument("--timeout", type=int, help = 'Maximum time allowed for a Clingo program to run.', default = 80)
    parser.add_argument("--upper", type=int, help = 'Run in parallel with n workers.', default = None)
    parser.add_argument("--lower", type=int, help = 'Run in parallel with n workers.', default = None)
    
    args = parser.parse_args()
    
    if not args.o:
        args.o = args.dataset
    
    model = args.model
    RAG = args.RAG
    
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
    
    max_updates = 1 + int(args.max_updates)
    num_verifiers = int(args.num_verifiers)
    
    current_modules = None
    current_output = None
    all_verifier_feedback = None
    
    from load_datasets import loaders_dict, meta_prompts_dict, formatter_instructions_dict
    
    # =============================================================================
    # read dataset
    # =============================================================================
    
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
        
        write_intermediate([[prob_desc, [0], 'problem', '']], [0], [''], output_dir, num_write=0)
        
        n2l = {i: letter for (i, letter) in zip(range(1,5), ['a','b','c','d','e'])}
        
        
        input_dict = {'prob_desc': prob_desc, 'current_modules': None, 'current_output': None, 'all_verifier_feedback': None, 'candidate_feedback_filled': None, 'test_case': None,
                      'levels': [1]}
        token_usage = {'main': [], 'verifier': [], 'formatter': [], 'evaluator': []}
        last_action, last_dict, prompt_cache, pos, pos_label, num_write, token_usage = debugger('none', input_dict, prompt_cache, prompt_cache_RAG, token_usage, pos=[0], pos_label = [""], num_write = 1, num_verifiers = num_verifiers, RAG = RAG)
        last_dict['levels'][-1]+=1
        
        
        log = [[last_dict['current_modules'], last_dict['levels'], f'ASP_program', ''],
               [last_dict['current_output'], last_dict['levels'], f'ASP_output', '']]
        
        write_intermediate(log, [0], [''], output_dir, num_write)
        
        # format
        final_output = last_dict['current_output'][:last_dict['current_output'].index('stderr')] if 'stderr' in last_dict['current_output'] else last_dict['current_output']
        prompt_formatter_filled = prompt_formatter.replace('<PROB_DESC>',prob_desc_).replace('<ANSWER_SET>',final_output).replace('<DOMAIN_SPECIFIC_INSTRUCTIONS>',formatter_instructions_dict[args.dataset][0]).replace('<INSTRUCTION>', formatter_instructions_dict[args.dataset][1])
        
        response, prompt_cache, prompt_cache_RAG = get_response_check(prompt_formatter_filled, prompt_cache, prompt_cache_RAG, model = model, redo=False)
        
        if 'gem' in model:
            token_usage['formatter'].append(response.usage_metadata)
        elif 'o4-' in model or 'o3-' in model or 'deepseek' in model:
            token_usage['formatter'].append(response.usage)
            
        token_usages.append(token_usage)
        
        if 'gem' in model:
            formatted_output = response.text
        elif 'o4-' in model or 'o3-' in model:
            formatted_output = response.output_text
        elif 'deepseek' in model:
            formatted_output = response.choices[0].message.content
        formatted_output = formatted_output.strip('```').strip()
        
        log = [[prompt_formatter_filled, last_dict['levels'], f'human-readable output', 'input'],
               [formatted_output, last_dict['levels'], f'human-readable output', 'output']]
        
        write_intermediate(log, [0], [''], output_dir, num_write)
        
        # evaluation
        current_correct = 'unknown'
        if gt!='':
            evaluation_model = 'gemini-2.5-pro'
            
            prompt_evaluator_filled = prompt_evaluator.replace('<GROUND_TRUTH>',gt).replace('<PROPOSED_ANSWER>',formatted_output).replace('<PROB_DESC>', prob_desc_)
            
            response, prompt_cache, prompt_cache_RAG = get_response_check(prompt_evaluator_filled, prompt_cache, prompt_cache_RAG, model = evaluation_model)
            if 'gem' in evaluation_model:
                token_usage['evaluator'].append(response.usage_metadata)
            else:
                token_usage['evaluator'].append(response.usage)
            
            evaluation_str = response.output_text if 'gem' not in evaluation_model else response.text
            evaluation_str = evaluation_str.replace('"','').strip()
            
            
            log = [[prompt_evaluator_filled, last_dict['levels'], f'evaluation', 'input'],
                   [evaluation_str, last_dict['levels'], f'evaluation', 'output']]
            
            write_intermediate(log, [0], [''], output_dir, num_write)
            
            if evaluation_str.lower()=='correct':
                current_correct = 'True'
                correct += 1 
            else:
                current_correct = 'False'
                correct += 0
                print(prob_id)
            total+=1
            print(f'Accuracy: {correct/total} ({correct}/{total})')

        log = [[gt, last_dict['levels'], f'ground_truth', '']]
        write_intermediate(log, [0], [''], output_dir, num_write)
        
        
        # write stats
        if 'gem' in model:
            write_stats(token_usage, current_correct, output_dir)
        elif 'o4-' in model or 'o3' in model:
            write_stats_openai(token_usage, current_correct, output_dir)
        elif 'deepseek-reasoner' in model:
            write_stats_deepseek(token_usage, current_correct, output_dir)
        elif 'deepseek-chat' in model:
            write_stats_deepseek_chat(token_usage, current_correct, output_dir)
    
    if run_once:
        if not RAG:
            save_cache(prompt_cache, model)
        else:
            save_cache(prompt_cache_RAG, model, RAG)


