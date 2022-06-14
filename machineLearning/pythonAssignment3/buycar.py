import sys
import mdp
import math
import argparse
import time
import json
import numpy


class CarState:
    def __init__(self, carType, month):
        self.carType = carType
        self.month = month

    def __str__(self):
        return '{0} month{1}'.format(self.carType, self.month)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.carType == other.carType and self.month == other.month

def Payment(principle, interest, term):
    return principle * interest / (1.0 - math.pow(1.0+interest, -term))

def PurchaseCost(month, repairNeeded):
    global args
    global newCarTax, newCarRegistration
    global tradeRepair

    remainingMonths = args.maxMonths - month
    cost = 0

    # calculate depriciation
    initialDepreciation = args.immediateDepriciation * args.newCarPrice
    initialValue = (1 - args.immediateDepriciation) * args.newCarPrice

    """
    oldMonthlyDepriciationMultiplier = math.pow(1 - args.annualDepriciation, 1/12.0)
    oldTotalDepriciation = initialValue * (1.0 - math.pow(oldMonthlyDepriciationMultiplier, remainingMonths))
    """

    monthlyDepriciationMultiplier = math.pow(1 - args.annualDepriciation, 1/12.0) / gamma
    totalDepriciation = initialValue * (1.0 - math.pow(monthlyDepriciationMultiplier, remainingMonths))

    totalDepriciation += initialDepreciation

    cost += newCarTax + newCarRegistration
    geometricSum = (1.0 - gamma ** remainingMonths) / (1.0 - gamma)
    cost += geometricSum * args.newCarMonthlyRepairs
    cost += totalDepriciation

    principle = args.newCarPrice
    if repairNeeded:
        principle -= tradeRepair
    else:
        principle -= args.tradeValue

    payment = Payment(principle, args.interestRate, args.loanTerm)

    # calculate total interest payed by interest on decreasing principle month-to-month
    totalInterest = 0

    monthlyInterestRate = math.pow(1.0 + args.interestRate, 1/12.) - 1.0
    discount = 1.0
    for i in range(min(remainingMonths, int(args.loanTerm))):
        oldInterest = principle * monthlyInterestRate
        interest = principle * monthlyInterestRate * discount
        totalInterest += interest
        principle -= (payment - interest)
        discount *= gamma

    cost += totalInterest

    return cost


def InitializeModel():
    global args
    global tradeRepair

    model = mdp.Model('Buy Car', args.graph, fill=False)
    state = model.findOrCreateState(CarState('old-ok', 0))
    model.setInitialState(state.key)

    terminalNoRepair = args.tradeValue * args.salvage
    terminalRepair = tradeRepair * args.salvage
    terminalBuy = 0

    for month in range(0, args.maxMonths-1):
        nextOkState = model.findOrCreateState(CarState('old-ok', month+1))
        nextRepairState = model.findOrCreateState(CarState('old-repair', month+1))
        nextBuyState = model.findOrCreateState(CarState('new', month+1))

        # set terminal rewards
        if month == args.maxMonths-2:
            nextOkState.setReward(terminalNoRepair)
            nextRepairState.setReward(terminalRepair)
        # buy state is always terminal
        nextBuyState.setReward(terminalBuy)

        # actions, transitions and rewards for old-ok
        state = model.findOrCreateState(CarState('old-ok', month))
        action = mdp.Action('keep')
        action.addTransition(state, nextOkState, 1.0 - args.repairProb, reward=0)
        action.addTransition(state, nextRepairState, args.repairProb, reward=0)
        state.addAction(action)
        action = mdp.Action('buy')
        action.addTransition(state, nextBuyState, 1.0, -PurchaseCost(month, False))
        state.addAction(action)

        if month == 0:
            continue

        # actions, transitions and rewards for old-repair
        state = model.findOrCreateState(CarState('old-repair', month))
        action = mdp.Action('keep')
        action.addTransition(state, nextOkState, 1.0 - args.repairProb, -args.averageRepairCost)
        action.addTransition(state, nextRepairState, args.repairProb, -args.averageRepairCost)
        state.addAction(action)
        action = mdp.Action('buy')
        action.addTransition(state, nextBuyState, 1.0, -PurchaseCost(month, True))
        state.addAction(action)

    return model

def analyzeRL(model, immediateRewardsKnown):
    maxRLiterations = 5 * maxIterations
    epsilonDecay = math.pow(0.001, 1.0/maxRLiterations)
    analyze = {'sample':0, 'samples':100, 'simulations':200, 'results':{}}
    for rewardTest in range(50):
        start = time.time()
        analyze['sample'] = 0
        policy, stats = model.reinforcementLearn(gamma, epsilonDecay, maxRLiterations, immediateRewardsKnown=immediateRewardsKnown, analyze=analyze)
        deltaTime = time.time() - start
        print "RL test {0} took {1:.1f} sec".format(rewardTest, deltaTime)

    print "RL test results immediateRewardsKnown:{0}".format(immediateRewardsKnown)
    print json.dumps(analyze['results'], indent=2)

    rewardsType = 'known' if immediateRewardsKnown else 'unknown'
    f = open('buycar.rl.{0}.json'.format(rewardsType), "wt")
    json.dump(analyze['results'], f, indent=2)
    f.close()


def analyzeVI(model):
    analyze = {'sample':0, 'samples':100, 'simulations':200, 'results':{}}
    policy, stats = model.valueIteration(gamma, maxDelta, maxIterations, analyze=analyze)
    print json.dumps(analyze['results'], indent=2)

    f = open('buycar.vi.json', "wt")
    json.dump(analyze['results'], f, indent=2)
    f.close()


def solveModel(model):
    policy, stats = model.valueIteration(gamma, maxDelta, maxIterations)
    model.graphviz('buycar.vi.optimalonly.dot', utility=True, policy=policy, bestPolicy=True)
    model.graphviz('buycar.vi.policy.dot', utility=True, policy=policy)
    model.outputUtilites('buycar.vi.utilities')
    print "VI: ", stats

    policy, stats = model.policyIteration(gamma, maxIterations)
    model.graphviz('buycar.pi.optimalonly.dot', utility=True, policy=policy, bestPolicy=True)
    model.graphviz('buycar.pi.policy.dot', utility=True, policy=policy)
    model.outputUtilites('buycar.pi.utilities')
    print "PI: ", stats

    # use enough iterations to visit same number of states as valueIteration
    maxRLiterations = 5 * maxIterations
    epsilonDecay = math.pow(0.001, 1.0/maxRLiterations)
    policy, stats = model.reinforcementLearn(gamma, epsilonDecay, maxRLiterations, immediateRewardsKnown=False)
    model.graphviz('buycar.rlk.optimalonly.dot', utility=True, policy=policy, bestPolicy=True)
    model.graphviz('buycar.rlk.policy.dot', utility=True, policy=policy)
    print "RLK: ", stats

    policy, stats = model.reinforcementLearn(gamma, epsilonDecay, maxRLiterations, immediateRewardsKnown=True)
    model.graphviz('buycar.rlu.optimalonly.dot', utility=True, policy=policy, bestPolicy=True)
    model.graphviz('buycar.rlu.policy.dot', utility=True, policy=policy)
    print "RLU: ", stats



def compareRewardSimulation(model):
    policies = {}
    rewards = {}

    policies['vi'], stats = model.valueIteration(gamma, maxDelta, maxIterations)
    for rewardTest in range(50):
        policies['random'] = mdp.Policy(model.states, isRandom=True)

        maxRLiterations = 5 * maxIterations
        epsilonDecay = math.pow(0.001, 1.0/maxRLiterations)
        policies['rlk'], stats = model.reinforcementLearn(gamma, epsilonDecay, maxRLiterations, immediateRewardsKnown=False)

        policies['rlu'], stats = model.reinforcementLearn(gamma, epsilonDecay, maxRLiterations)

        for key, policy in policies.items():
            if not rewards.has_key(key):
                rewards[key] = []
            rewards[key].append(model.simulate(200, policy))


    print "maxRLiterations:{0}".format(maxRLiterations)
    for key, policy in rewards.items():
        print "{0} rewards: mean:{1}, std.dev:{2}".format(key, numpy.mean(rewards[key]), numpy.std(rewards[key]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run MDP for deciding whether to repair an old car or buy a new car')
    parser.add_argument('--maxMonths', type=int, help='maximum months to simulate', default=12)
    parser.add_argument('--repairProb', type=float, help='probability that the car will need to be repaired', default=0.3)
    parser.add_argument('--averageRepairCost', type=float, help='average cost of single repair', default=1000)
    parser.add_argument('--newCarPrice', type=float, help='cost of new car (excluding fees)', default=24698)
    parser.add_argument('--immediateDepriciation', type=float, help='ratio of immediate depreciation', default=0.05)
    parser.add_argument('--newCarMonthlyRepairs', type=float, help='cost of monthly repairs for new car', default=0)
    parser.add_argument('--annualDepriciation', type=float, help='ratio of annual depreciation', default=0.15)
    parser.add_argument('--interestRate', type=float, help='interest rate', default=0.031)
    parser.add_argument('--loanTerm', type=float, help='months in loan term', default=60)
    parser.add_argument('--tradeValue', type=float, help='trade value', default=3000)
    parser.add_argument('--salvage', type=float, help='salvage ratio', default=0.5)
    parser.add_argument('--graph', action='store_true', help='print .dot file for graphviz')
    parser.add_argument('--analyze', help='do more in-depth time-consuming analysis')

    args = parser.parse_args()
    print ' '.join(sys.argv)

    carStates = 3

    newCarTax = 0.0625 * args.newCarPrice
    newCarRegistration = 370

    tradeRepair =  args.tradeValue - args.averageRepairCost * 0.5

    gamma = 0.99
    maxDelta = 0.001
    maxIterations = 100

    model = InitializeModel()

    model.graphviz('buycarInitial.dot')

    print model.countItems()

    solveModel(model)

    if args.analyze:
        analyzeRL(model, immediateRewardsKnown=True)
        analyzeRL(model, immediateRewardsKnown=False)
        analyzeVI(model)
        compareRewardSimulation(model)


