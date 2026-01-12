QUALITY_FEW_SHOT_COT_PROMPT = """## Example 1
### Question
In the context of "Les Misérables", written by Victor Hugo in 1862, what is the main setting of the novel? There is only one correct choice.
### Choices
A. London
B. Madrid
C. Paris
D. Rome
### Thought Process and Answer
Thought process: "Les Misérables" is primarily set in Paris, making C the correct choice. London, Madrid, and Rome are significant cities in other literary works but not in Victor Hugo's "Les Misérables". There is only one correct choice.
Answer: C.

## Example 2
### Question
In the context of "Brave New World", written by Aldous Huxley in 1932, what substance is widely used in the society to control citizens' happiness? There is only one correct choice.
### Choices
A. Gold
B. Soma
C. Silver
D. Iron
### Thought Process and Answer
Thought process: In Aldous Huxley's "Brave New World," Soma is used as a means to maintain social control by ensuring citizens' happiness, making B the correct choice. Gold, Silver, and Iron are not the substances used for this purpose in the book.
Answer: B.

## Example 3
### Question
In the context of "Romeo and Juliet", written by William Shakespeare in the early 1590s, what are the names of the two feuding families? There is only one correct choice.
Choices:
A. Montague and Capulet
B. Bennet and Darcy
C. Linton and Earnshaw
D. Bloom and Dedalus
### Thought Process and Answer
Thought process: In William Shakespeare's "Romeo and Juliet," the two feuding families are the Montagues and the Capulets, making A the correct choice. The Bennets and Darcys are in "Pride and Prejudice", the Lintons and Earnshaws in "Wuthering Heights", and Bloom and Dedalus in "Ulysses".
Answer: A.

## Example 4
### Question
In the context of "1984", written by George Orwell in 1949, what is the name of the totalitarian leader? There is only one correct choice.
### Choices
A. Big Brother
B. O'Brien
C. Winston Smith
D. Emmanuel Goldstein
### Thought Process and Answer
Thought process: In George Orwell's "1984," the totalitarian leader is known as Big Brother, making A the correct choice. O'Brien is a character in the novel, Winston Smith is the protagonist, and Emmanuel Goldstein is a rebel leader.
Answer: A.

## Example 5
### Question
In the context of "Moby-Dick", written by Herman Melville in 1851, what is the name of the ship's captain obsessed with hunting the titular whale? There is only one correct choice.
### Choices
A. Captain Hook
B. Captain Nemo
C. Captain Flint
D. Captain Ahab
### Thought Process and Answer
Thought process: In Herman Melville's "Moby-Dick," the ship's captain obsessed with hunting the whale is Captain Ahab, making D the correct choice. Captain Nemo is in "Twenty Thousand Leagues Under the Sea", Captain Flint in "Treasure Island", and Captain Hook in "Peter Pan".
Answer: D.

## Example 6
"""

OPENAI_API_SYSTEM_QUALITY_GENERATE_ENTITIES = """
As a knowledge analyzer, your task is to dissect and understand an article provided by the user. You are required to perform the following steps:
1. Summarize the Article: Provide a concise summary of the entire article, capturing the main points and themes.
2. Extract Entities: Identify and list all significant "nouns" or entities mentioned within the article. These entities should include but not limited to:
    * People: Any individuals mentioned in the article, using the names or references provided.
    * Places: Both specific locations and abstract spaces relevant to the content.
    * Object: Any concrete object that is referenced by the provided content.
    * Concepts: Any significant abstract ideas or themes that are central to the article's discussion.

Try to exhaust as many entities as possible. Your response should be structured in a JSON format to organize the information effectively. Ensure that the summary is brief yet comprehensive, and the list of entities is detailed and accurate.

Here is the format you should use for your response:

{
  "summary":  "<A concise summary of the article>",
  "entities": ["entity1", "entity2", ...]
}
"""

OPENAI_API_SYSTEM_QUALITY_GENERATE_ENTITY_SPECIFIC_QUESTIONS = """
As an examiner, you are tasked with creating reading comprehension questions for students based on a provided article and a specified entity referenced within it. Your role involves crafting questions and corresponding answers that fulfill the following criteria:

1. **Focus on the Entity**: Ensure all questions consistently center around the specified entity from the article.
2. **Encourage Deep Analysis**: Develop thought-provoking, open-ended questions that challenge students to think critically and analytically. Questions should:
   - Prompt students to reflect deeply, questioning the assumptions within the article.
   - Require students to evaluate evidence and consider alternative perspectives.
   - Encourage complex reasoning about the entity and its implications within the article's context.
3. **Comprehensive Answers**: For each question, provide a detailed solution that:
   - Explicitly connects back to the specified entity and its role or representation in the article.
   - Includes concrete references to specific paragraphs or sections of the article to support the answer.

Try to write as many questions as possible. Your response should be formatted to organize the questions and answers systematically. Here is the structure you should use:

### Questions and answers about <entity> in context of <title>
Question: <Question1 focusing on the entity>
Answer: <Detailed answer with references to the article>

Question: <Question2 focusing on the entity>
Answer: <Detailed answer with references to the article>
  ...

"""

OPENAI_API_SYSTEM_QUALITY_GENERATE_TWO_ENTITIES_CONNECTION_SCORE = """
You will act as a knowledge analyzer tasked with evaluating the strength of the association between two specified entities (E1 and E2) within an article. Your evaluation will be based on three criteria:
1. Causality: Assess whether there is a cause-and-effect relationship between E1 and E2. Describe these relationships in two ways:
	* When E1 causes changes or influences E2.
	* When E2 causes changes or influences E1.
2. Dependence: Evaluate how one entity depends on or is influenced by the other, within the context of the article.
	* Discuss how E1 depends on or is influenced by E2.
	* Discuss how E2 depends on or is influenced by E1.
3. Indirect Association: Identify any indirect links between E1 and E2 through other entities when no direct connection is present.
	* List all other entities in the article that have connections to both E1 and E2.
	* Describe how entities bridge the connection between E1 and E2
	* Identify relation type between the intermediate entity and two specified entities.

After analyzing these three criteria, assign a connection strength score between 0 and 1 based on their tightness in the article’s context. The score should reflect the overall strength of the association between E1 and E2.
Your response should follow this format to ensure clarity and organization:

### Causality between <E1> and <E2> in the context of <article title>
E1 influencing E2: <Describe the cause-and-effect relationship from E1 to E2>.
E2 influencing E1: <Describe the cause-and-effect relationship from E2 to E1>.
### Dependence between <E1> and <E2> in the context of <article title>
E1 depending on E2: <Describe how E1 relies on E2>.
E2 depending on E1: <Describe how E2 relies on E1>.
### Indirect association between <E1> and <E2> in the context of <article title>
Intermediate entities: <List and describe any entities that serve as intermediaries between E1 and E2>.
Connection through intermediaries: <Discuss how these entities link E1 and E2>.

Score: <Assign a score between 0 and 1 based on the strength of the connection>.
"""

OPENAI_API_SYSTEM_QUALITY_GENERATE_TWO_ENTITY_RELATIONS = """
You will act as a knowledge analyzer tasked with dissecting an article provided by the user. Your role involves two main objectives:
1. Rephrasing Content: The user will identify two specific entities mentioned in the article. You are required to rephrase the content of the article twice:
    * Once, emphasizing the first entity.
    * Again, emphasizing the second entity.
2. Analyzing Interactions: Discuss how the two specified entities interact within the context of the article.
3. Generating qeustions and answers: crafting questions and corresponding answers that fulfill the following criteria:
    - **Focus on the two Concepts/Terms**: Ensure all questions consistently center around the two concepts provided by the user.
    - **Encourage Deep Analysis**: Develop thought-provoking, open-ended questions that challenge students to think critically and analytically understand how the interaction between the two entities shape the article.

Your responses should provide clear segregation between the rephrased content and the interaction analysis. Ensure each section of the output include sufficient context, ideally referencing the article's title to maintain clarity about the discussion's focus.
Here is the format you should follow for your response:

### Discussion of <title> in relation to <entity1>
<Rephrased content focusing on the first entity>

### Discussion of <title> in relation to <entity2>
<Rephrased content focusing on the second entity>

### Discussion of Interaction between <entity1> and <entity2> in context of <title>
<Discussion on how the two entities interact within the article>

### Questions and answers about <entity1> and <entity2> in context of <title>
Question: <Question1 focusing on the two entities>
Answer: <Detailed answer with references to the article>

Question: <Question2 focusing on the two entities>
Answer: <Detailed answer with references to the article>

...
"""

OPENAI_API_SYSTEM_QUALITY_GENERATE_THREE_ENTITY_RELATIONS = """
You will act as a knowledge analyzer tasked with dissecting an article provided by the user. Your role involves three main objectives:
1. Rephrasing Content: The user will identify three specific entities mentioned in the article. You are required to rephrase the content of the article three times:
    * Once, emphasizing the first entity.
    * Again, emphasizing the second entity.
    * Lastly, emphasizing the third entity.
2. Analyzing Interactions: Discuss how these three specified entities interact within the context of the article.
3. Asking Questions: Generate some questions that involves all three entities and their interactions. Ensure your questions satisfies the following criteria:
    * Focus on the entities: Ensure all questions consistently center around the three entities specified.
    * Encourage Deep Analysis: Develop thought-provoking, open-ended questions that challenge students to think critically and analytically about the entities. Questions should:
        - Prompt students to reflect deeply on the meaning and implications of all three concepts.
        - Encourage complex reasoning about the concept’s broader implications in the context of the article.
Your responses should provide clear segregation between the rephrased content and the interaction analysis. Ensure each section of the output include sufficient context, ideally referencing the article's title to maintain clarity about the discussion's focus.
Here is the format you should follow for your response:

### Discussion of <title> in relation to <entity1>
<Rephrased content focusing on the first entity>

### Discussion of <title> in relation to <entity2>
<Rephrased content focusing on the second entity>

### Discussion of <title> in relation to <entity3>
<Rephrased content focusing on the third entity>

### Discussion of Interaction between <entity1>, <entity2> and <entity3> in context of <title>
<Discussion on how the three entities interact within the article>

### Question involving <entity1>, <entity2> and <entity3> in context of <title>
<Question1 that involves all three entities and their interactions>
<Answer to the Question1>

<Question2 that involves all three entities and their interactions>
<Answer to the Question2>

...
"""

QUALITY_CHECK_ENTITY_LIST_PROMPT = """
As an entity analyst, your task is to select the correct and complete personally identifiable entities that appear in the article from the list of candidate entities provided by the user.

Your response should be organized in JSON format to ensure clarity of information. Ensure that the summary is concise and comprehensive, and that the entity list is accurate. You only select from the original list of entities, without adding any new ones.

The following format should be used:

{
  "summary": "<Summary of the entity list analysis>",
  "correct_entities": ["Entity1", "Entity2", ...]
}
"""

RAG_QUALITY_PROMPT1 = """
## Example 1

### Instructions
Answer the following question using the 1 supporting context below.

*Context 1*
Title: Les Misérables Overview
Author: Sarah Jane
Year Written: 2019

Les Misérables, the renowned novel by Victor Hugo, is set mainly in Paris. The story follows various characters in the tumultuous period of early 19th century France, with iconic scenes taking place in the streets and neighborhoods of Paris.

### Question
In the context of "Les Misérables", written by Victor Hugo in 1862, what is the main setting of the novel? There is only one correct choice.

### Choices
A. London
B. Madrid
C. Paris
D. Rome

### Thought Process and Answer
Thought process: "Les Misérables" is primarily set in Paris, making C the correct choice. London, Madrid, and Rome are significant cities in other literary works but not in Victor Hugo's "Les Misérables".
Answer: C.

## Example 2

### Instructions
Answer the following question using the 2 supporting contexts below.

*Context 1*
Title: Soma: The Happiness Drug in Brave New World
Author: James Anderson
Year Written: 2018

In Aldous Huxley's 'Brave New World,' Soma is a powerful tool used by the state to ensure the happiness and compliance of its citizens. This drug provides an escape from any discomfort or dissatisfaction, thus maintaining societal stability.

*Context 2*
Title: The Role of Soma in Brave New World
Author: Catherine Evans
Year Written: 2020

Soma is the cornerstone of the government's control over the population in Huxley's dystopian society. By offering a chemically-induced form of happiness, the state effectively prevents any dissent or unrest among its citizens.

### Question
In the context of "Brave New World", written by Aldous Huxley in 1932, what substance is widely used in the society to control citizens' happiness? There is only one correct choice.

### Choices
A. Gold
B. Soma
C. Silver
D. Iron

### Thought Process and Answer
Thought process: In Aldous Huxley's "Brave New World," Soma is used as a means to maintain social control by ensuring citizens' happiness, making B the correct choice. Gold, Silver, and Iron are not the substances used for this purpose in the book.
Answer: B.

## Example 3

### Instructions
Answer the following question using the 3 supporting contexts below.

*Context 1*
Title: Romeo and Juliet - Analysis of Feuding Families
Author: Jane Smith
Year Written: 2019

The central conflict in "Romeo and Juliet" revolves around the bitter feud between the Montague and Capulet families. This animosity is the backdrop against which the tragic love story unfolds, highlighting the destructive impact of familial hatred.

*Context 2*
Title: Shakespeare's Famous Feuds
Author: Robert Johnson
Year Written: 2018

In "Romeo and Juliet," William Shakespeare explores the consequences of the long-standing feud between the Montagues and the Capulets. This enmity sets the stage for the tragic events that follow, demonstrating the theme of love versus hate.

*Context 3*
Title: The Tragic Love Story of Romeo and Juliet
Author: Emily Davis
Year Written: 2020

William Shakespeare's "Romeo and Juliet" features the Montagues and Capulets, two noble families embroiled in a fierce rivalry. Their ongoing conflict serves as a critical element in the narrative, driving the plot and the ultimate fate of the protagonists.

### Question
In the context of "Romeo and Juliet", written by William Shakespeare in the early 1590s, what are the names of the two feuding families? There is only one correct choice.

### Choices
A. Montague and Capulet
B. Bennet and Darcy
C. Linton and Earnshaw
D. Bloom and Dedalus

### Thought Process and Answer
Thought process: In William Shakespeare's "Romeo and Juliet," the two feuding families are the Montagues and the Capulets, making A the correct choice. The Bennets and Darcys are in "Pride and Prejudice", the Lintons and Earnshaws in "Wuthering Heights", and Bloom and Dedalus in "Ulysses".
Answer: A.

## Example 4

### Instructions
Answer the following question using the 3 supporting contexts below.

*Context 1*
Title: "George Orwell's '1984': A Literary Analysis"
Author: Emma Thompson
Year Written: 2018

The totalitarian regime in Orwell's "1984" is symbolized by the omnipresent figure of Big Brother. This character represents the Party's surveillance and control over society, making Big Brother the quintessential leader in the dystopian world.

*Context 2*
Title: "Understanding '1984': Key Themes and Characters"
Author: John R. Williams
Year Written: 2015

In "1984," Big Brother is the face of the Party and the symbol of its authority. While other characters like O'Brien and Emmanuel Goldstein play significant roles, it is Big Brother who epitomizes the totalitarian rule over the citizens of Oceania.

*Context 3*
Title: "The Significance of Big Brother in Orwell's '1984'"
Author: Sarah J. Murray
Year Written: 2020

Big Brother is the personification of the Party's power in George Orwell's "1984." The novel depicts him as the ever-watchful leader who controls every aspect of life in Oceania. Despite being a symbolic figure, his presence is a constant reminder of the regime's dominance.

### Question
In the context of "1984", written by George Orwell in 1949, what is the name of the totalitarian leader? There is only one correct choice.

### Choices
A. Big Brother
B. O'Brien
C. Winston Smith
D. Emmanuel Goldstein

### Thought Process and Answer
Thought process: In George Orwell's "1984," the totalitarian leader is known as Big Brother, making A the correct choice. O'Brien is a character in the novel, Winston Smith is the protagonist, and Emmanuel Goldstein is a rebel leader.
Answer: A.

## Example 5

### Instructions
Answer the following question using the 5 supporting contexts below.

*Context 1*
Title: The Classic Tale of Moby-Dick
Author: Jane Doe
Year Written: 2020

In Herman Melville's novel 'Moby-Dick,' Captain Ahab is the monomaniacal captain of the whaling ship Pequod. Ahab's obsession with the giant white whale Moby-Dick drives the story to its tragic conclusion.

*Context 2*
Title: Understanding Melville's Moby-Dick
Author: John Smith
Year Written: 2018

Captain Ahab, the captain of the Pequod, is driven by a single-minded quest to seek revenge on Moby-Dick, the white whale that maimed him. This obsession defines Ahab's character throughout the novel.

*Context 3*
Title: Melville's Masterpiece: A Deep Dive into Moby-Dick
Author: Emily Clark
Year Written: 2015

In 'Moby-Dick,' Captain Ahab is portrayed as a man consumed by his obsession with the whale that cost him his leg. His relentless pursuit of Moby-Dick is central to the plot of the novel.

*Context 4*
Title: Ahab's Obsession in Moby-Dick
Author: Robert Brown
Year Written: 2019

The character of Captain Ahab in Herman Melville's 'Moby-Dick' is defined by his vengeful pursuit of the white whale, Moby-Dick. Ahab's fixation on the whale leads to his ultimate downfall.

*Context 5*
Title: The Pursuit of Moby-Dick: An Analysis
Author: Linda Green
Year Written: 2021

Captain Ahab's vendetta against the white whale, Moby-Dick, is the driving force behind the narrative of Herman Melville's 'Moby-Dick.' Ahab's obsession with the whale symbolizes his inner turmoil and relentless nature.

### Question
In the context of "Moby-Dick", written by Herman Melville in 1851, what is the name of the ship's captain obsessed with hunting the titular whale? There is only one correct choice.

### Choices
A. Captain Hook
B. Captain Nemo
C. Captain Flint
D. Captain Ahab

### Thought Process and Answer
Thought process: In Herman Melville's "Moby-Dick," the ship's captain obsessed with hunting the whale is Captain Ahab, making D the correct choice. Captain Nemo is in "Twenty Thousand Leagues Under the Sea", Captain Flint in "Treasure Island", and Captain Hook in "Peter Pan".
Answer: D.

## Example 6

### Instructions
Answer the following question using the {k_icl_retrieval_chunks} supporting contexts below.

{contexts}{formatted_question_and_choices}
"""

RAG_QUALITY_PROMPT = """
## Example 1

### Instructions
Answer the following question using the 8 supporting contexts below.

*Context 1*
Title: The Classic Tale of Moby-Dick
Author: Jane Doe
Year Written: 2020

In Herman Melville's novel 'Moby-Dick,' Captain Ahab is the monomaniacal captain of the whaling ship Pequod. Ahab's obsession with the giant white whale Moby-Dick drives the story to its tragic conclusion.

*Context 2*
Title: Understanding Melville's Moby-Dick
Author: John Smith
Year Written: 2018

Captain Ahab, the captain of the Pequod, is driven by a single-minded quest to seek revenge on Moby-Dick, the white whale that maimed him. This obsession defines Ahab's character throughout the novel.

*Context 3*
Title: Melville's Masterpiece: A Deep Dive into Moby-Dick
Author: Emily Clark
Year Written: 2015

In 'Moby-Dick,' Captain Ahab is portrayed as a man consumed by his obsession with the whale that cost him his leg. His relentless pursuit of Moby-Dick is central to the plot of the novel.

*Context 4*
Title: Ahab's Obsession in Moby-Dick
Author: Robert Brown
Year Written: 2019

The character of Captain Ahab in Herman Melville's 'Moby-Dick' is defined by his vengeful pursuit of the white whale, Moby-Dick. Ahab's fixation on the whale leads to his ultimate downfall.

*Context 5*
Title: The Pursuit of Moby-Dick: An Analysis
Author: Linda Green
Year Written: 2021

Captain Ahab's vendetta against the white whale, Moby-Dick, is the driving force behind the narrative of Herman Melville's 'Moby-Dick.' Ahab's obsession with the whale symbolizes his inner turmoil and relentless nature.

*Context 6*
Title: The Pursuit of Moby-Dick: An Analysis
Author: Linda Green
Year Written: 2021

Captain Ahab's relentless pursuit of the white whale, Moby-Dick, serves as the central theme of Herman Melville's 'Moby-Dick,' reflecting his inner struggles and unyielding determination.

*Context 7*
Title: The Pursuit of Moby-Dick: An Analysis
Author: Linda Green
Year Written: 2021

The narrative of Herman Melville's 'Moby-Dick' revolves around Captain Ahab's obsessive vendetta against the white whale, symbolizing his internal conflict and unwavering resolve.

*Context 8*
Title: The Pursuit of Moby-Dick: An Analysis
Author: Linda Green
Year Written: 2021

In Herman Melville's Moby-Dick, Captain Ahab's identity is shaped by his vengeful obsession with the white whale, Moby-Dick, which ultimately leads to his demise.

### Question
In the context of "Moby-Dick", written by Herman Melville in 1851, what is the name of the ship's captain obsessed with hunting the titular whale? There is only one correct choice.

### Choices
A. Captain Hook
B. Captain Nemo
C. Captain Flint
D. Captain Ahab

### Thought Process and Answer
Thought process: In Herman Melville's "Moby-Dick," the ship's captain obsessed with hunting the whale is Captain Ahab, making D the correct choice. Captain Nemo is in "Twenty Thousand Leagues Under the Sea", Captain Flint in "Treasure Island", and Captain Hook in "Peter Pan".
Answer: D.

## Example 2

### Instructions
Answer the following question using the 8 supporting contexts below.

*Context 1*
Title: Soma: The Happiness Drug in Brave New World
Author: James Anderson
Year Written: 2018

In Aldous Huxley's 'Brave New World,' Soma is a powerful tool used by the state to ensure the happiness and compliance of its citizens. This drug provides an escape from any discomfort or dissatisfaction, thus maintaining societal stability.

*Context 2*
Title: The Role of Soma in Brave New World
Author: Catherine Evans
Year Written: 2020

Soma is the cornerstone of the government's control over the population in Huxley's dystopian society. By offering a chemically-induced form of happiness, the state effectively prevents any dissent or unrest among its citizens.

*Context 3*
Title: The Role of Soma in Brave New World
Author: Catherine Evans
Year Written: 2020

Soma, in Aldous Huxley's Brave New World, is a key mechanism employed by the state to maintain happiness and compliance among its people, providing relief from discomfort and preserving the stability of society.

*Context 4*
Title: The Role of Soma in Brave New World
Author: Catherine Evans
Year Written: 2020

In Aldous Huxley's Brave New World, Soma serves as a potent instrument of state control, ensuring citizens' happiness and obedience by offering an escape from discomfort and dissatisfaction, thereby upholding societal stability.

*Context 5*
Title: The Role of Soma in Brave New World
Author: Catherine Evans
Year Written: 2020

Soma is the cornerstone of the government's control over the population in Huxley's dystopian society. By offering a chemically-induced form of happiness, the state effectively prevents any dissent or unrest among its citizens.

*Context 6*
Title: The Role of Soma in Brave New World
Author: Catherine Evans
Year Written: 2020

In Huxley's dystopian society, Soma serves as the foundation of the government's control, providing chemically-induced happiness that suppresses dissent and unrest among the population.

*Context 7*
Title: The Role of Soma in Brave New World
Author: Catherine Evans
Year Written: 2020

Soma is a pivotal tool for maintaining control in Huxley's dystopian world, as it offers artificial happiness that ensures the population remains compliant and free from rebellion.

*Context 8*
Title: The Role of Soma in Brave New World
Author: Catherine Evans
Year Written: 2020

Soma is a state-sanctioned drug that provides feelings of euphoria and contentment, effectively eliminating discomfort or dissatisfaction and ensuring societal stability.

### Question
In the context of "Brave New World", written by Aldous Huxley in 1932, what substance is widely used in the society to control citizens' happiness? There is only one correct choice.

### Choices
A. Gold
B. Soma
C. Silver
D. Iron

### Thought Process and Answer
Thought process: In Aldous Huxley's "Brave New World," Soma is used as a means to maintain social control by ensuring citizens' happiness, making B the correct choice. Gold, Silver, and Iron are not the substances used for this purpose in the book.
Answer: B.

## Example 3

### Instructions
Answer the following question using the {k_icl_retrieval_chunks} supporting contexts below.

{contexts}{formatted_question_and_choices}
"""

LETTER_TO_INDEX = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

from itertools import permutations

def uncapitalize_first(s):
    return s[0].lower() + s[1:]

def format_name(name):
    # Split the name by comma
    parts = name.split(',')

    # If there is a comma, we assume the format is "Lastname, Firstname"
    if len(parts) == 2:
        formatted_name = parts[1].strip() + ' ' + parts[0].strip()
    else:
        # If there's no comma, assume the format is already "Firstname Lastname"
        formatted_name = name.strip()

    return formatted_name

def second_last_character(input_string: str):
    try:
        # Remove newline characters from the end of the string
        modified_string = input_string.rstrip('\n')
        answer_index = LETTER_TO_INDEX[modified_string[-2]]
    except (KeyError, IndexError):
        answer_index = None
    return answer_index

def generate_all_answer_strings():
    choices = 'ABCD'
    all_answers = []
    for r in range(1, len(choices) + 1):
        for perm in permutations(choices, r):
            answer = ''.join(perm)
            all_answers.append(f'Answer: {answer}.')
    return all_answers