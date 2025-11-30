import queue

class Instance:  

    def __init__(self, state, initialState, finalState, dictionary, actions):

        # Sort, because the order doesn't matter, more efficiency and consistency, so that one state has only one representation
        # Tuple, immutable object so that they can be hashed to be used in the search algorithm (bfs - indirect, set, dict)
        self.state = sorted(state)
        self.intialState = sorted(initialState)
        self.finalState = sorted(finalState)
        self.dictionary = dictionary
        self.actions = actions
        # Indicates the father, the state that generated the current state
        self.prev = None
        # Indicates the action that was carried out on the father that generated the current state
        self.action = None

    def __repr__(self):
        # A printable string representation of the sequence of actions

        s = ""
        for i in range(len(self.state)):
            s += "{} ".format(self.state[i])
            s += "\n"
        return s

    def __eq__(self, other):
        return self.state == other.state
    
    # The hash function exists to allow the storage and data recuperation in a very quick way
    # Convert the variable size entry/input in a fixed integer value (the hash value)
    def __hash__(self):
        # To hash an object, it needs to be immutable, so we transform in a tuple
        return hash(tuple(self.state))
    
    def __lt__(self, other):
        return str(self) < str(other)
    
    def copy(self):
        # Return a copy of the state

        state = []
        for i in range(len(self.state)):
                state.append(self.state[i])

        return Instance(state, self.intialState, self.finalState, self.dictionary, self.actions)
    
    def is_goal(self):
        # True if this is a goal state, False otherwise
        # Check if the set of propositions of the final state (desired state, what we want as True)
        # is contained in the set of porprositions of the current state

        satisfied = True
        for proposition in self.finalState:
            if proposition not in self.state:
                satisfied = False

        return satisfied, self.state

    def get_neighbs(self):
        ## Get the neighboring states. Returns a list of the neighboring states

        neighbs = []

        # Step 1: check to each action of my instance, all the pre-conditions are satisifed in my current state 
        # Current state: everything inside our current state is considered true, all the rest is false
        for action in self.actions:
            pre_conditions_list = [prop for prop in actions[action]["pre"]]
            satisfied = True

            for item in pre_conditions_list:
                if item not in self.state:
                    satisfied = False
                    break

            # Step 2: update my current state accordingly the post conditions of the taken action 
            if satisfied:
                n = self.copy()
                post_condition_list = actions[action]["pos"]
                for post in post_condition_list:
                    # There is a positive propostion in my current state that is going to to become negative/false = negative post condition
                    # We must remove this proposition of our current state 
                    # We only consider the true propositions in our current state and when we are seeking the final state
                    if post < 0:
                        positive_post = post * (-1)
                        if positive_post in n.state:
                            n.state.remove(positive_post)

                    if post > 0:
                        # Check if there isn't a post condition equals an already current state proposition
                        # If there isn't the post in our current state, it's a new propostion generated after the action, we must add
                        if post not in n.state:
                            n.state.append(post)
                n.state = sorted(n.state)
                neighbs.append((n,  action))

        return neighbs
    
    def solve(self):
        # Find a shortest path from this state to a goal state. Returns list of State:
        # A path from this state to a goal state, where the first element is this state and the last element is the goal

        finished = False

        frontier = queue.Queue()
        frontier.put(self)

        on_frontier = set([self])
        visited = set([])

        # Each vertex passes through the frontier exactly once
        v = None
        while not finished and not frontier.empty():
            print(frontier.qsize())
            v = frontier.get()
            visited.add(v)
            on_frontier.remove(v)
            bool, res = v.is_goal()
            if bool:
                # print("final state:", res)
                finished = True
            else:
                for n, a in v.get_neighbs():
                    if n not in on_frontier and n not in visited:
                        on_frontier.add(n)
                        n.prev = v     # save the state that generates n (father of n)
                        n.action = a   # save the action that generated n
                        frontier.put(n)

        solution = []
        
        # Tracks form the final state (v) back to the initial state (where v.prev é None)
        while v.prev: 
            # Adiciona a ação que levou ao 'v' state
            solution.append(v.action) 
            v = v.prev
    
        solution.reverse()
        return solution
    
def process_instance():
    ## map: mapping the propositions into integers
    ## Ex:  {
    ##        on_c: 1, ...
    ##       }

    dictionary = {}
    actions = {}
    initialState = []
    finalState = []
    lines = []

    def reading():
        
        with open('planningsat/blocks-4-0.strips', 'r', encoding='utf-8') as arquivo:
            lines_content = arquivo.readlines()
            
            for line in lines_content:
                line = line.strip().split(";") # .strip() remove blank spaces and extra linebreaks 
                lines.append(line)

            # Breaking inital state and final state
            initialState = lines[len(lines) - 2]
            finalState = lines[len(lines) - 1]
        return initialState, finalState
        
    def mapping_into_integer_in_dictionary(dictionary):
        # Mapping each term into integer
        count = 1

        for i in range(len(lines)):
            for word in lines[i]:
                word = word.replace("~", "")
                if word not in dictionary:
                    dictionary[word] = count
                    count += 1

    def get_code(word, dictionary):
        if "~" in word:
            word = word.replace("~", "")
            index = dictionary[word] * (-1)
        else:
            index = dictionary[word]
        return index

    def mapping_into_integer_in_actions(dictionary, actions):
        # Adding actions, pre and post-conditions in integer form accordingly to "dictionary" in dictionary "actions"
        for i in range(len(lines) - 3):
            if i % 3 == 0:
                action = lines[i][0]
                actions[action] = {}
                list_pre_conditions = lines[i + 1]
                actions[action]["pre"] = [get_code(word, dictionary) for word in list_pre_conditions]
                list_post_conditions = lines[i + 2]
                actions[action]["pos"] = [get_code(word, dictionary) for word in list_post_conditions]

    def mapping_states(dictionary, initialState, finalState):
        # Transforming states into integers accordingly to "dictionary"
        initialState = [get_code(word, dictionary) for word in initialState]
        finalState = [get_code(word, dictionary) for word in finalState]
        state = initialState
        return state, initialState, finalState

    initialState, finalState = reading()
    mapping_into_integer_in_dictionary(dictionary)
    mapping_into_integer_in_actions(dictionary, actions)
    state, initialState, finalState = mapping_states(dictionary, initialState, finalState)

    # print(dictionary)
    # print(initialState)
    # print(finalState)

    return state, initialState, finalState, dictionary, actions
    

if __name__ == "__main__":
    state, initialState, finalState, dictionary, actions = process_instance()
    instance = Instance(state, initialState, finalState, dictionary, actions)
    result = instance.solve()
    print(result)


                               
