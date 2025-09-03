import os
import subprocess
import pickle
import time
import openai
import re
import json
import random 

from keys import API_KEY,ORG_KEY

openai.api_key= API_KEY
openai.organization = ORG_KEY

from openai import OpenAI
client = OpenAI(api_key = API_KEY, organization = ORG_KEY)

from google import genai
from keys import API_KEY_GEM, API_KEY_DEEPSEEK

client_gem = genai.Client(api_key=API_KEY_GEM)
client_deepseek = OpenAI(api_key=API_KEY_DEEPSEEK, base_url="https://api.deepseek.com")


#from utils import run_clingo_external, process_clingo_output, get_error_lines, write_intermediate, get_response_check, save_cache, parse_output_no_verifier, write_stats, write_stats_openai, write_stats_deepseek, write_stats_deepseek_chat




def run_clingo_external(program_str, num_models=1, timeout = 60):
    """
    Run a Clingo program externally via subprocess.

    Args:
        program_str (str): The ASP program as a string.
        num_models (int): Max number of models to compute.

    Returns:
        Tuple[str, str, int]: (stdout, stderr, return_code)
    """
    try:
        # Run Clingo with input from stdin (-), return num_models models
        result = subprocess.run(
            ["clingo", "-", str(num_models), '--opt-mode=optN', '-t 8'],
            input=program_str.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout = timeout
        )
        return result.stdout.decode("utf-8"), result.stderr.decode("unicode_escape"), result.returncode
    except subprocess.TimeoutExpired as exc:
        print(exc)
        return f"TIMEOUT: exceeded {timeout} seconds.", '', ''
    #except FileNotFoundError:
        #return "", "Clingo not found. Make sure it is installed and in your PATH.", 1


def process_clingo_output(stdout, stderr):
    if 'OPTIMUM FOUND' in stdout:
        stdout = stdout[:stdout.find('Progression')] + stdout[stdout.rfind('Answer: 1'):]
    while '(Time:' in stdout: # clingo 5.8
        time_idx = stdout.index('(Time:')
        
        time_end_idx = stdout.find(')', time_idx)
    
        stdout = stdout[:time_idx] + stdout[time_end_idx + 1:]
    
    if 'Solving...' in stdout:
        start_idx = stdout.index('Solving...')
    elif 'UNKNOWN' in stdout:
        start_idx = stdout.index('UNKNOWN')
    stdout = stdout.replace('Answer: 1', 'Answer Set 1:')
    end_idx = stdout.index('Calls')
    if stderr != '':
        return stdout[start_idx:end_idx], stderr, 1
    else:
        
        return stdout[start_idx:end_idx], stderr, 0

def get_response(prompt, prompt_cache, prompt_cache_RAG, model, redo=False, temp=0.,max_tokens=3500, stop = None, num_verifier = None, RAG = False):
    
    
    # check if in prompt_cache/prompt_cache_RAG
    if not RAG:
        if prompt in prompt_cache and not redo and num_verifier is None:
            return prompt_cache[prompt][0], prompt_cache, prompt_cache_RAG
        elif prompt in prompt_cache and not redo and len(prompt_cache[prompt]) >= num_verifier:
            return prompt_cache[prompt][num_verifier-1], prompt_cache, prompt_cache_RAG
    else:
        if prompt in prompt_cache_RAG and not redo and num_verifier is None:
            return prompt_cache_RAG[prompt][0], prompt_cache, prompt_cache_RAG
        elif prompt in prompt_cache_RAG and not redo and len(prompt_cache_RAG[prompt]) >= num_verifier:
            return prompt_cache_RAG[prompt][num_verifier-1], prompt_cache, prompt_cache_RAG

    if not RAG:
        passed = False; tries = 0 
        messages = [{'role': 'user', 'content': prompt}]
        while not passed:
            try:
                
                
                response = client.responses.create(
                    model=model,
                    input=messages
                )
                
                passed=True;tries+=1
                if prompt not in prompt_cache:
                    prompt_cache[prompt] = [response]
                else:
                    prompt_cache[prompt].append(response)
            except BaseException as e:
                print(e)
                if tries > 5:
                    breakpoint()
                    import  sys
                    sys.exit()
        return response, prompt_cache, prompt_cache_RAG
    else:
        try:
            response = get_response_RAG(prompt, model)
            if prompt not in prompt_cache_RAG:
                prompt_cache_RAG[prompt] = [response]
            else:
                prompt_cache_RAG[prompt].append(response)
        except:
            breakpoint()
                        
        return response, prompt_cache, prompt_cache_RAG

def get_response_check(prompt, prompt_cache, prompt_cache_RAG, model = 'gpt-4', temp=0,max_tokens=3500, redo=False, stop = None, num_verifier = None, RAG = False):
    
    if 'o4-' in model or 'o3-' in model:
        response, prompt_cache, prompt_cache_RAG = get_response(prompt, prompt_cache, prompt_cache_RAG, model, redo, temp=temp,max_tokens=max_tokens, stop = stop, num_verifier = num_verifier, RAG = RAG)
    elif 'gem' in model:
        response, prompt_cache, prompt_cache_RAG = get_response_gem(prompt, prompt_cache, prompt_cache_RAG, model, redo, temp=temp,max_tokens=max_tokens, stop = stop, num_verifier = num_verifier, RAG = RAG)
    elif 'deepseek' in model:
        response, prompt_cache, prompt_cache_RAG = get_response_deepseek(prompt, prompt_cache, prompt_cache_RAG, model, redo, temp=temp,max_tokens=max_tokens, stop = stop, num_verifier = num_verifier, RAG = RAG)
    if not RAG:
        pass#save_cache(prompt_cache, model)
    else:
        pass#save_cache(prompt_cache_RAG, model, RAG = RAG)
        
    return response, prompt_cache, prompt_cache_RAG

def save_cache_basic(prompt_cache, model = 'gpt-4', RAG=''):
    if not RAG:
        filename = f'prompt_cache_asp_{model}.pickle'
    else:
        filename = f'prompt_cache_asp_{model}_RAG_{RAG}.pickle'
    with open(filename, 'wb') as handle:
        pickle.dump(prompt_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)


def save_cache(prompt_cache, model = 'gpt-4', RAG=False):
    passed=False
    try_num = 0
    
    if not RAG:
        filename = f'prompt_cache_asp_{model}.pickle'
    else:
        filename = f'prompt_cache_asp_{model}_RAG_{RAG}.pickle'
    while not passed and try_num<5:
        try:
            if os.path.exists(filename):
                with open(filename, 'rb') as handle: # load in case it was updated
                    temp_prompt_cache = pickle.load(handle)
            else:
                save_cache_basic(prompt_cache, model, RAG=RAG)
                return
            passed=True
        except:
            try_num+=1
            time.sleep(random.randint(3,40))
            pass
    if passed==False:
        breakpoint()
        
    temp_prompt_cache.update(prompt_cache) # combine dicts
    prompt_cache = temp_prompt_cache
    save_cache_basic(prompt_cache, model)



from keys import VS_ID
def get_response_RAG(prompt, model = 'gpt-4'):
    
    response = client.responses.create(
        input = prompt,
        model = model,
        tools = [{
            'type': 'file_search',
            'vector_store_ids': [VS_ID],
            }],
        include = ['file_search_call.results']
        )
    
    return response


from vertexai.generative_models import GenerativeModel, Tool
from gemini_rag_utils import rag_retrieval_tool

def get_response_gemini_RAG(prompt, model):
    
    
    rag_model = GenerativeModel(
        model_name=model, tools=[rag_retrieval_tool]
    )
    
    response = rag_model.generate_content(prompt)
    return response



def parse_output(output):
    output_prog = output
    to_remove_strings = ['```asp', '```prolog', '% MODULES START', '% MODULES END', '```']
    
    for to_remove_string in to_remove_strings:
        output_prog = output_prog.replace(to_remove_string, '')#.strip()
        
    #output_prog = output.replace('% MODULES START','').replace('% MODULES END','').replace('```','').strip()
    return 'update', [output_prog]
    

def parse_test_descs(output):
    
    tests = []; test_start = False
    for line in output.split('\n'):
        if 'ACTION' in line:
            pass
        elif 'START' in line:
            test_start = True
            test = []
        elif 'END' in line:
            tests.append(test)
            test_start = False
        elif test_start:
            test.append(line)
        else:
            pass
    tests = ['\n'.join(test) for test in tests]
    return tests


def extract_between_last_backticks(text: str):
    if '```' not in text:
        return text
    occurrences = [m.start() for m in re.finditer(r"```", text)]

    # Check if there are at least two occurrences
    if len(occurrences) < 2:
        #breakpoint()
        #print("Error: Fewer than two occurrences of '```' were found.")
        return text

    # Get the start index of the second-to-last "```"
    # We add 3 to move the index past the backticks themselves.
    start_index = occurrences[-2] + 3

    # Get the start index of the last "```"
    end_index = occurrences[-1]

    # Extract and return the substring between these two points.
    # We also strip leading/trailing whitespace which often includes a newline.
    return text[start_index:end_index].strip()



def parse_output_no_verifier(output):
    no_operation = True
    for line in output.split('\n'):
        if 'OPERATION' in line:
            no_operation = False
            break
    if no_operation:
        output_prog = extract_between_last_backticks(output).replace('% MODULES START','').replace('% MODULES END','').replace('asp\n', '').replace('```','').strip()
        return 'update', [output_prog]
    if 'update' in line.lower():
        
        output_prog = extract_between_last_backticks(output).replace(line,'').replace('% MODULES START','').replace('% MODULES END','').replace('```','').strip()
        return 'update', [output_prog]
    elif 'test' in line.lower():
        
        output = output.replace(line,'')#.replace('% MODULES START','').replace('% MODULES END','').replace('```','').strip()
        #prob_desc = output_prog.split('% PROBLEM DESCRIPTION END')[0].split('% PROBLEM DESCRIPTION START')[1].strip()
        #output_prog = output_prog[output_prog.index('% PROBLEM DESCRIPTION END')+25:]
        test_prob_descs = parse_test_descs(output)
        return 'test', test_prob_descs
    elif 'pass' in line.lower():
        return 'pass', ['']


def write_intermediate(log, pos, pos_label, output_dir, num_write, RAG=False):
    update_levels = pos[0::2]
    test_levels = pos[1::2]
    
    u_nodes = ['u' + str(u) for u in update_levels]
    t_nodes = ['t' + str(t) for t in test_levels]
    node = []
    for pair in zip(u_nodes,t_nodes):
        node+=pair
    
    if len(u_nodes)>len(t_nodes):
        node+=u_nodes[-1:]
    
    if pos[-1] == 0:
        node=node[:-1]
    
    pos_list = []
    for step, label in zip(pos, pos_label):
        pos_list.append((label+str(step)) if label!='p' else 'p')
    if pos[-1] == 0:
        pos_list=pos_list[:-1]
    
    for text, levels, step_name, inp_out in log:
        levels_str = '.'.join(pos_list)
        path = os.path.join(output_dir,f'{num_write}_{levels_str + ("_" if levels_str else "")}{step_name}{"_" + inp_out if inp_out else ""}{"_" + "RAG" if (inp_out=="output" and RAG) else ""}' + '.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
    
    return

def get_error_lines(current_modules, stderr):
    
    error_lines = []    
    current_modules_split = current_modules.split('\n')
    for line in stderr.split('\n'):
        if 'error:' in line:
            inds = [i for i, ltr in enumerate(line) if ltr == ':']
            line_num = line[inds[0]+1:inds[1]]
            line_num_0idx = int(line_num)-1
            line_to_show = current_modules_split[line_num_0idx] if line_num_0idx < len(current_modules_split) else "unexpected EOF"
            error_line = f'LINE {line_num}: ' + line_to_show
            
            error_lines.append(error_line)
    return error_lines


def get_response_gem(prompt, prompt_cache, prompt_cache_RAG, model, redo=False, temp=0.,max_tokens=3500, stop = None, num_verifier = None, RAG = False):
    if not RAG:
        if prompt in prompt_cache and not redo and num_verifier is None:
            return prompt_cache[prompt][0], prompt_cache, prompt_cache_RAG
        elif prompt in prompt_cache and not redo and len(prompt_cache[prompt]) >= num_verifier:
            return prompt_cache[prompt][num_verifier-1], prompt_cache, prompt_cache_RAG
    else:
        if prompt in prompt_cache_RAG and not redo and num_verifier is None:
            return prompt_cache_RAG[prompt][0], prompt_cache, prompt_cache_RAG
        elif prompt in prompt_cache_RAG and not redo and len(prompt_cache_RAG[prompt]) >= num_verifier:
            return prompt_cache_RAG[prompt][num_verifier-1], prompt_cache, prompt_cache_RAG

    if not RAG:
        passed = False; tries = 0 
        messages = [{'role': 'user', 'content': prompt}]
        while not passed:
            try:
                
                tries+=1
                response = client_gem.models.generate_content(
                    model=model, contents=prompt
                )
                if response.text is None:
                    print('gemini returned no text')
                    continue
                passed=True;tries+=1
                if prompt not in prompt_cache:
                    prompt_cache[prompt] = [response]
                else:
                    prompt_cache[prompt].append(response)
            except BaseException as e:
                if tries > 5:
                    breakpoint()
                    import  sys
                    sys.exit()
        return response, prompt_cache, prompt_cache_RAG
    else:
        try:
            response = get_response_gemini_RAG(prompt, model)
            if prompt not in prompt_cache_RAG:
                prompt_cache_RAG[prompt] = [response]
            else:
                prompt_cache_RAG[prompt].append(response)
        except:
            breakpoint()
        return response, prompt_cache, prompt_cache_RAG

def get_response_deepseek(prompt, prompt_cache, prompt_cache_RAG, model, redo=False, temp=0.,max_tokens=3500, stop = None, num_verifier = None, RAG = False):
    
    if not RAG:
        if prompt in prompt_cache and not redo and num_verifier is None:
            return prompt_cache[prompt][0], prompt_cache, prompt_cache_RAG
        elif prompt in prompt_cache and not redo and len(prompt_cache[prompt]) >= num_verifier:
            return prompt_cache[prompt][num_verifier-1], prompt_cache, prompt_cache_RAG
    else:
        if prompt in prompt_cache_RAG and not redo and num_verifier is None:
            return prompt_cache_RAG[prompt][0], prompt_cache, prompt_cache_RAG
        elif prompt in prompt_cache_RAG and not redo and len(prompt_cache_RAG[prompt]) >= num_verifier:
            return prompt_cache_RAG[prompt][num_verifier-1], prompt_cache, prompt_cache_RAG

    if not RAG:
        passed = False; tries = 0 
        messages = [{'role': 'user', 'content': prompt}]
        while not passed:
            try:
                
                tries+=1
                response = client_deepseek.chat.completions.create(
                    model=model,
                    messages=messages
                )
                if response.choices[0].message.content is None:
                    print('deepseek returned no text')
                    continue
                passed=True;tries+=1
                if prompt not in prompt_cache:
                    prompt_cache[prompt] = [response]
                else:
                    prompt_cache[prompt].append(response)
            except BaseException as e:
                if tries > 5:
                    breakpoint()
                    import  sys
                    sys.exit()
        return response, prompt_cache, prompt_cache_RAG


def write_stats(token_usage, correct, output_dir):
    token_types = ['main', 'verifier', 'formatter', 'evaluator'] if token_usage['evaluator'] else ['main', 'verifier', 'formatter']
    tokens_by_type = {tok_type: {tok_type: 0 for tok_type in ['thought_tokens', 'total_tokens', 'prompt_tokens', 'candidates_tokens']} for tok_type in token_types}
    
    
    for token_type in token_types:
        for token_stats in token_usage[token_type]:
            thought_toks = token_stats.thoughts_token_count
            total_toks = token_stats.total_token_count
            prompt_toks = token_stats.prompt_token_count
            candidate_toks = token_stats.candidates_token_count
            
            tokens_by_type[token_type]['thought_tokens']+=thought_toks
            tokens_by_type[token_type]['total_tokens']+=total_toks
            tokens_by_type[token_type]['prompt_tokens']+=prompt_toks
            tokens_by_type[token_type]['candidates_tokens']+=candidate_toks
    
    if correct != 'unknown':
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type, 'correct': correct }
    else:
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type}
    
    with open(os.path.join(output_dir,'stats.txt'), 'w') as f:
        json.dump(stats, f)


def write_stats_openai(token_usage, correct, output_dir):
    token_types = ['main', 'verifier', 'formatter'] if token_usage['evaluator'] else ['main', 'verifier', 'formatter']
    tokens_by_type = {tok_type: {tok_type: 0 for tok_type in ['thought_tokens', 'total_tokens', 'prompt_tokens']} for tok_type in token_types}
    
    for token_type in token_types:
        for token_stats in token_usage[token_type]:
            thought_toks = token_stats.output_tokens_details.reasoning_tokens
            output_toks = token_stats.output_tokens
            prompt_toks = token_stats.input_tokens
            
            tokens_by_type[token_type]['thought_tokens']+=thought_toks
            tokens_by_type[token_type]['total_tokens']+=thought_toks + output_toks + prompt_toks
            tokens_by_type[token_type]['prompt_tokens']+=prompt_toks
        
    if correct != 'unknown':
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type, 'correct': correct }
    else:
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type}
    
    with open(os.path.join(output_dir,'stats.txt'), 'w') as f:
        json.dump(stats, f)

def write_stats_deepseek(token_usage, correct, output_dir):
    token_types = ['main', 'verifier', 'formatter'] if token_usage['evaluator'] else ['main', 'verifier', 'formatter']
    tokens_by_type = {tok_type: {tok_type: 0 for tok_type in ['thought_tokens', 'total_tokens', 'prompt_tokens']} for tok_type in token_types}
    
    
    for token_type in token_types:
        for token_stats in token_usage[token_type]:
            thought_toks = token_stats.completion_tokens_details.reasoning_tokens
            output_toks = token_stats.completion_tokens
            prompt_toks = token_stats.prompt_tokens
            
            tokens_by_type[token_type]['thought_tokens']+=thought_toks
            tokens_by_type[token_type]['total_tokens']+=thought_toks + output_toks + prompt_toks
            tokens_by_type[token_type]['prompt_tokens']+=prompt_toks
    
    if correct != 'unknown':
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type, 'correct': correct }
    else:
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type}
    
    with open(os.path.join(output_dir,'stats.txt'), 'w') as f:
        json.dump(stats, f)

def write_stats_deepseek_chat(token_usage, correct, output_dir):
    token_types = ['main', 'verifier', 'formatter'] if token_usage['evaluator'] else ['main', 'verifier', 'formatter']
    tokens_by_type = {tok_type: {tok_type: 0 for tok_type in ['thought_tokens', 'total_tokens', 'prompt_tokens']} for tok_type in token_types}
    
    for token_type in token_types:
        for token_stats in token_usage[token_type]:
            output_toks = token_stats.completion_tokens
            prompt_toks = token_stats.prompt_tokens
            
            tokens_by_type[token_type]['total_tokens']+= output_toks + prompt_toks
            tokens_by_type[token_type]['prompt_tokens']+=prompt_toks
        
    
    if correct != 'unknown':
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type, 'correct': correct }
    else:
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type}
    
    with open(os.path.join(output_dir,'stats.txt'), 'w') as f:
        json.dump(stats, f)

def write_stats_baseline(token_usage, correct, output_dir):
    token_types = ['main', 'evaluator']
    tokens_by_type = {tok_type: {tok_type: 0 for tok_type in ['thought_tokens', 'total_tokens', 'prompt_tokens', 'candidates_tokens']} for tok_type in token_types}
    
    for token_type in token_types:
        for token_stats in token_usage[token_type]:
            thought_toks = token_stats.thoughts_token_count
            total_toks = token_stats.total_token_count
            prompt_toks = token_stats.prompt_token_count
            candidate_toks = token_stats.candidates_token_count
            
            tokens_by_type[token_type]['thought_tokens']+=(0 if (thought_toks == None) else thought_toks)
            tokens_by_type[token_type]['total_tokens']+=total_toks
            tokens_by_type[token_type]['prompt_tokens']+=prompt_toks
            tokens_by_type[token_type]['candidates_tokens']+=candidate_toks
    
    if correct != 'unknown':
        stats = {'token_usage': tokens_by_type, 'correct': correct }
    else:
        stats = {'token_usage': tokens_by_type}
    
    with open(os.path.join(output_dir,'stats.txt'), 'w') as f:
        json.dump(stats, f)


def write_stats_baseline_openai(token_usage, correct, output_dir):
    token_types = ['main', 'evaluator'] if token_usage['evaluator'] else ['main']
    tokens_by_type = {tok_type: {tok_type: 0 for tok_type in ['thought_tokens', 'total_tokens', 'prompt_tokens']} for tok_type in token_types}
    
    for token_type in token_types:
        for token_stats in token_usage[token_type]:
            thought_toks = token_stats.output_tokens_details.reasoning_tokens
            output_toks = token_stats.output_tokens
            prompt_toks = token_stats.input_tokens
            total_toks = token_stats.total_tokens
            
            tokens_by_type[token_type]['thought_tokens']+=thought_toks
            tokens_by_type[token_type]['total_tokens']+=total_toks
            tokens_by_type[token_type]['prompt_tokens']+=prompt_toks
    
    if correct != 'unknown':
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type, 'correct': correct }
    else:
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type}
    
    with open(os.path.join(output_dir,'stats.txt'), 'w') as f:
        json.dump(stats, f)

def write_stats_baseline_deepseek(token_usage, correct, output_dir):
    token_types = ['main', 'evaluator'] if token_usage['evaluator'] else ['main']
    tokens_by_type = {tok_type: {tok_type: 0 for tok_type in ['thought_tokens', 'total_tokens', 'prompt_tokens']} for tok_type in token_types}
    
    for token_type in token_types:
        for token_stats in token_usage[token_type]:
            thought_toks = token_stats.completion_tokens_details.reasoning_tokens
            output_toks = token_stats.completion_tokens # doesn't include reasoning tokens
            prompt_toks = token_stats.prompt_tokens
            total_tokens = token_stats.total_tokens
            
            tokens_by_type[token_type]['thought_tokens']+=thought_toks
            tokens_by_type[token_type]['total_tokens']+=total_tokens
            tokens_by_type[token_type]['prompt_tokens']+=prompt_toks
    
    if correct != 'unknown':
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type, 'correct': correct }
    else:
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type}
    
    with open(os.path.join(output_dir,'stats.txt'), 'w') as f:
        json.dump(stats, f)

def write_stats_baseline_deepseek_chat(token_usage, correct, output_dir):
    token_types = ['main', 'evaluator'] if token_usage['evaluator'] else ['main']
    tokens_by_type = {tok_type: {tok_type: 0 for tok_type in ['thought_tokens', 'total_tokens', 'prompt_tokens']} for tok_type in token_types}
    
    for token_type in token_types:
        for token_stats in token_usage[token_type]:
            output_toks = token_stats.completion_tokens # doesn't include reasoning tokens
            prompt_toks = token_stats.prompt_tokens
            total_tokens = token_stats.total_tokens
            
            tokens_by_type[token_type]['total_tokens']+= total_tokens
            tokens_by_type[token_type]['prompt_tokens']+=prompt_toks
    
    if correct != 'unknown':
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type, 'correct': correct }
    else:
        stats = {'revisions': len(token_usage['main'])-1, 'token_usage': tokens_by_type}
    
    with open(os.path.join(output_dir,'stats.txt'), 'w') as f:
        json.dump(stats, f)