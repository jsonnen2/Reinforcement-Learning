"""
PPO script.
Imports: numpy, torch, tyro (dataclass)
class Args-- dataclass for args
  -- I want to expose the dataclass to the command line so that the user can specify ANY arg from a command line call
class CNN-- pytorch conv net. with layer_init. get_value(). forward().
class Env-- my custom env wrapper. preprocess. run multiple envs in parallel. framestacking.
import ppo from stable baselines 3

"""
