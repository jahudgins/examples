##
## Basketball MDP
##
## by Jonathan Hudgins <jhudgins8@gatech.edu>
##
## Assumptions:
##      Shots always hit rim to reset shot clock
##      Steals are not considered
##      Fouling is not considered
##      Trying to *setup* a 3pt or 2pt shot is always successful
##


import mdp
import math
import argparse
import sys
import numpy
import json
import time


class BasketballState:
    def __init__(self, pointDiff, shotRange, homePos, timeRemaining, shotClock, end=False):
        self.pointDiff = pointDiff
        self.shotRange = shotRange
        self.homePos = homePos
        self.timeRemaining = timeRemaining
        self.shotClock = shotClock
        self.end = end

    def __str__(self):
        if self.end:
            if self.pointDiff == 0: return 'Tie'
            if self.pointDiff < 0:  return 'Lose'
            if self.pointDiff > 0:  return 'Win'

        if self.pointDiff == 0: lead = 'Tied'                     
        if self.pointDiff < 0:  lead = 'L:{0}'.format(-self.pointDiff)
        if self.pointDiff > 0:  lead = 'W:{0}'.format(self.pointDiff)

        if self.shotRange == 0: rangeText = 'R:Far'
        if self.shotRange == 1: rangeText = 'R:2pt'
        if self.shotRange == 2: rangeText = 'R:3pt'

        if self.homePos:    pos = 'P:H'
        else:               pos = 'P:A'

        timeText = 'T:{0}'.format(self.timeRemaining)

        shotClockText = 'S:{0}'.format(self.shotClock)

        return '{0} {1} {2} {3} {4}'.format(lead, rangeText, pos, timeText, shotClockText)

    def __hash__(self):
        if self.end:
            return hash(str(self))
        return hash((self.pointDiff, self.shotRange, self.homePos, self.timeRemaining, self.shotClock))

    def __eq__(self, other):
        if self.end:
            return other.end and str(self) == str(other)

        return (self.pointDiff == other.pointDiff and
                self.shotRange == other.shotRange and
                self.homePos == other.homePos and
                self.timeRemaining == other.timeRemaining and
                self.shotClock == other.shotClock)


def EndBasketballState(model, pointDiff):
    # at the end of the game the only thing that matters is the point differential
    basketballState = BasketballState(pointDiff, 0, 0, 0, 0, end=True)
    state = model.findOrCreateState(basketballState)

    if pointDiff == 0: state.setReward(0)
    if pointDiff < 0:  state.setReward(-1000)
    if pointDiff > 0:  state.setReward(1000)
    
    return state


def CreateShootAction(model, curState, shotRange, pos, pointDiff, endGame, nextTime):
    global args

    action = mdp.Action('shoot')

    # get values for made shot
    if shotRange == 1: points = 2
    if shotRange == 2: points = 3
    if shotRange == 1: scoreProb = args.pt2Percent/100.
    if shotRange == 2: scoreProb = args.pt3Percent/100.

    if pos: nextPointDiff = pointDiff + points
    else:   nextPointDiff = pointDiff - points

    if abs(nextPointDiff) >= args.pointsToWin or endGame:
        madeShot = EndBasketballState(model, nextPointDiff)
    else:
        basketballState = BasketballState(nextPointDiff, 0, not pos, nextTime, min(nextTime, args.shotClock))
        madeShot = model.findOrCreateState(basketballState, maximizeReward=not pos)

    if endGame:
        missed = EndBasketballState(model, pointDiff)
        action.addTransition(curState, madeShot, scoreProb)
        action.addTransition(curState, missed, 1-scoreProb)

    else:
        # create states
        oReboundProb = (1-scoreProb) * (args.rebound / 100.)
        dReboundProb = (1-scoreProb) * (1. - args.rebound / 100.)
        oRebound = model.findOrCreateState(BasketballState(pointDiff, 1, pos, nextTime, min(nextTime, args.shotClock)), pos)
        dRebound = model.findOrCreateState(BasketballState(pointDiff, 0, not pos, nextTime, min(nextTime, args.shotClock)), not pos)

        # create transitions
        action.addTransition(curState, madeShot, scoreProb)
        action.addTransition(curState, oRebound, oReboundProb)
        action.addTransition(curState, dRebound, dReboundProb)

    curState.addAction(action)


def CreateGotoAction(model, actionName, nextShotRange, curState, pos, pointDiff, endGame, nextTime, shotClock):
    global args

    action = mdp.Action(actionName)
    nextShotClock = shotClock - args.step

    if endGame:
        endState = EndBasketballState(model, pointDiff)
        action.addTransition(curState, endState, 1)

    elif nextShotClock <= 0:
        # if shot clock expires
        basketballState = BasketballState(pointDiff, 0, not pos, nextTime, min(nextTime, args.shotClock))
        turnover = model.findOrCreateState(basketballState, maximizeReward=not pos)
        action.addTransition(curState, turnover, 1)

    else:
        basketballState = BasketballState(pointDiff, nextShotRange, pos, nextTime, nextShotClock)
        nextState = model.findOrCreateState(basketballState, maximizeReward=pos)
        action.addTransition(curState, nextState, 1)

    curState.addAction(action)


def InitializeModel():
    global args

    model = mdp.Model('Basketball', args.graph)

    for time in range(args.time, 1, -args.step):

        # determine nextTime and endGame
        nextTime = time - args.step
        endGame = nextTime <= 0

        for pos in [True, False]:
            actualShotClock = min(args.shotClock, time)
            for shotClock in range(actualShotClock, 0, -args.step):
                for pointDiff in range(-args.pointsToWin+1, args.pointsToWin):
                    for shotRange in [0, 1, 2]:
                        basketballState = BasketballState(pointDiff, shotRange, pos, time, shotClock)
                        curState = model.findOrCreateState(basketballState, maximizeReward=pos)

                        if shotRange != 0:
                            CreateShootAction(model, curState, shotRange, pos, pointDiff, endGame, nextTime)

                        CreateGotoAction(model, 'goto2pt', 1, curState, pos, pointDiff, endGame, nextTime, shotClock)
                        CreateGotoAction(model, 'goto3pt', 2, curState, pos, pointDiff, endGame, nextTime, shotClock)

    return model


def analyzeRL(model, immediateRewardsKnown):
    maxRLiterations = maxIterations * len(model.states) / (args.time / args.step)
    epsilonDecay = math.pow(0.001, 1.0/maxRLiterations)
    analyze = {'samples':100, 'simulations':200, 'results':{}}
    for rewardTest in range(50):
        start = time.time()
        analyze['sample'] = 0
        policy, stats = model.reinforcementLearn(gamma, epsilonDecay, maxRLiterations, immediateRewardsKnown=immediateRewardsKnown, analyze=analyze)
        deltaTime = time.time() - start
        print "RL test {0} took {1:.1f} sec".format(rewardTest, deltaTime)

    print "RL test results immediateRewardsKnown:{0}".format(immediateRewardsKnown)
    print json.dumps(analyze['results'], indent=2)
    rewardsType = 'known' if immediateRewardsKnown else 'unknown'
    f = open('basketball.rl.{0}.json'.format(rewardsType), "wt")
    json.dump(analyze['results'], f, indent=2)
    f.close()


def analyzeVI(model):
    analyze = {'sample':0, 'samples':100, 'simulations':200, 'results':{}}
    for rewardTest in range(50):
        analyze['sample'] = 0
        policy, stats = model.valueIteration(gamma, maxDelta, maxIterations, analyze=analyze)

    print json.dumps(analyze['results'], indent=2)
    f = open('basketball.vi.json', "wt")
    json.dump(analyze['results'], f, indent=2)
    f.close()



def solveModel(model):
    policy, stats = model.valueIteration(gamma, maxDelta, maxIterations)
    model.graphviz('basketball.vi.optimalonly.dot', utility=True, policy=policy, bestPolicy=True)
    # model.outputUtilites('basketball.vi.utilities')
    print "VI: ", stats

    policy, stats = model.policyIteration(gamma, maxIterations)
    model.graphviz('basketball.pi.optimalonly.dot', utility=True, policy=policy, bestPolicy=True, lastTransitions=False)
    model.graphviz('basketball.4level.optimal.dot', utility=True, policy=policy, bestPolicy=True, levels=4, lastTransitions=False)
    model.outputUtilites('basketball.pi.utilities')
    print "PI: ", stats

    # use enough iterations to visit same number of states as valueIteration
    maxRLiterations = maxIterations * len(model.states) / (args.time / args.step)
    epsilonDecay = math.pow(0.001, 1.0/maxRLiterations)
    policy, stats = model.reinforcementLearn(gamma, epsilonDecay, maxRLiterations, immediateRewardsKnown=False)
    model.graphviz('basketball.rlk.optimalonly.dot', utility=True, policy=policy, bestPolicy=True)
    print "RLK: ", stats

    # use enough iterations to visit same number of states as valueIteration
    policy, stats = model.reinforcementLearn(gamma, epsilonDecay, maxRLiterations, immediateRewardsKnown=True)
    model.graphviz('basketball.rlu.optimalonly.dot', utility=True, policy=policy, bestPolicy=True)
    print "RLU: ", stats


def compareRewardSimulation(model):
    policies = {}
    rewards = {}

    policies['vi'], stats = model.valueIteration(gamma, maxDelta, maxIterations)

    for rewardTest in range(50):
        policies['random'] = mdp.Policy(model.states, isRandom=True)

        maxRLiterations = maxIterations * len(model.states) / (args.time / args.step)
        epsilonDecay = math.pow(0.001, 1.0/maxRLiterations)
        policies['rlk'], stats = model.reinforcementLearn(gamma, epsilonDecay, maxRLiterations, immediateRewardsKnown=False)
        policies['rlu'], stats = model.reinforcementLearn(gamma, epsilonDecay, maxRLiterations, immediateRewardsKnown=True)

        for homeKey, homePolicy in policies.items():
            for awayKey, awayPolicy in policies.items():
                key = '{0} vs {1}'.format(homeKey, awayKey)
                if not rewards.has_key(key):
                    rewards[key] = []
                rewards[key].append(model.simulate(200, homePolicy, awayPolicy))


    print "maxRLiterations:{0}".format(maxRLiterations)
    for homeKey, homePolicy in policies.items():
        for awayKey, awayPolicy in policies.items():
            key = '{0} vs {1}'.format(homeKey, awayKey)
            print "{0} rewards: mean:{1}, std.dev:{2}".format(key, numpy.mean(rewards[key]), numpy.std(rewards[key]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Basketball MDP for deciding to shoot 2 or 3 or wait')
    parser.add_argument('--time', '-t', type=int, help='number of seconds left', default=60)
    parser.add_argument('--step', '-s', type=int, help='time step for states', default=5)
    parser.add_argument('--pointsToWin', '-p', type=int, help='point differential that we assume a win', default=5) 
    parser.add_argument('--pt2Percent', '-2', type=int, help='2pt shot percentage', default=47.0) 
    parser.add_argument('--pt3Percent', '-3', type=int, help='3pt shot percentage', default=34.4)
    parser.add_argument('--rebound', '-r', type=int, help='percent of offensive rebounds', default=31.5)
    parser.add_argument('--shotClock', type=int, help='shot clock seconds', default=35)
    parser.add_argument('--graph', action='store_true', help='print .dot file for graphviz')
    parser.add_argument('--results', help='file to print out results')
    parser.add_argument('--analyze', help='do more in-depth time-consuming analysis')

    args = parser.parse_args()
    print ' '.join(sys.argv)

    gamma = 0.99
    maxDelta = 0.001
    maxIterations = 100

    model = InitializeModel()

    model.setInitialState(BasketballState(0, 1, True, args.time, min(args.time, args.shotClock)))
    model.prune()
    print model.countItems()

    # "Tied R:2pt P:A T:45 S:30"
    # model.limitDisplay(BasketballState(0, 1, False, 10, min(10, args.shotClock)))
    if args.graph:
        model.graphviz('basketball.dot', levels=3, lastTransitions=False)

    solveModel(model)

    if args.analyze:
        analyzeRL(model, immediateRewardsKnown=True)
        analyzeRL(model, immediateRewardsKnown=False)
        analyzeVI(model)
        compareRewardSimulation(model)

