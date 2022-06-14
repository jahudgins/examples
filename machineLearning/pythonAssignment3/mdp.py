import sys
import random
import numpy
import numpy.matlib
import time
import operator

#random.seed(1234)
def nodetext(state, utility):
    result = str(state.key).replace(' ', '\\n')
    if utility:
        result += "\\n{0:.0f}".format(state.utility)
    return result

class Model:
    def __init__(self, name='Model', graphStates=False, fill=True):
        self.states = {}
        self.initial = None
        self.name = name
        self.graphStates = graphStates
        self.fill = fill

    def setInitialState(self, key):
        self.initial = self.states[key]

    def __setDisplayRecurse(self, state, display):
        if state == self.limitDisplay:
            display = True
        elif state.display:
            return display

        finalDisplay = display
        for action in state.actions:
            for transition in action.transitions:
                nextDisplay = self.__setDisplayRecurse(transition.toState, display)
                finalDisplay = finalDisplay or nextDisplay

        state.display = finalDisplay
        return finalDisplay

    # limit display to go through this node (other paths ignored)
    def limitDisplay(self, key):
        self.limitDisplay = self.states[key]
        for state in self.states.values():
            state.display = False
        self.__setDisplayRecurse(self.initial, False)

    def bestPolicyOnly(self, state, policy, bestStates, indent=''):
        if state in bestStates:
            return

        bestStates.add(state)
        policyAction = policy.decisions[state.key]
        if policyAction and policyAction.transitions:
            for transition in policyAction.transitions:
                self.bestPolicyOnly(transition.toState, policy, bestStates, indent+'   ')

    def statesAndChildren(self, stateKeys):
        displaySet = set()
        for stateKey in stateKeys:
            state = self.states[stateKey]
            displaySet.add(state)
            for action in state.actions:
                for transition in action.transitions:
                    displaySet.add(transition.toState)

            """
            # Showing the parents of selected states isn't very useful
            for state in self.states.values():
                for action in state.actions:
                    for transition in action.transitions:
                        if transition.toState.key == stateKey:
                            displaySet.add(state)
            """

        return displaySet

    def displayStates(self, policy):
        if policy and self.initial:
            bestStates = set();
            self.bestPolicyOnly(self.initial, policy, bestStates)
            return bestStates

        if not self.limitDisplay:
            return set(self.states.values())

        return set(filter(lambda x : x.display, self.states.values()))


    def findOrCreateState(self, key, maximizeReward=True):
        if not self.states.has_key(key):
            self.states[key] = State(key, len(self.states), maximizeReward)
        return self.states[key]

    def prune(self):
        if not self.initial:
            return
        
        idx = 0
        stateSet = set()
        foundStates = [self.initial]
        while idx < len(foundStates):
            state = foundStates[idx]
            idx += 1
            for action in state.actions:
                for transition in action.transitions:
                    if transition.toState not in stateSet:
                        foundStates.append(transition.toState)
                        stateSet.add(transition.toState)

        self.states = {}
        idx = 0
        for state in foundStates:
            self.states[state.key] = state
            # re-index because many nodes have been deleted
            state.index = idx
            idx += 1

    def initialStates(self, state, displayStates, levels):
        if levels == 0:
            return

        displayStates.add(state)
        for action in state.actions:
            for transition in action.transitions:
                self.initialStates(transition.toState, displayStates, levels-1)

    def graphviz(self, filename, utility=False, policy=None, bestPolicy=False, displayKeys=None, displayChildren=False, useActionQ=False, levels=0, lastTransitions=True):
        f = open(filename, 'wt')
        f.write('digraph "{0}" {{\n'.format(self.name))

        if displayKeys:
            displaySet = set(map(lambda x : self.states[x], displayKeys))
        else:
            if displayChildren:
                displaySet = self.statesAndChildren(displayAndChildrenKeys)
            else:
                displaySet = self.displayStates(bestPolicy and policy)

            if levels!=0:
                limitSet = set()
                self.initialStates(self.initial, limitSet, levels)
                displaySet = limitSet & displaySet


        # write node labels
        for state in displaySet:
            color = 'yellowgreen' if state.maximizeReward else 'gold'
            extra = '' if not self.fill else ' fillcolor={0} style=filled'.format(color)
            f.write('  "{0}" [label="{1}" {2}];\n'.format(state.key, nodetext(state, utility), extra))

        for state in displaySet:
            # check the policy
            policyAction = None
            if policy:
                policyAction = policy.decisions[state.key]

            for action in state.actions:
                extra = ''
                if policyAction == action:
                    extra = 'color=red style=bold '

                for transition in action.transitions:
                    if not lastTransitions and transition.toState not in displaySet:
                        continue

                    f.write('  "{0}" -> "{1}"'.format(state.key, transition.toState.key))
                    Qlabel = ''
                    if useActionQ:
                        Qlabel = '\\n{0:.1f}'.format(action.Q)
                    f.write(' [{0} label = "{1}\\n{2:.2f}\\n{3:.0f}{4}"];\n'.format(extra, action,
                                    transition.probability, (transition.reward + transition.toState.reward), Qlabel))
                    if transition.toState not in displaySet:
                        f.write('  "{0}" [label="a" style=invis];\n'.format(transition.toState.key))

            if len(state.actions) == 0:
                f.write('  {{ rank=max; "{0}"; }}\n'.format(state.key))

        f.write('}\n')
        f.close()

    def initailzeUtilities(self):
        for state in self.states.values():
            state.utility = 0
            for action in state.actions:
                # to many conditions need to be handled for unitialized action.Q so just set it to 0
                # this will mean for negative rewards, unvisited actions will be more heavily weighted
                action.Q = 0

    def valueIteration(self, gamma, maxDelta, maxIterations, analyze=None):
        start = time.time()
        self.initailzeUtilities()
        iterations = 0
        delta = maxDelta
        while iterations < maxIterations and delta >= maxDelta:

            # reset delta for this iteration
            delta = 0

            # randomly visit all states
            stateValues = self.states.values()
            indices = range(len(stateValues))
            random.shuffle(indices)
            for index in indices:
                state = stateValues[index]

                # base truth when in terminal state
                if len(state.actions) == 0:
                    newUtility = 0
                else:
                    # calculate new utility
                    if state.maximizeReward:
                        newUtility = -sys.float_info.max
                    else:
                        newUtility = sys.float_info.max

                    for action in state.actions:
                        actionUtility = action.calculateUtility(gamma)
 
                        # get maximum of all actions
                        if state.maximizeReward:
                            newUtility = max(newUtility, actionUtility)
                        else:
                            newUtility = min(newUtility, actionUtility)

                # keep track of maximum delta for terminating iteration; update utility

                delta = max(delta, abs(newUtility - state.utility))
                state.utility = newUtility

            self.analyzeLearning(iterations, maxIterations, analyze, useActionQ=False)

            if iterations < 5 and self.graphStates:
                self.graphviz('valueIteration{0}.dot'.format(iterations), True)

            iterations += 1

        policy = Policy(self.states)
        deltaTime = time.time() - start
        if self.graphStates:
            self.graphviz('valueIteration{0}.dot'.format(iterations), True, policy)
        stats = { 'iterations':iterations, 'numstates':len(self.states), 'elapsed':deltaTime }
        return policy, stats

    def policyEvaluation(self, policy, gamma):
        #
        # for fixed policy
        #
        # v = T * gamma * v + R
        #
        # where:
        #       v[i] is utility for state i
        #       T[i, j] is transition probability from state i to j
        #       R[i] is expected reward from state i (weighted sum over all transitions)
        #
        # v = inv([I - gamma * T]) * R
        #
        T = numpy.matlib.zeros((len(self.states), len(self.states)))
        R = numpy.matlib.zeros((len(self.states), 1))
        for state in self.states.values():
            action = policy.decisions[state.key]
            if action:
                for transition in action.transitions:
                    T[state.index, transition.toState.index] = transition.probability
                    R[state.index] += (transition.reward + transition.toState.reward) * transition.probability

        # this might be more optimal using arrays and pinv (Moore-Penrose pseudoinverse)
        # see http://stackoverflow.com/questions/3890621/matrix-and-array-multiplication-in-numpy
        v = (numpy.matlib.identity(len(self.states)) - gamma * T).I * R

        # set the utilities
        for state in self.states.values():
            state.utility = v[(state.index, 0)]

    def policyIteration(self, gamma, maxIterations):
        start = time.time()
        self.initailzeUtilities()
        iterations = 0

        policy = Policy(self.states, isRandom=True)

        while iterations < maxIterations:

            # evaluate utility based on policy
            self.policyEvaluation(policy, gamma)

            if iterations < 5 and self.graphStates:
                self.graphviz('policyIteration{0}.dot'.format(iterations), True, policy)

            iterations += 1

            # policy improvement
            newPolicy = Policy(self.states)
            if newPolicy == policy:
                break

            policy = newPolicy

        deltaTime = time.time() - start
        if self.graphStates:
            self.graphviz('policyIterationFinal.dot', True, policy)
        stats = { 'iterations':iterations, 'numstates':len(self.states), 'elapsed':deltaTime }
        return policy, stats

    def analyzeLearning(self, iterations, maxIterations, analyze, useActionQ):
        if not analyze:
            return

        results = analyze['results']
        step = maxIterations / analyze['samples']
        if iterations == (analyze['sample'] + 1) * step:
            policy = Policy(self.states, useActionQ=useActionQ)
            if not results.has_key(iterations):
                results[iterations] = []
            results[iterations].append(self.simulate(analyze['simulations'], policy))
            analyze['sample'] += 1


    def UpdateQKnown(self, actions, state, epsilon, gamma, learningRate):
        bestAction = None
        for action in actions:
            totalOccurances = sum(map(lambda x : x.occurances, action.transitions))

            bestQ = -sys.float_info.max if state.maximizeReward else sys.float_info.max

            actionQ = 0
            # add expected discounted Q and transition-reward
            for transition in action.transitions:
                if totalOccurances == 0:
                    probability = 1.0 / len(action.transitions)
                else:
                    probability = transition.occurances / totalOccurances
                actionQ += gamma * transition.toState.utility * probability
                actionQ += (transition.toState.reward + transition.reward) * probability

            # get maximum (or minimum) of all actions
            if state.maximizeReward and actionQ > bestQ:
                bestQ = actionQ
                bestAction = action
            elif not state.maximizeReward and actionQ < bestQ:
                bestQ = actionQ
                bestAction = action

        # learn utility
        state.utility = (1-learningRate) * state.utility + learningRate * bestQ

        # *BUT* sometimes we *choose* random action (despite our calculation of best) at epsilon proportion
        if random.random() < epsilon:
            bestAction = state.actions[random.randint(0, len(state.actions)-1)]

        # go to next state
        transition = bestAction.randomTransition()
        transition.occurances += 1
        return transition.toState


    def UpdateQUnknown(self, actions, state, epsilon, gamma, learningRate):
        # decide on action just based on Q or random (even immediate reward is unknown)
        # sometimes we *choose* random action (despite our calculation of best) at epsilon proportion
        if random.random() < epsilon:
            bestAction = state.actions[random.randint(0, len(state.actions)-1)]
        else:
            bestAction = actions[0]
            for action in actions:
                if state.maximizeReward and action.Q > bestAction.Q:
                    bestAction = action
                elif not state.maximizeReward and action.Q < bestAction.Q:
                    bestAction = action

        transition = bestAction.randomTransition()
        state = transition.toState

        # now calculate Q update
        reward = transition.toState.reward + transition.reward

        # estimate of optimal future value (one step look-ahead)
        if len(state.actions) == 0:
            bestQ = 0
        else:
            nextActions = list(state.actions)
            random.shuffle(nextActions)
            bestQ = nextActions[0].Q
            for action in nextActions:
                bestQ = max(bestQ, action.Q) if state.maximizeReward else min(bestQ, action.Q)

        learnedValue = reward + gamma * bestQ

        bestAction.Q = (1-learningRate) * bestAction.Q + learningRate * learnedValue

        return state


    def reinforcementLearn(self, gamma, epsilonDecay, maxIterations, immediateRewardsKnown=False, analyze=None):
        start = time.time()
        self.initailzeUtilities()
        useActionQ = not immediateRewardsKnown

        iterations = 0
        epsilon = 1

        while iterations < maxIterations:

            # calc learning rate for this iteration
            learningRate = 1.0 / (iterations + 1)

            # start at initial and make decisions until we get to end state
            state = self.initial
            graphKeys = []
            graphKeys.append(state.key)
            while len(state.actions) > 0:
                # calculate new Q and choose best action
                actions = list(state.actions)
                random.shuffle(actions)

                if immediateRewardsKnown:
                    state = self.UpdateQKnown(actions, state, epsilon, gamma, learningRate)
                else:
                    state = self.UpdateQUnknown(actions, state, epsilon, gamma, learningRate)
                graphKeys.append(state.key)

            if iterations < 10 and self.graphStates:
                self.graphviz('rl{0}.dot'.format(iterations), useActionQ=useActionQ)

            self.analyzeLearning(iterations, maxIterations, analyze, useActionQ=useActionQ)

            iterations += 1
            epsilon *= epsilonDecay

        policy = Policy(self.states, useActionQ=useActionQ)
        deltaTime = time.time() - start
        if self.graphStates:
            self.graphviz('rlFinal.dot'.format(iterations), True, policy, useActionQ=useActionQ)
        stats = { 'iterations':iterations, 'numstates':len(self.states), 'elapsed':deltaTime }
        return policy, stats


    def simulate(self, iterations, policy, policyMin=None):
        totalReward = 0
        iteration = 0
        while iteration < iterations:
            state = self.initial
            while len(state.actions) > 0:
                # use policy if it has a decision for this state, random decision otherwise
                if policy.decisions.has_key(state.key):
                    if policyMin and not state.maximizeReward:
                        action = policyMin.decisions[state.key]
                    else:
                        action = policy.decisions[state.key]
                else:
                    actionIndex = random.randint(0, len(state.actions)-1)
                    action = state.actions[actionIndex]

                transition = action.randomTransition()
                totalReward += transition.toState.reward + transition.reward
                state = transition.toState

            iteration += 1

        return totalReward / iterations

    def countItems(self):
        numActions = 0
        numTransitions = 0
        for state in self.states.values():
            numActions += len(state.actions)
            for action in state.actions:
                numTransitions += len(action.transitions)

        return { 'numStates':len(self.states), 'numActions':numActions, 'numTransitions':numTransitions }

    def outputUtilites(self, filename):
        f = open(filename, 'wt')
        states = list(self.states.values())
        states.sort(key=operator.attrgetter('key'))
        for state in self.states.values():
            f.write(str(state) + '\n')
        f.close()

class Policy:
    def __init__(self, states, isRandom=False, useActionQ=False):
        self.decisions = {}
        if isRandom:
            self.randomPolicy(states)
        else:
            self.bestPolicy(states, useActionQ)

    def randomPolicy(self, states):
        for state in states.values():
            # terminaml states have action None
            if len(state.actions) > 0:
                actionIndex = random.randint(0, len(state.actions)-1)
                action = state.actions[actionIndex]
            else:
                action = None

            self.decisions[state.key] = action

    def bestPolicy(self, states, useActionQ):
        for state in states.values():

            # argmax for all actions
            bestAction = None
            if state.maximizeReward:
                bestActionUtility = -sys.float_info.max
            else:
                bestActionUtility = sys.float_info.max

            for action in state.actions:
                # find best utility (gamma doesn't really matter here)
                if useActionQ:
                    actionUtility = action.Q
                else:
                    actionUtility = action.calculateUtility(1)

                update = state.maximizeReward and actionUtility > bestActionUtility
                update = update or not state.maximizeReward and actionUtility < bestActionUtility
                if update:
                    bestActionUtility = actionUtility
                    bestAction = action

            self.decisions[state.key] = bestAction

    def __eq__(self, other):
        # check each decision for object (pointer) comparison
        for key, decision in self.decisions.items():
            if decision != other.decisions[key]:
                return False
        return True

    def __str__(self):
        result = '{'
        for key, value in self.decisions.items():
            result += ' {0} : {1}\n'.format(str(key), str(value))
        result += '}'
        return result


class State:
    def __init__(self, key, index, maximizeReward=True):
        self.actions = []
        self.key = key
        self.index = index
        self.maximizeReward = maximizeReward
        self.utility = 0
        self.reward = 0
        self.display = True

    def __str__(self):
        return '{0} {1} {2}'.format(str(self.key), self.utility, self.reward)

    def addAction(self, action):
        self.actions.append(action)

    def setReward(self, reward):
        self.reward = reward

class Action:
    def __init__(self, actionName):
        self.transitions = []
        self.actionName = actionName
        self.Q = 0

    def __str__(self):
        return self.actionName

    def addTransition(self, fromState, toState, probability, reward=0):
        self.transitions.append(Transition(fromState, toState, probability, reward))

    def calculateUtility(self, gamma):
        actionUtility = 0
        # add expected discounted utility and transition-reward
        for transition in self.transitions:
            actionUtility += gamma * transition.toState.utility * transition.probability
            actionUtility += (transition.toState.reward + transition.reward) * transition.probability

        return actionUtility

    # simulate the next state based on actual transition probabilities (unknown to reinforcementLearner)
    def randomTransition(self):
        p = random.random()
        pTotal = 0
        for transition in self.transitions:
            pTotal += transition.probability
            if p < pTotal:
                return transition
        return transition

class Transition:
    def __init__(self, fromState, toState, probability, reward):
        self.fromState = fromState
        self.toState = toState
        self.reward = reward
        self.probability = probability
        self.occurances = 0

