from haxballgym import TemplateAgent
from stable_baselines3 import A2C


class A2CBaselineAgent(TemplateAgent):

    def __init__(self, model, frames_per_action, env):
        TemplateAgent.__init__(self, frames_per_action=frames_per_action)

        self.env = env
        self.model = A2C.load(model, env=env)

    def get_numpy_action(self, state):
        action, _states = self.model.predict(state, deterministic=False)
        return [action]
