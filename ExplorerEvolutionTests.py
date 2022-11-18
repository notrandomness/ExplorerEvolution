import unittest
from ExplorerEvolution import StateMachine
from ExplorerEvolution import State

class TestStateMachineMethods(unittest.TestCase):

    def test_getNewId_no_gap(self):
        statesDict = {}
        for i in range(5):
            statesDict[i] = State(0, 0, 0, 0, 1, i)
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.getNewId(), 5)

    def test_getNewId_with_gap(self):
        statesDict = {}
        for i in range(5):
            statesDict[i] = State(0, 0, 0, 0, 1, i)
        stateMachine = StateMachine(statesDict)
        stateMachine.removeState(3)
        self.assertEqual(stateMachine.getNewId(), 3)

    def test_removeState_valid_state_removed(self):
        statesDict = {}
        for i in range(5):
            statesDict[i] = State(0, 0, 0, 0, 1, i)
        stateMachine = StateMachine(statesDict)
        stateMachine.removeState(3)
        with self.assertRaises(KeyError):
            stateMachine.statesDict[3]
        self.assertEqual(len(stateMachine.statesDict), 4)

    def test_removeState_invalid_state(self):
        statesDict = {}
        for i in range(5):
            statesDict[i] = State(0, 0, 0, 0, 1, i)
        stateMachine = StateMachine(statesDict)
        with self.assertRaises(KeyError):
            stateMachine.removeState(5)
        self.assertEqual(len(stateMachine.statesDict), 5)

    def test_removeState_zero_state(self):
        statesDict = {}
        for i in range(5):
            statesDict[i] = State(0, 0, 0, 0, 1, i)
        stateMachine = StateMachine(statesDict)
        stateMachine.removeState(0)
        self.assertEqual(len(stateMachine.statesDict), 5)

    def test_removeCurrentState(self):
        statesDict = {}
        for i in range(5):
            statesDict[i] = State(0, 0, 0, 0, 1, i)
        stateMachine = StateMachine(statesDict)
        stateMachine.currentState = 3
        stateMachine.removeCurrentState()
        with self.assertRaises(KeyError):
            stateMachine.statesDict[3]
        self.assertEqual(len(stateMachine.statesDict), 4)

    def test_nextState_existing_nonzero(self):
        statesDict = {}
        statesDict[0] = State(2, 3, 4, 5, 1, 0)
        statesDict[1] = State(0, 3, 4, 5, 1, 1)
        statesDict[2] = State(1, 3, 4, 5, 1, 2)
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.currentState, 0)
        stateMachine.nextState()
        self.assertEqual(stateMachine.currentState, 2)
        self.assertEqual(stateMachine.statesDict[0].hitCount, 1)

    def test_nextState_nonexisting_nonzero(self):
        statesDict = {}
        statesDict[0] = State(3, 3, 4, 5, 1, 0)
        statesDict[1] = State(0, 3, 4, 5, 1, 1)
        statesDict[2] = State(1, 3, 4, 5, 1, 2)
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.currentState, 0)
        stateMachine.nextState()
        self.assertEqual(stateMachine.currentState, 0)
        self.assertEqual(stateMachine.statesDict[0].hitCount, 1)

    def test_nextState_zero(self):
        statesDict = {}
        statesDict[0] = State(0, 3, 4, 5, 1, 0)
        statesDict[1] = State(0, 3, 4, 5, 1, 1)
        statesDict[2] = State(1, 3, 4, 5, 1, 2)
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.currentState, 0)
        stateMachine.nextState()
        self.assertEqual(stateMachine.currentState, 0)
        self.assertEqual(stateMachine.statesDict[0].hitCount, 1)

    def test_nextState_with_hits_equal_to_breakAfter(self):
        statesDict = {}
        statesDict[0] = State(2, 3, 1, 1, 1, 0)
        statesDict[1] = State(0, 3, 4, 1, 1, 1)
        statesDict[2] = State(1, 3, 4, 1, 1, 2)
        statesDict[0].hitCount = 1
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.currentState, 0)
        stateMachine.nextState()
        self.assertEqual(stateMachine.currentState, 1)
        self.assertEqual(stateMachine.statesDict[0].hitCount, 0)

    def test_nextState_with_hits_greater_than_breakAfter(self):
        statesDict = {}
        statesDict[0] = State(2, 3, 1, 1, 1, 0)
        statesDict[1] = State(0, 3, 4, 1, 1, 1)
        statesDict[2] = State(1, 3, 4, 1, 1, 2)
        statesDict[0].hitCount = 2
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.currentState, 0)
        stateMachine.nextState()
        self.assertEqual(stateMachine.currentState, 1)
        self.assertEqual(stateMachine.statesDict[0].hitCount, 0)

    def test_nextState_with_nonexistent_current(self):
        statesDict = {}
        statesDict[0] = State(2, 2, 1, 10, 1, 0)
        statesDict[1] = State(1, 0, 2, 10, 3, 1)
        statesDict[2] = State(1, 3, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        stateMachine.currentState = 5
        with self.assertRaises(RuntimeError):
            stateMachine.nextState()

    def test_blockedState_existing_nonzero(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 4, 5, 1, 0)
        statesDict[1] = State(3, 0, 4, 5, 1, 1)
        statesDict[2] = State(3, 1, 4, 5, 1, 2)
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.currentState, 0)
        stateMachine.blockedState()
        self.assertEqual(stateMachine.currentState, 2)
        self.assertEqual(stateMachine.statesDict[0].hitCount, 1)

    def test_blockedState_nonexisting_nonzero(self):
        statesDict = {}
        statesDict[0] = State(3, 3, 4, 5, 1, 0)
        statesDict[1] = State(3, 0, 4, 5, 1, 1)
        statesDict[2] = State(3, 1, 4, 5, 1, 2)
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.currentState, 0)
        stateMachine.blockedState()
        self.assertEqual(stateMachine.currentState, 0)
        self.assertEqual(stateMachine.statesDict[0].hitCount, 1)

    def test_blockedState_zero(self):
        statesDict = {}
        statesDict[0] = State(3, 0, 4, 5, 1, 0)
        statesDict[1] = State(3, 0, 4, 5, 1, 1)
        statesDict[2] = State(3, 1, 4, 5, 1, 2)
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.currentState, 0)
        stateMachine.blockedState()
        self.assertEqual(stateMachine.currentState, 0)
        self.assertEqual(stateMachine.statesDict[0].hitCount, 1)

    def test_blockedState_with_hits_equal_to_breakAfter(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 1, 1, 0)
        statesDict[1] = State(3, 0, 4, 1, 1, 1)
        statesDict[2] = State(3, 1, 4, 1, 1, 2)
        statesDict[0].hitCount = 1
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.currentState, 0)
        stateMachine.blockedState()
        self.assertEqual(stateMachine.currentState, 1)
        self.assertEqual(stateMachine.statesDict[0].hitCount, 0)

    def test_blockedState_with_hits_greater_than_breakAfter(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 1, 1, 0)
        statesDict[1] = State(3, 0, 4, 1, 1, 1)
        statesDict[2] = State(3, 1, 4, 1, 1, 2)
        statesDict[0].hitCount = 2
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.currentState, 0)
        stateMachine.blockedState()
        self.assertEqual(stateMachine.currentState, 1)
        self.assertEqual(stateMachine.statesDict[0].hitCount, 0)

    def test_blockedState_with_nonexistent_current(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 1, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        stateMachine.currentState = 5
        with self.assertRaises(RuntimeError):
            stateMachine.blockedState()

    def test_replaceOrAddState_replace(self):
        statesDict = {}
        for i in range(5):
            statesDict[i] = State(0, 0, 0, 0, 1, i)
        stateMachine = StateMachine(statesDict)
        newState = State(1, 1, 1, 1, 1, 1)
        stateMachine.replaceOrAddState(newState)
        self.assertEqual(stateMachine.statesDict[1], newState)
        self.assertEqual(len(stateMachine.statesDict), 5)

    def test_replaceOrAddState_add(self):
        statesDict = {}
        for i in range(5):
            statesDict[i] = State(0, 0, 0, 0, 1, i)
        stateMachine = StateMachine(statesDict)
        newState = State(1, 1, 1, 1, 1, 5)
        stateMachine.replaceOrAddState(newState)
        self.assertEqual(stateMachine.statesDict[5], newState)
        self.assertEqual(len(stateMachine.statesDict), 6)

    def test_purgeIslands_with_unreachable_states(self):
        statesDict = {}
        #reachable
        statesDict[0] = State(2, 2, 1, 1, 1, 0)
        statesDict[1] = State(0, 0, 2, 1, 1, 1)
        statesDict[2] = State(1, 1, 0, 1, 1, 2)
        #unreachable
        statesDict[3] = State(4, 1, 0, 1, 1, 3)
        statesDict[4] = State(1, 1, 0, 1, 1, 4)
        stateMachine = StateMachine(statesDict)
        stateMachine.purgeIslands()
        self.assertEqual(len(stateMachine.statesDict), 3)
        self.assertEqual(stateMachine.statesDict[0], statesDict[0])
        self.assertEqual(stateMachine.statesDict[1], statesDict[1])
        self.assertEqual(stateMachine.statesDict[2], statesDict[2])

    def test_purgeIslands_with_no_unreachable_states(self):
        statesDict = {}
        #reachable
        statesDict[0] = State(4, 2, 1, 1, 1, 0)
        statesDict[1] = State(0, 0, 2, 1, 1, 1)
        statesDict[2] = State(1, 3, 0, 1, 1, 2)
        statesDict[3] = State(0, 1, 0, 1, 1, 3)
        statesDict[4] = State(1, 1, 0, 1, 1, 4)
        stateMachine = StateMachine(statesDict)
        stateMachine.purgeIslands()
        self.assertEqual(len(stateMachine.statesDict), 5)
        self.assertEqual(stateMachine.statesDict[0], statesDict[0])
        self.assertEqual(stateMachine.statesDict[1], statesDict[1])
        self.assertEqual(stateMachine.statesDict[2], statesDict[2])
        self.assertEqual(stateMachine.statesDict[3], statesDict[3])
        self.assertEqual(stateMachine.statesDict[4], statesDict[4])

    def test_recursiveGroom_with_unreachable_states(self):
        statesDict = {}
        #reachable
        statesDict[0] = State(2, 2, 1, 1, 1, 0)
        statesDict[1] = State(0, 0, 2, 1, 1, 1)
        statesDict[2] = State(1, 1, 0, 1, 1, 2)
        #unreachable
        statesDict[3] = State(4, 1, 0, 1, 1, 3)
        statesDict[4] = State(1, 1, 0, 1, 1, 4)
        stateMachine = StateMachine(statesDict)
        stateHitCounter = {}
        for key in statesDict.keys():
            stateHitCounter[key] = 0
        stateMachine.recursiveGroom(stateHitCounter, 0)
        self.assertEqual(stateHitCounter[0], 1)
        self.assertEqual(stateHitCounter[1], 1)
        self.assertEqual(stateHitCounter[2], 1)
        self.assertEqual(stateHitCounter[3], 0)
        self.assertEqual(stateHitCounter[4], 0)

    def test_recursiveGroom_with_no_unreachable_states(self):
        statesDict = {}
        #reachable
        statesDict[0] = State(2, 2, 1, 1, 1, 0)
        statesDict[1] = State(0, 0, 2, 1, 1, 1)
        statesDict[2] = State(1, 3, 4, 1, 1, 2)
        statesDict[3] = State(4, 1, 0, 1, 1, 3)
        statesDict[4] = State(1, 1, 0, 1, 1, 4)
        stateMachine = StateMachine(statesDict)
        stateHitCounter = {}
        for key in statesDict.keys():
            stateHitCounter[key] = 0
        stateMachine.recursiveGroom(stateHitCounter, 0)
        self.assertEqual(stateHitCounter[0], 1)
        self.assertEqual(stateHitCounter[1], 1)
        self.assertEqual(stateHitCounter[2], 1)
        self.assertEqual(stateHitCounter[3], 1)
        self.assertEqual(stateHitCounter[4], 1)

    def test_getNextValue_with_default_current(self):
        statesDict = {}
        statesDict[0] = State(2, 2, 1, 10, 1, 0)
        statesDict[1] = State(0, 0, 2, 10, 3, 1)
        statesDict[2] = State(1, 3, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.getNextValue(), 5)

    def test_getNextValue_with_specified_current(self):
        statesDict = {}
        statesDict[0] = State(2, 2, 1, 10, 1, 0)
        statesDict[1] = State(1, 0, 2, 10, 3, 1)
        statesDict[2] = State(1, 3, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        stateMachine.currentState = 1
        self.assertEqual(stateMachine.getNextValue(), 3)

    def test_getNextValue_with_nonexistent_current(self):
        statesDict = {}
        statesDict[0] = State(2, 2, 1, 10, 1, 0)
        statesDict[1] = State(1, 0, 2, 10, 3, 1)
        statesDict[2] = State(1, 3, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        stateMachine.currentState = 5
        with self.assertRaises(RuntimeError):
            stateMachine.getNextValue()

    def test_getNextValue_with_unreachable_next(self):
        statesDict = {}
        statesDict[0] = State(2, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 0, 2, 10, 3, 1)
        statesDict[2] = State(1, 3, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        stateMachine.currentState = 1
        self.assertEqual(stateMachine.getNextValue(), 1)

    def test_getBlockedValue_with_default_current(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 0, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.getBlockedValue(), 5)

    def test_getBlockedValue_with_specified_current(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 1, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        stateMachine.currentState = 1
        self.assertEqual(stateMachine.getBlockedValue(), 3)

    def test_getBlockedValue_with_nonexistent_current(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 1, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        stateMachine.currentState = 5
        with self.assertRaises(RuntimeError):
            stateMachine.getBlockedValue()

    def test_getBlockedValue_with_unreachable_next(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 3, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        stateMachine.currentState = 1
        self.assertEqual(stateMachine.getBlockedValue(), 1)

    def test_getCurrentValue_with_existing_current(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 3, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        stateMachine.currentState = 1
        self.assertEqual(stateMachine.getCurrentValue(), 3)

    def test_getCurrentValue_with_default_current(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 3, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.getCurrentValue(), 1)

    def test_getCurrentValue_with_nonexistent_current(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 3, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        stateMachine.currentState = 5
        self.assertEqual(stateMachine.getCurrentValue(), 1)

    def test_toString(self):
        statesDict = {}
        statesDict[0] = State(0, 1, 2, 3, 5, 0)
        statesDict[1] = State(0, 1, 2, 3, 5, 1)
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine.toString(), "{[down, next: 0, blocked: 1, break: 2, break after: 3, ID: 0], [down, next: 0, blocked: 1, break: 2, break after: 3, ID: 1], }")

    def test_copyMachine_members(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 3, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        stateMachine.removedStateIds.append(4)
        stateMachine2 = stateMachine.copyMachine()
        self.assertEqual(stateMachine, stateMachine2)
        self.assertEqual(stateMachine.removedStateIds, stateMachine2.removedStateIds)

    def test_copyMachine_new_object(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 3, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        stateMachine.removedStateIds.append(4)
        stateMachine2 = stateMachine.copyMachine()
        stateMachine2.removedStateIds.append(8)
        stateMachine2.statesDict[1] = State(1, 2, 3, 10, 1, 1)
        self.assertNotEqual(stateMachine, stateMachine2)
        self.assertNotEqual(stateMachine.removedStateIds, stateMachine2.removedStateIds)

    def test_resetStates(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 3, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        statesDict[1].hitCount = 5
        statesDict[2].hitCount = 7
        stateMachine = StateMachine(statesDict)
        stateMachine.resetStates()
        self.assertEqual(stateMachine.statesDict[0].hitCount, 0)
        self.assertEqual(stateMachine.statesDict[1].hitCount, 0)
        self.assertEqual(stateMachine.statesDict[2].hitCount, 0)

    def test_equals_with_equal_members(self):
        statesDict = {}
        statesDict2 = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 3, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        statesDict2[0] = State(3, 2, 1, 10, 1, 0)
        statesDict2[1] = State(3, 3, 2, 10, 3, 1)
        statesDict2[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine1 = StateMachine(statesDict)
        stateMachine2 = StateMachine(statesDict2)
        self.assertEqual(stateMachine1, stateMachine2)

    def test_equals_with_different_state_values(self):
        statesDict = {}
        statesDict2 = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 3, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        statesDict2[0] = State(3, 2, 1, 10, 1, 0)
        statesDict2[1] = State(3, 4, 2, 10, 3, 1)
        statesDict2[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine1 = StateMachine(statesDict)
        stateMachine2 = StateMachine(statesDict2)
        self.assertNotEqual(stateMachine1, stateMachine2)

    def test_equals_with_self(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 3, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine = StateMachine(statesDict)
        self.assertEqual(stateMachine, stateMachine)

    def test_hash_with_equal_members(self):
        statesDict = {}
        statesDict2 = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 3, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        statesDict2[0] = State(3, 2, 1, 10, 1, 0)
        statesDict2[1] = State(3, 3, 2, 10, 3, 1)
        statesDict2[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine1 = StateMachine(statesDict)
        stateMachine2 = StateMachine(statesDict2)
        self.assertEqual(hash(stateMachine1), hash(stateMachine2))

    def test_hash_with_self(self):
        statesDict = {}
        statesDict[0] = State(3, 2, 1, 10, 1, 0)
        statesDict[1] = State(3, 3, 2, 10, 3, 1)
        statesDict[2] = State(3, 1, 4, 10, 5, 2)
        stateMachine1 = StateMachine(statesDict)
        self.assertEqual(hash(stateMachine1), hash(stateMachine1))
    

class TestStateMethods(unittest.TestCase):

    def test_equals_with_equal_members(self):
        state1 = State(0, 1, 2, 3, 5, 0)
        state2 = State(0, 1, 2, 3, 5, 0)
        self.assertEqual(state1, state2)

    def test_equals_with_different_identifiers(self):
        state1 = State(0, 1, 2, 3, 5, 0)
        state2 = State(0, 1, 2, 3, 5, 1)
        self.assertNotEqual(state1, state2)

    def test_equals_with_self(self):
        state1 = State(0, 1, 2, 3, 5, 0)
        self.assertEqual(state1, state1)

    def test_hash_with_different_identifiers(self):
        state1 = State(0, 1, 2, 3, 5, 0)
        state2 = State(0, 1, 2, 3, 5, 1)
        self.assertNotEqual(hash(state1), hash(state2))

    def test_hash_with_equal_members(self):
        state1 = State(0, 1, 2, 3, 5, 0)
        state2 = State(0, 1, 2, 3, 5, 0)
        self.assertEqual(hash(state1), hash(state2))

    def test_hash_with_self(self):
        state1 = State(0, 1, 2, 3, 5, 0)
        self.assertEqual(hash(state1), hash(state1))

    def test_toString(self):
        state1 = State(0, 1, 2, 3, 5, 0)
        self.assertEqual(state1.toString(), "[down, next: 0, blocked: 1, break: 2, break after: 3, ID: 0]")

    def test_copyState_members(self):
        state1 = State(0, 1, 2, 3, 5, 0)
        state2 = state1.copyState()
        self.assertEqual(state1, state2)

    def test_copyState_new_object(self):
        state1 = State(0, 1, 2, 3, 5, 0)
        state2 = state1.copyState()
        state2.value = 1
        self.assertNotEqual(state1, state2)

    def test_valueDictionary_values(self):
        self.assertEqual(State.valueDictionary[1], "up")
        self.assertEqual(State.valueDictionary[2], "up-right")
        self.assertEqual(State.valueDictionary[3], "right")
        self.assertEqual(State.valueDictionary[4], "down-right")
        self.assertEqual(State.valueDictionary[5], "down")
        self.assertEqual(State.valueDictionary[6], "down-left")
        self.assertEqual(State.valueDictionary[7], "left")
        self.assertEqual(State.valueDictionary[8], "up-left")


if __name__ == '__main__':
    unittest.main()
