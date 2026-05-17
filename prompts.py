checklist = ''


debugger_prompt_resource_v2_2 = '''<RESOURCE_PROMPT>

<instructions>
You are tasked with constructing an ASP program to solve the following problem:
<problem-description>
<PROBLEM>
</problem-description>
The ASP program should be made of ASP modules, which each make up a necessary part of the program to represent the problem.
In the program, include the #show command for atoms which will help for verifying the answer and/or debugging. For example, don't just show the final answer, but show atoms which can be used to check that the parts determining the final answer are also correct.

<TEST_CASE><CURRENT MODULES><CANDIDATE_FEEDBACK><VERIFIER_FEEDBACK>

<AVAILABLE ACTIONS>
</instructions>'''.replace('<CHECKLIST>', checklist)


current_modules_prompt = '''<current-clingo-modules>
Here are the current ASP modules:
<CURRENT MODULES>
</current-clingo-modules>'''

candidate_feedback_prompt = '''<candidate-answer-set>
Here is the candidate answer set to solve the problem, from running the ASP program:
<CURRENT OUTPUT>
</candidate-answer-set>'''


candidate_feedback_prompt_both = '''<candidate-answer-sets>
<run-1>
Here is the candidate answer set when running from running the ASP program  with {:- test_query}:
<CURRENT OUTPUT1>
</run-1>

<run-2>
Here is the candidate answer set when running from running the ASP program  with {:- -test_query}:
<CURRENT OUTPUT2>
</run-2>
</candidate-answer-sets>'''



verifier_feedback_prompt = '''<verifier-feedback>
Here is feedback from verifiers, which analyzed the candidate answer set.
<FEEDBACK>
</verifier-feedback>'''

resource_prompt = '''Consider the following resource material describing Answer Set Programming and the language of Clingo to do the following task.
<resource-material>
<RESOURCE>
</resource-material>
'''


pre_a1 = '''(UPDATE) - This should be done either to:
	(a) write an initial ASP program (still considered an update).
	(b) update the program based on the Clingo output and verifiers which may help to debug the current output.'''


pre_a1_no_ver = '''(UPDATE) - This should be done either to:
	(a) write an initial ASP program (still considered an update).
	(b) update the program based on the Clingo output which may help to debug the current output.'''


pre_a1_no_ver_full_prog = '''(UPDATE) - This should be done either to:
	(a) write an initial ASP program (still considered an update).
	(b) update the program based on the Clingo output which may help to debug the current output.
If updated, make sure to write the complete program.'''
    
pre_a1_ver = '''(UPDATE) - This should be done to update the program based on the Clingo output and verifiers which may help to debug the current output.'''



pre_a2 = '''(TEST) - This option is for generating or updating test cases, which help make sure that the program correctly captures what is intended by the problem. The test cases will later be run by Clingo, and the output will be checked. This can also help debug issues with the program. For example:
    In an action domain, this action can be used to test cases can be helpful to check whether preconditions are correctly implemented, states update correctly based on actions, etc.
    In a static domain (a domain which does not have actions over time), test cases can make sure that the constraints intended in the problem description are enforced, etc.'''



pre_a3 = '''(PASS) - This should be done when the Clingo output is correct. There should be no ambiguity and consensus on the proposed solution being correct. ONLY use when absolutely sure the output is correct. If the proposed solution is correct, you may ignore stderr and still pass.'''

instr_a1 = '''For UPDATE, format your output exactly like the following:

```
% MODULES START
% module <name of first module>
<ASP code for this module>
% module <name of first module> END

% module <name of second module>
<ASP code for this module>
% module <name of second module> END
...
% MODULES END
```'''

instr_a1_full_prog = '''For UPDATE, format your output exactly like the following, writing the complete program:

```
% MODULES START
% module <name of first module>
<ASP code for this module>
% module <name of first module> END

% module <name of second module>
<ASP code for this module>
% module <name of second module> END
...
% MODULES END
```'''

instr_a2 = '''For TEST, write a brief but sufficient description of the problem and it's purpose relative to the original program (e.g., it is testing if updating a rule changes the output to be correct, a simpler query with a known solution can work etc.). Create as many test cases as needed. Format your output exactly like the following:

```
% PROBLEM DESCRIPTION START #1
...
% PROBLEM DESCRIPTION END #1

% PROBLEM DESCRIPTION START #2
...
% PROBLEM DESCRIPTION END #2
...
% PROBLEM DESCRIPTION START #n
...
% PROBLEM DESCRIPTION END #n
```'''

instr_a3 = '''For PASS, format your output exactly like the following (only write the action, since nothing else is to be done):

```
OPERATION: PASS
```'''

'''
You have <NUM ACTIONS> available actions. If you run into an issue that does not have a clear, pinpointed, and actionable solution, then take the test action (option 2). Do not update to try to see if something works, that is what a test case is for.
'''
actions_desc = [
    [pre_a1, instr_a1],
    [pre_a2, instr_a2],
    [pre_a3, instr_a3]
    ]


actions_desc_ver = [
    [pre_a1_ver, instr_a1],
    [pre_a2, instr_a2],
    [pre_a3, instr_a3]
    ]

actions_desc_no_ver = [
    [pre_a1_no_ver, instr_a1],
    [pre_a2, instr_a2],
    [pre_a3, instr_a3]
    ]

actions_desc_no_ver_full_prog = [
    [pre_a1_no_ver_full_prog, instr_a1_full_prog],
    [pre_a2, instr_a2],
    [pre_a3, instr_a3]
    ]


def writeActions(a_bool):
    num_actions = sum(a_bool)
    num_actions_string = 'You are tasked with doing the UPDATE operation, described as follows.'.replace('<NUM ACTIONS>',str(num_actions))
    pre, instr = [], []
    
    for a_idx,a in enumerate(a_bool):
        if not a:
            continue
        pre.append(actions_desc[a_idx][0])
        instr.append(actions_desc[a_idx][1])
    
    pre_str = '\n'.join(pre)
    instr_str = '\n'.join(instr)
    
    full_str = num_actions_string + '\n' + pre_str + '\n\n' + instr_str + '\n\nDo not write anything outside of the three backticks.'
    
    return full_str


def writeActions_no_ver(a_bool):
    num_actions = sum(a_bool)
    num_actions_string = 'You are tasked with doing the an operation from the following.'.replace('<NUM ACTIONS>',str(num_actions))
    pre, instr = [], []
    
    for a_idx,a in enumerate(a_bool):
        if not a:
            continue
        pre.append(actions_desc_no_ver_full_prog[a_idx][0])
        instr.append(actions_desc_no_ver_full_prog[a_idx][1])
    
    pre_str = '\n'.join(pre)
    instr_str = '\n'.join(instr)
    
    full_str = num_actions_string + '\n' + pre_str + '\n\n' + instr_str + '\n\nDo not write anything outside of the three backticks.'
    
    return full_str


def writeActions_ver(a_bool):
    num_actions = sum(a_bool)
    num_actions_string = 'Summarize your findings in a single block, encapsulated by three backticks (```), including anything that seems wrong. Specify the module(s) you are commenting on. This feedback will potentially be used to adjust anything in the ASP program. If the proposed solution is correct, you may ignore stderr and pass. At the end of the block you will vote for one of the available actions by writing "[VOTE: UPDATE]" or "[VOTE: PASS]:'.replace('<NUM ACTIONS>',str(num_actions))
    pre = []
    
    for a_idx,a in enumerate(a_bool):
        if not a:
            continue
        pre.append(actions_desc_ver[a_idx][0])
    
    pre_str = '\n'.join(pre)
    
    full_str = num_actions_string + '\n' + pre_str
    
    return full_str



actions_desc_v3 = [
    [pre_a1, instr_a1],
    [pre_a2, instr_a2],
    [pre_a3, instr_a3]
    ]

