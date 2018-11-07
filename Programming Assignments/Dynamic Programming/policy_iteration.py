import numpy as np
import pprint
import sys
if "../" not in sys.path:
    sys.path.append("../")
from lib.envs.gridworld import GridworldEnv

pp = pprint.PrettyPrinter(indent=2)
env = GridworldEnv()

# Taken from policy_evaluation.py
def policy_eval(policy, env, discount_factor=1.0, theta=0.00001):
    """
    Evaluate a policy given an environment and a full description of the environment's dynamics

    Args:
        policy: [S, A] shaped matrix representing the policy
        env: OpenAI env. env.P represents the transition probabilities of the environment
            env.P[s][a] is a list of transition tuples (prob, next_state, reward, done).
            env.nS is the number of of states in the environment
            env.nA is the number of of actions in the environment
        theta: Stop evaluation once the value function change is less than theta for all states.
        discount_factor: Gamma discount factor

    Returns:
        Vector of length env.nS representing the value function
    """

    # Start with a random (all 0) value function
    V = np.zeros(env.nS)

    while True:
        old_v = V
        delta = 0
        # For each state, perform a "full backup"
        for s in range(env.nS):
            v = 0
            # Look at the possible next actions
            for a, action_prob in enumerate(policy[s]):
                # For each action, look at the possible next states
                for  prob, next_state, reward, done in env.P[s][a]:
                    # Calculate the expected value
                    v += action_prob * prob * (reward + discount_factor * V[next_state])

            # How much the value function changed
            # Max over all states
            delta = max(delta, np.abs(v - V[s]))
            V[s] = v

        # Stop evaluation once the value function change
        # is less than theta for all states
        if delta < theta:
            break

    return np.array(V)

def policy_improvement(env, policy_eval_fn=policy_eval, discount_factor=1.0):
    """
    Policy Improvement Algorithm. Iteratively evaluates and improves a policy
    until an optimal policy is found

    Args:
        env: The OpenAI environment
        policy_eval_fn: Policy Evaluation function that takes 3 arguments:
            policy, env, discount factor
        discount_factor: gamma discount factor

    Returns:
        A tuple (policy, V)
        policy is the optimal policy, a matrix of shape [S, A] where each state
        s contains a valid probability distribution over actions
        V is the value function for the optimal policy
    """

    def one_step_lookahead(state, V):
        """
        Helper function to calculate the value for all actions in a given state

        Args:
            state: The state to consider (int)
            V: The value to use as an estimator
        """
        A = np.zeros(env.nA)
        for a in range(env.nA):
            for prob, next_state, reward, done in env.P[state][a]:
                A[a] += prob * (reward + discount_factor * V[next_state])

        return A

    # Start with a random policy
    policy = np.ones([env.nS, env.nA]) / env.nA

    while True:
        # Evaluate the current policy
        V = policy_eval(policy, env)

        # Will be set to false if any changes are made to policy
        policy_stable = True

        # For each state
        for s in range(env.nS):
            # The best action taken under the current policy
            old_action = np.argmax(policy[s])

            # Find the best action by one-step lookahead
            action_values = one_step_lookahead(s, V)
            best_a = np.argmax(action_values)

            # Greedy policy improvement
            if old_action != best_a:
                policy_stable = False
            policy[s] = np.eye(env.nA)[best_a]

        # If policy is stable, then optimal policy has been found
        if policy_stable:
            return policy, V

policy, v = policy_improvement(env)
print("Policy Probability Distribution:")
print(policy)
print("")

print("Reshaped Grid Policy (0=up, 1=right, 2=down, 3=left):")
print(np.reshape(np.argmax(policy, axis=1), env.shape))
print("")

print("Value Function:")
print(v)
print("")

print("Reshaped Grid Value Function:")
print(v.reshape(env.shape))
print("")

# Test the value function
expected_v = np.array([ 0, -1, -2, -3, -1, -2, -3, -2, -2, -3, -2, -1, -3, -2, -1,  0])
np.testing.assert_array_almost_equal(v, expected_v, decimal=2)
