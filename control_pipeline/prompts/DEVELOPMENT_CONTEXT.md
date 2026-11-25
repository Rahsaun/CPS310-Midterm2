# Major design and argument instructions

This record preserves the assignment instructions and the major user requests that guided development in the ChatGPT conversation. It was assembled retrospectively from the visible conversation when the user requested a completeness review. It records selected major instructions, rather than presenting a reconstructed full conversation as an original model-call log. The generation prompts and raw JSON responses are saved separately with the demonstration evidence.

## Assignment prompt supplied in the user's image

> Please design and implement a process control pipeline for the AI-driven development of your Zombie Game Simulation Framework using ontology.
>
> You must explicitly state your pipeline, including every step. And, you must explicitly explain the design of your pipeline.
>
> You must rigorously argue what aspects of development are controlled and improved using your pipeline, and why those controls are effective, including the comparisons with naive AI-driven development without those controls.
>
> All major prompts must be explicitly provided.
>
> Demos of your pipeline, with concrete outcomes, are required. (You can simplify your Zombie Game design, yet keeping it non-trivial, when addressing the demos. Free-tier AI models are fine. No subscription is needed.)
>
> If free-tier AI models run into limits, please let Fanchao know immediately, and Fanchao will help with it.
>
> If no AI models are accessible at all, please let Fanchao know immediately, and demos can be skipped with Fanchao's permission.
>
> For submissions, documents and prompts for your design and arguments are required. Demos and intermediate results (especially the ontologies) are required to be uploaded to GitHub, if available.

## Major user requests

The following excerpts preserve the user's wording. They were instructions to the assistant in the existing conversation.

**Implementation request**

> okay....so i need you to answer the problem that i gave you

**Design, argument and demo review request**

> im gonna give you some more task 1.change the repo title to CPS310-Midterm2          2.make sure tthat i have concrete arguements. 3. make sure theres instructions to run all demos 4. makde sure youstate my pipline inlucing each step for it and the explain the overall design of thje pipeline

**Completeness review request**

> now that youve did these chnages i need you to look over theese questions and ask yoursweld did you truly meet all the reqiurments ?

**Correction request**

> so are you able to fix theese things or is it not possible?

## Scope decisions made during development

The assistant selected structured scenario generation as the bounded development task. A fixed Python template turns AI-supplied JSON into executable code, and the ontology controls the accepted domain values. The supplied game provides movement, combat, conversion and strategy behavior. The report explains these design decisions and ties the arguments to saved results.

No separate design-agent or argument-agent invocation was performed. The design and argument were produced in the same ongoing assistant conversation in response to the instructions above. The fresh comparison responses also share that conversation context. This context includes knowledge of the game and ontology, including for the naive-prompt response.

## Operational prompt locations

- `controlled.txt` defines the controlled generation instructions.
- `naive.txt` defines the baseline generation instructions.
- `repair.txt` defines the correction instructions.
- `evidence/pipeline/session_2/context/` contains complete prompts with the task and ontology attached.
- `evidence/pipeline/session_2/injected_rejection/repair_prompt.txt` contains the complete feedback prompt used for the fresh correction response.
- `control_pipeline/examples/session_*_response.json` contains the newly authored responses.

The injected faulty response is a deliberate mutation of a valid candidate. It is labeled as a fault fixture throughout the evidence. The subsequent correction response was authored after the assistant read the generated feedback.
