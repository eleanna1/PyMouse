import pygame
from pygame.locals import *
import numpy as np
from utils.Timer import *


class Stimulus:
    """ This class handles the stimulus presentation
    use function overrides for each stimulus class
    """

    def __init__(self, logger, params, conditions, beh=False):
        # initilize parameters
        self.params = params
        self.logger = logger
        self.conditions = conditions
        self.beh = beh
        self.isrunning = False
        self.flip_count = 0
        self.iter = []
        self.curr_cond = []
        self.rew_probe = []
        self.curr_difficulty = 1
        self.probes = np.array([d['probe'] for d in self.conditions])
        self.difficulties = [cond['difficulty'] for cond in self.conditions]
        self.timer = Timer()
        self.bias_window = 5
        self.staircase_window = 10
        self.stair_up = 0.7
        self.stair_down = 0.6

    def setup(self):
        """setup stimulation for presentation before experiment starts"""
        pass

    def prepare(self, conditions=False):
        """prepares stuff for presentation before trial starts"""
        pass

    def init(self, cond=False):
        """initialize stuff for each trial"""
        pass

    def present(self):
        """trial presentation method"""
        pass

    def stop(self):
        """stop trial"""
        pass

    def _get_new_cond(self):
        """Get curr condition & create random block of all conditions
        Should be called within init_trial
        """
        if self.params['trial_selection'] == 'block':
            if np.size(self.iter) == 0:
                self.iter = np.random.permutation(np.size(self.conditions))
            cond = self.conditions[self.iter[0]]
            self.iter = self.iter[1:]
            self.curr_cond = cond
        elif self.params['trial_selection'] == 'random':
            self.curr_cond = np.random.choice(self.conditions)
        elif self.params['trial_selection'] == 'bias':
            h = np.array(self.beh.probe_history[-self.bias_window:])
            if len(h) < self.bias_window: h = np.mean(self.probes)
            mn = np.min(self.probes); mx = np.max(self.probes)
            bias_probe = np.random.binomial(1, 1 - np.nanmean((h - mn) / (mx - mn))) * (mx - mn) + mn
            selected_conditions = [i for (i, v) in zip(self.conditions, self.probes == bias_probe) if v]
            self.curr_cond = np.random.choice(selected_conditions)
        elif self.params['trial_selection'] == 'staircase':
            h = np.array(self.beh.probe_history[-self.bias_window:])
            if len(h) < self.bias_window: h = np.mean(self.probes)
            mn = np.min(self.probes); mx = np.max(self.probes)
            bias_probe = np.random.binomial(1, 1 - np.nanmean((h - mn) / (mx - mn))) * (mx - mn) + mn
            if self.iter == 0 or np.size(self.iter) == 0:
                self.iter = self.staircase_window
                perf = np.nanmean(np.greater(self.beh.reward_history[-self.staircase_window:],0))
                if perf > self.stair_up and self.curr_difficulty < max(self.difficulties):
                    self.curr_difficulty += 1
                elif perf < self.stair_down and self.curr_difficulty > min(self.difficulties):
                    self.curr_difficulty -= 1
            self.iter -= 1
            selected_conditions = [i for (i, v) in zip(self.conditions, np.logical_and(self.probes == bias_probe,
                                                       np.array(self.difficulties) == self.curr_difficulty)) if v]
            self.curr_cond = np.random.choice(selected_conditions)

            print('Difficulty: %d' % self.curr_difficulty)
            print('Probe history')
            print(h)
            print('Iteration %d' % self.iter)
            print('Rew history')
            print(self.beh.reward_history[-self.staircase_window:])
            print('Performance %f' % np.nanmean(np.greater(self.beh.reward_history[-self.staircase_window:], 0)))
